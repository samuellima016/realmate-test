FROM node:18-alpine

WORKDIR /app

# Instalar dependências do sistema
RUN apk add --no-cache bash

# Copiar arquivos de dependências
COPY package*.json ./

# Instalar dependências
RUN npm install

# Copiar código fonte
COPY . .

# Copiar e tornar executável o script de entrada
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expor porta 8000
EXPOSE 8000

# Variável de ambiente para a porta
ENV PORT=8000

# Script de entrada
ENTRYPOINT ["/entrypoint.sh"]

# Comando para iniciar o servidor
CMD ["npm", "start"]

