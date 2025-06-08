#!/bin/bash

echo "🔐 Przekierowuję do Cloudflare w celu zalogowania i utworzenia API Tokenu..."
sleep 1

# URL do stworzenia API tokenu z predefiniowanymi uprawnieniami
CREATE_TOKEN_URL="https://dash.cloudflare.com/profile/api-tokens"

# Otwórz stronę w przeglądarce domyślnej
if command -v xdg-open &>/dev/null; then
  xdg-open "$CREATE_TOKEN_URL"
elif command -v open &>/dev/null; then
  open "$CREATE_TOKEN_URL"
else
  echo "⚠️ Nie wykryto domyślnej przeglądarki. Otwórz ręcznie:"
  echo "$CREATE_TOKEN_URL"
fi

echo ""
echo "📌 Po zalogowaniu kliknij: ➕ 'Create Token'"
echo "Wybierz: 'Use Template' → 'Edit zone DNS'"
echo ""
echo "Ustaw zakres (Zone Resources):"
echo "→ Include → Specific zone → wybierz swoją domenę"
echo ""
echo "🔑 Po wygenerowaniu tokenu, dodaj go do pliku .env jako:"
echo "CF_API_TOKEN=twój_token_tutaj"

curl "https://api.cloudflare.com/client/v4/user/tokens/verify" \
     -H "Authorization: Bearer ${CF_API_TOKEN}"