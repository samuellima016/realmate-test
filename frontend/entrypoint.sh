#!/bin/sh
# Script de entrada para o container do frontend

# Criar arquivo .env se não existir
if [ ! -f .env ]; then
  echo "PORT=8000" > .env
  echo "REACT_APP_API_URL=${REACT_APP_API_URL:-http://localhost:80}" >> .env
fi

# Executar o comando
exec "$@"

