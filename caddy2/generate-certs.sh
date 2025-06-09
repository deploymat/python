#!/bin/bash
set -e

# Funkcja do wyświetlania komunikatów
echo_info() {
    echo -e "\033[1;34m[i] $1\033[0m"
}

echo_success() {
    echo -e "\033[1;32m[✓] $1\033[0m"
}

echo_error() {
    echo -e "\033[1;31m[✗] $1\033[0m" >&2
}

# Sprawdź czy skrypt jest uruchamiany jako root
if [ "$(id -u)" -eq 0 ]; then
    if [ -z "$SUDO_USER" ]; then
        echo_error "Błąd: Nie używaj bezpośrednio sudo do uruchomienia skryptu!"
        echo "Użyj: ./$(basename "$0")"
        exit 1
    fi
    # Jeśli jesteśmy tu, to znaczy że użytkownik użył sudo
    USER_HOME=$(getent passwd "$SUDO_USER" | cut -d: -f6)
else
    # Normalne wykonanie
    USER_HOME="$HOME"
fi

# Katalogi
CERTS_DIR="${USER_HOME}/.local/share/caddy-certs"
CONFIG_DIR="./config"
WORKDIR=$(pwd)

# Funkcja do sprawdzania i instalacji zależności
install_dependencies() {
    echo_info "Sprawdzanie zależności..."
    
    # Sprawdź czy mkcert jest zainstalowany
    if ! command -v mkcert &> /dev/null; then
        echo_info "Instalacja mkcert..."
        
        # Instalacja dla różnych dystrybucji
        if [ -f /etc/debian_version ]; then
            # Dla Debian/Ubuntu
            sudo apt update
            sudo apt install -y libnss3-tools
        elif [ -f /etc/redhat-release ]; then
            # Dla RHEL/CentOS
            sudo dnf install -y nss-tools
        elif [ -f /etc/arch-release ]; then
            # Dla Arch Linux
            sudo pacman -S --noconfirm nss
        fi
        
        # Pobierz i zainstaluj mkcert
        local temp_dir=$(mktemp -d)
        cd "$temp_dir"
        curl -JLO "https://dl.filippo.io/mkcert/latest?for=linux/amd64"
        chmod +x mkcert-v*-linux-amd64
        sudo mv mkcert-v*-linux-amd64 /usr/local/bin/mkcert
        cd - >/dev/null
        rm -rf "$temp_dir"
        
        # Zainstaluj lokalne CA
        mkcert -install
    fi
}

# Funkcja do tworzenia katalogów z odpowiednimi uprawnieniami
setup_directories() {
    echo_info "Konfiguracja katalogów..."
    
    # Utwórz katalogi jeśli nie istnieją
    for dir in "$CERTS_DIR" "$CONFIG_DIR"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            chmod 755 "$dir"
        fi
        
        # Sprawdź uprawnienia
        if [ ! -w "$dir" ]; then
            echo_info "Brak uprawnień do zapisu w $dir. Próba z sudo..."
            sudo mkdir -p "$dir"
            sudo chown -R $USER:$USER "$dir"
            sudo chmod 755 "$dir"
        fi
    done
}

# Funkcja do generowania certyfikatów
generate_certificates() {
    echo_info "Generowanie certyfikatów..."
    
    # Załaduj zmienne środowiskowe
    if [ -f .env ]; then
        export $(grep -v '^#' .env | xargs)
    else
        echo_error "Brak pliku .env"
        exit 1
    fi
    
    # Przygotuj listę domen
    local domains=("$DOMAIN" "*.$DOMAIN" "localhost" "127.0.0.1" "::1")
    
    # Dodaj subdomeny z .env jeśli istnieją
    for sub in "$API_SUBDOMAIN" "$WEB_SUBDOMAIN" "$AUTH_SUBDOMAIN"; do
        if [ -n "$sub" ]; then
            domains+=("$sub.$DOMAIN")
        fi
    done
    
    # Usuń duplikaty
    local unique_domains=$(printf "%s\n" "${domains[@]}" | sort -u | tr '\n' ' ')
    
    echo "Domeny: ${unique_domains}"
    
    # Generuj certyfikaty w katalogu tymczasowym
    local temp_dir=$(mktemp -d)
    
    # Generuj certyfikaty
    if ! mkcert -cert-file "$temp_dir/localhost.crt" \
                -key-file "$temp_dir/localhost.key" \
                ${unique_domains[@]}; then
        echo_error "Błąd podczas generowania certyfikatów"
        rm -rf "$temp_dir"
        exit 1
    fi
    
    # Skopiuj certyfikaty do docelowego katalogu
    cp "$temp_dir/"* "$CERTS_DIR/"
    chmod 644 "$CERTS_DIR/"*
    
    # Posprzątaj
    rm -rf "$temp_dir"
    
    echo_success "Certyfikaty wygenerowane w $CERTS_DIR"
}

