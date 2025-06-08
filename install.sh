#!/bin/bash

# PyDock Installation Script
# Installs PyDock - Python Docker Deployment Manager

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_header() {
    echo -e "\n${CYAN}${1}${NC}"
    echo "=================================="
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_warning "Running as root. Consider using a virtual environment."
    fi
}

# Check Python version
check_python() {
    log_info "Checking Python version..."

    if command -v python3 &> /dev/null; then
        python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        log_info "Found Python $python_version"

        # Check if version is >= 3.8
        if python3 -c 'import sys; exit(0 if sys.version_info >= (3, 8) else 1)'; then
            log_success "Python version is compatible"
        else
            log_error "Python 3.8 or higher is required"
            exit 1
        fi
    else
        log_error "Python 3 not found. Please install Python 3.8 or higher."
        exit 1
    fi
}

# Check if pip is available
check_pip() {
    log_info "Checking pip..."

    if command -v pip3 &> /dev/null; then
        log_success "pip3 found"
        PIP_CMD="pip3"
    elif command -v pip &> /dev/null; then
        log_success "pip found"
        PIP_CMD="pip"
    else
        log_error "pip not found. Please install pip."
        exit 1
    fi
}

# Install PyDock from PyPI
install_from_pypi() {
    log_info "Installing PyDock from PyPI..."

    $PIP_CMD install pydock

    if command -v pydock &> /dev/null; then
        log_success "PyDock installed successfully!"
        pydock --help
    else
        log_error "Installation failed. PyDock command not found."
        exit 1
    fi
}

# Install PyDock from source
install_from_source() {
    log_info "Installing PyDock from source..."

    # Check if git is available
    if ! command -v git &> /dev/null; then
        log_error "Git is required to install from source"
        exit 1
    fi

    # Clone repository
    TEMP_DIR=$(mktemp -d)
    log_info "Cloning PyDock repository to $TEMP_DIR..."

    git clone https://github.com/pydock/pydock.git "$TEMP_DIR/pydock"
    cd "$TEMP_DIR/pydock"

    # Install in development mode
    log_info "Installing PyDock in development mode..."
    $PIP_CMD install -e .

    if command -v pydock &> /dev/null; then
        log_success "PyDock installed successfully from source!"
        pydock --help
    else
        log_error "Installation failed. PyDock command not found."
        exit 1
    fi

    # Cleanup
    cd - > /dev/null
    rm -rf "$TEMP_DIR"
}

# Create virtual environment
create_venv() {
    log_info "Creating Python virtual environment..."

    if [[ ! -d "pydock-venv" ]]; then
        python3 -m venv pydock-venv
        log_success "Virtual environment created: pydock-venv"
    else
        log_info "Virtual environment already exists"
    fi

    # Activate virtual environment
    source pydock-venv/bin/activate
    log_success "Virtual environment activated"

    # Upgrade pip
    pip install --upgrade pip
}

# Install system dependencies
install_system_deps() {
    log_info "Installing system dependencies..."

    if command -v apt-get &> /dev/null; then
        # Debian/Ubuntu
        sudo apt-get update
        sudo apt-get install -y python3-pip python3-venv git openssh-client
        log_success "System dependencies installed (Debian/Ubuntu)"
    elif command -v yum &> /dev/null; then
        # CentOS/RHEL
        sudo yum install -y python3-pip python3-venv git openssh-clients
        log_success "System dependencies installed (CentOS/RHEL)"
    elif command -v brew &> /dev/null; then
        # macOS
        brew install python git
        log_success "System dependencies installed (macOS)"
    else
        log_warning "Unknown package manager. Please install Python 3.8+, pip, git manually."
    fi
}

# Setup completion
setup_completion() {
    log_info "Setting up command completion..."

    # For bash
    if [[ $SHELL == *"bash"* ]]; then
        # Add completion to .bashrc if not already present
        if ! grep -q "pydock completion" ~/.bashrc 2>/dev/null; then
            echo '# PyDock completion' >> ~/.bashrc
            echo 'eval "$(_PYDOCK_COMPLETE=bash_source pydock)"' >> ~/.bashrc
            log_success "Bash completion configured"
        fi
    fi

    # For zsh
    if [[ $SHELL == *"zsh"* ]]; then
        if ! grep -q "pydock completion" ~/.zshrc 2>/dev/null; then
            echo '# PyDock completion' >> ~/.zshrc
            echo 'eval "$(_PYDOCK_COMPLETE=zsh_source pydock)"' >> ~/.zshrc
            log_success "Zsh completion configured"
        fi
    fi
}

# Create example project
create_example() {
    log_info "Creating example project..."

    mkdir -p pydock-example
    cd pydock-example

    # Create example configuration
    cat > pydock.json << 'EOF'
{
  "domain": "example.com",
  "vps_ip": "192.168.1.100",
  "ssh_key_path": "~/.ssh/id_rsa",
  "services": {
    "web-app": {
      "subdomain": "app",
      "port": 5000,
      "build_path": "./web-app"
    },
    "static-site": {
      "subdomain": "site",
      "port": 80,
      "image": "nginx:alpine"
    }
  }
}
EOF

    # Generate sample applications
    pydock generate app
    pydock generate static

    cd ..
    log_success "Example project created in: pydock-example/"
}

# Show next steps
show_next_steps() {
    log_header "🎉 Installation Complete!"

    echo "PyDock has been successfully installed!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Initialize a new project:    pydock init mydomain.com 192.168.1.100"
    echo "2. Generate sample app:         pydock generate app"
    echo "3. Deploy to VPS:              pydock deploy"
    echo "4. Check status:               pydock status"
    echo ""
    echo "📖 Documentation: https://github.com/pydock/pydock"
    echo "🐛 Issues:        https://github.com/pydock/pydock/issues"
    echo ""
    echo "🚀 Happy deploying with PyDock!"
}

# Main installation function
main() {
    log_header "🐳 PyDock Installation"

    echo "PyDock - Python Docker Deployment Manager"
    echo "This script will install PyDock on your system."
    echo ""

    # Parse command line arguments
    INSTALL_METHOD="pypi"
    USE_VENV=false
    INSTALL_DEPS=false
    CREATE_EXAMPLE=false

    while [[ $# -gt 0 ]]; do
        case $1 in
            --source)
                INSTALL_METHOD="source"
                shift
                ;;
            --venv)
                USE_VENV=true
                shift
                ;;
            --deps)
                INSTALL_DEPS=true
                shift
                ;;
            --example)
                CREATE_EXAMPLE=true
                shift
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --source     Install from source (GitHub)"
                echo "  --venv       Create and use virtual environment"
                echo "  --deps       Install system dependencies"
                echo "  --example    Create example project"
                echo "  --help       Show this help"
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done

    # Installation steps
    check_root

    if [[ "$INSTALL_DEPS" == true ]]; then
        install_system_deps
    fi

    check_python
    check_pip

    if [[ "$USE_VENV" == true ]]; then
        create_venv
    fi

    if [[ "$INSTALL_METHOD" == "source" ]]; then
        install_from_source
    else
        install_from_pypi
    fi

    setup_completion

    if [[ "$CREATE_EXAMPLE" == true ]]; then
        create_example
    fi

    show_next_steps
}

# Run main function with all arguments
main "$@"