#!/bin/bash

# Script de deploy SalesQuest no Cloudflare Pages
# Usar: ./deploy-cloudflare.sh

echo "🚀 Deploying SalesQuest to Cloudflare Pages..."

# Instalar Wrangler (se não tiver)
if ! command -v wrangler &> /dev/null; then
    echo "📦 Instalando Wrangler..."
    npm install -g wrangler
fi

# Login Cloudflare (primeira vez)
echo "🔐 Faça login na Cloudflare..."
wrangler login

# Deploy
echo "📤 Fazendo deploy..."
wrangler pages deploy frontend --project-name=salesquest --branch=main

echo "✅ Deploy concluído!"
echo "🌐 URL: https://salesquest.pages.dev"
