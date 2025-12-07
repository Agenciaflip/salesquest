"""
Teste da API de Análise de Conversas
"""
import requests
import json

API_URL = 'http://localhost:5200/api'

print("🧪 TESTANDO API DE ANÁLISE\n")
print("="*60)

# 1. Buscar vendedores
print("\n1️⃣ Buscando vendedores...")
response = requests.get(f'{API_URL}/vendedores')
vendedores = response.json()

if vendedores:
    print(f"✅ {len(vendedores)} vendedores encontrados!")
    print(f"\nPrimeiro vendedor: {vendedores[0]['nome']} (ID: {vendedores[0]['id']})")
    vendedor_id = vendedores[0]['id']
else:
    print("❌ Nenhum vendedor encontrado!")
    exit(1)

# 2. Buscar análise do vendedor
print(f"\n2️⃣ Buscando análise do vendedor ID {vendedor_id}...")
response = requests.get(f'{API_URL}/analise/vendedor/{vendedor_id}')
analise = response.json()

if analise:
    print("✅ Análise carregada com sucesso!")
    print(f"\n📊 DADOS DA ANÁLISE:")
    print(f"   Vendedor: {analise['vendedor']['nome']}")
    print(f"   Nota Média: {analise['nota_media_conversas']}/10")
    print(f"   Total Conversas: {analise['total_conversas_analisadas']}")

    if analise['performance']:
        print(f"\n📈 PERFORMANCE:")
        for key, data in analise['performance'].items():
            print(f"   {key.capitalize()}: {data['atual']}/{data['meta']} ({data['percentual']}%)")

    if analise['conversas_recentes']:
        print(f"\n💬 CONVERSAS RECENTES:")
        for conv in analise['conversas_recentes'][:3]:
            print(f"   • {conv['cliente_nome']} - Nota: {conv['nota_geral']}/10 - Resultado: {conv['resultado']}")
else:
    print("❌ Erro ao carregar análise!")
    exit(1)

print("\n" + "="*60)
print("✅ TODOS OS TESTES PASSARAM!")
print("="*60)