# Funkcja do generowania konfiguracji Caddy
generate_caddy_config() {
    echo_info "Generowanie konfiguracji Caddy..."
    
    local caddyfile="$CONFIG_DIR/Caddyfile"
    
    cat > "$caddyfile" <<EOL
{
    auto_https disable_redirects
    debug
    tls /etc/caddy/certs/localhost.crt /etc/caddy/certs/localhost.key
}

:80 {
    redir https://{host}{uri} permanent
}

:443 {
    log {
        output stderr
        format console
        level INFO
    }
    
    # Strona główna
    handle / {
        respond "Witaj w lokalnym środowisku deweloperskim!"
    }
EOL

    # Dodaj konfigurację dla każdej subdomeny
    for service in "api" "web" "auth"; do
        local var_name="${service}_SUBDOMAIN"
        local subdomain="${!var_name}"
        
        if [ -n "$subdomain" ]; then
            local service_name=$(echo "$service" | tr '[:lower:]' '[:upper:]')
            
            cat >> "$caddyfile" <<EOL

    # $service_name service
    @$service host $subdomain.$DOMAIN
    handle @$service {
        reverse_proxy $service:80 {
            header_up Host {host}
            header_up X-Real-IP {remote}
            header_up X-Forwarded-Proto https
        }
    }
EOL
        fi
    done
    
    echo "}" >> "$caddyfile"
    
    # Skopiuj Caddyfile do głównego katalogu
    cp "$caddyfile" "$WORKDIR/"
    
    echo_success "Konfiguracja Caddy wygenerowana"
}

# Funkcja do aktualizacji docker-compose.yml
update_docker_compose() {
    local docker_compose="$WORKDIR/docker-compose.yml"
    
    if [ -f "$docker_compose" ]; then
        echo_info "Aktualizacja docker-compose.yml..."
        
        # Utwórz kopię zapasową
        cp "$docker_compose" "${docker_compose}.bak"
        
        # Zaktualizuj ścieżkę do certyfikatów
        sed -i -E "s|\\./certs|$CERTS_DIR|g" "$docker_compose"
        
        echo_success "Zaktualizowano docker-compose.yml"
    fi
}

# Główna funkcja
main() {
    echo "=== Generator certyfikatów dla Caddy ==="
    
    # Sprawdź czy mkcert jest zainstalowany i zainstaluj jeśli potrzeba
    install_dependencies
    
    # Przygotuj katalogi
    setup_directories
    
    # Wygeneruj certyfikaty
    generate_certificates
    
    # Wygeneruj konfigurację Caddy
    generate_caddy_config
    
    # Zaktualizuj docker-compose.yml
    update_docker_compose
    
    # Podsumowanie
    echo -e "\n\033[1;32m=== Konfiguracja zakończona pomyślnie ===\033[0m"
    echo -e "Certyfikaty: \033[1;34m$CERTS_DIR\033[0m"
    echo -e "Konfiguracja Caddy: \033[1;34m$CONFIG_DIR/Caddyfile\033[0m"
    
    echo -e "\n\033[1;33mAby zastosować zmiany, uruchom:\033[0m"
    if [ "$(id -u)" -eq 0 ]; then
        echo "  su $SUDO_USER -c 'cd $WORKDIR && make down && make up'"
    else
        echo "  cd $WORKDIR && make down && make up"
    fi
    
    echo -e "\n\033[1;33mDostępne adresy:\033[0m"
    for sub in "$API_SUBDOMAIN" "$WEB_SUBDOMAIN" "$AUTH_SUBDOMAIN"; do
        if [ -n "$sub" ]; then
            echo "  - https://$sub.$DOMAIN"
        fi
    done
}

# Uruchom główną funkcję
main "$@"
