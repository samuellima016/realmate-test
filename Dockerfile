# ==============================
#  Dockerfile - Realmate Challenge
#  Samuel Lima - versão final estável
# ==============================

FROM python:3.13-slim

# Define diretório de trabalho
WORKDIR /app

# Instala dependências de sistema
RUN apt-get update && apt-get install -y curl build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

# Instala Poetry globalmente
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Copia arquivos do Poetry primeiro (para cache)
COPY pyproject.toml poetry.lock ./

# Instala dependências do projeto (sem reinstalar Poetry)
RUN poetry install --no-root --no-interaction --no-ansi

# Copia o restante do código
COPY . .

# Expõe porta padrão do Django
EXPOSE 80

# Comando padrão: aplica migrações e inicia o servidor
CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:80"]
