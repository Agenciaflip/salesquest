"""
Popular banco com dados realistas - SalesQuest v2.0
15 vendedores com perfis variados + 60 dias de histórico + conversas analisadas
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
from datetime import datetime, timedelta
from backend.models import (
    Vendedor, AcaoDiaria, Pontuacao, Conquista, Missao,
    ConversaAnalisada, MetricasVendedor, ScriptVendas, EtapaScript,
    get_session, criar_tabelas
)

# Criar tabelas primeiro
criar_tabelas()

session = get_session()

# Limpar dados antigos
print("🗑️  Limpando dados antigos...")
session.query(ConversaAnalisada).delete()
session.query(MetricasVendedor).delete()
session.query(Pontuacao).delete()
session.query(AcaoDiaria).delete()
session.query(Conquista).delete()
session.query(Missao).delete()
session.query(EtapaScript).delete()
session.query(ScriptVendas).delete()
session.query(Vendedor).delete()
session.commit()

print("✅ Dados antigos removidos!")

# ================================
# VENDEDORES REALISTAS (15)
# ================================

vendedores_data = [
    # TOP PERFORMERS (120-150% da meta)
    {"nome": "Rafael Souza", "avatar": "👑", "perfil": "top", "multiplicador": 1.45},
    {"nome": "Mariana Costa", "avatar": "🔥", "perfil": "top", "multiplicador": 1.35},
    {"nome": "Diego Santos", "avatar": "⭐", "perfil": "top", "multiplicador": 1.25},

    # HIGH PERFORMERS (90-119% da meta)
    {"nome": "Ana Paula Silva", "avatar": "💎", "perfil": "high", "multiplicador": 1.15},
    {"nome": "Lucas Oliveira", "avatar": "🚀", "perfil": "high", "multiplicador": 1.10},
    {"nome": "Juliana Mendes", "avatar": "🎯", "perfil": "high", "multiplicador": 1.05},
    {"nome": "Pedro Almeida", "avatar": "⚡", "perfil": "high", "multiplicador": 0.95},

    # MID PERFORMERS (60-89% da meta)
    {"nome": "Camila Rodrigues", "avatar": "🌟", "perfil": "mid", "multiplicador": 0.85},
    {"nome": "Fernando Lima", "avatar": "📊", "perfil": "mid", "multiplicador": 0.78},
    {"nome": "Beatriz Fernandes", "avatar": "💪", "perfil": "mid", "multiplicador": 0.72},
    {"nome": "Gustavo Pereira", "avatar": "🎲", "perfil": "mid", "multiplicador": 0.68},
    {"nome": "Renata Santos", "avatar": "🏃", "perfil": "mid", "multiplicador": 0.62},

    # LOW PERFORMERS (30-59% da meta)
    {"nome": "Carlos Eduardo", "avatar": "🌱", "perfil": "low", "multiplicador": 0.55},
    {"nome": "Patricia Souza", "avatar": "📚", "perfil": "low", "multiplicador": 0.45},
    {"nome": "Roberto Silva", "avatar": "🔰", "perfil": "low", "multiplicador": 0.35},
]

print("👥 Criando 15 vendedores...")

vendedores = []
for i, vd in enumerate(vendedores_data, 1):
    telefone = f"5511{9000 + i:04d}{random.randint(1000, 9999)}"
    vendedor = Vendedor(
        nome=vd["nome"],
        telefone=telefone,
        email=f"{vd['nome'].lower().replace(' ', '.')}@salesquest.com",
        nivel=random.randint(1, 20),
        xp_total=random.randint(100, 5000),
        avatar=vd["avatar"]
    )
    session.add(vendedor)
    vendedores.append((vendedor, vd))

session.commit()
print(f"✅ {len(vendedores)} vendedores criados!")

# ================================
# HISTÓRICO DE 60 DIAS
# ================================

print("📅 Gerando histórico de 60 dias...")

# Metas base (mensais = 30 dias)
META_LEADS_DIA = 40
META_ENTREVISTAS_DIA = 3
META_CONVERSOES_MES = 15  # ~0.5 por dia
META_VENDAS_MES = 8  # ~0.27 por dia

data_inicio = datetime.now() - timedelta(days=60)

for vendedor, vd in vendedores:
    multiplicador = vd["multiplicador"]

    for dia in range(60):
        data = data_inicio + timedelta(days=dia)

        # Variação por dia da semana (segunda maior, sábado menor)
        if data.weekday() == 0:  # Segunda
            fator_dia = 1.3
        elif data.weekday() == 5:  # Sábado
            fator_dia = 0.4
        elif data.weekday() == 6:  # Domingo
            fator_dia = 0.0
        else:
            fator_dia = 1.0

        # Se domingo, pula
        if fator_dia == 0:
            continue

        # Calcular ações do dia
        leads = int(META_LEADS_DIA * multiplicador * fator_dia * random.uniform(0.8, 1.2))
        entrevistas = int(META_ENTREVISTAS_DIA * multiplicador * fator_dia * random.uniform(0.7, 1.3))
        conversoes = 1 if random.random() < (META_CONVERSOES_MES / 30 * multiplicador) else 0
        vendas = 1 if random.random() < (META_VENDAS_MES / 30 * multiplicador) else 0

        ticket = random.uniform(3000, 8000) if vendas > 0 else 0
        faturamento = vendas * ticket

        pontos = leads * 2 + entrevistas * 10 + conversoes * 30 + vendas * 50

        acao = AcaoDiaria(
            vendedor_id=vendedor.id,
            data=data.date(),
            leads_alcancados=leads,
            entrevistas_agendadas=entrevistas,
            entrevistas_realizadas=entrevistas,
            conversoes=conversoes,
            vendas=vendas,
            ticket_medio=ticket,
            faturamento=faturamento,
            pontos_gerados=pontos
        )
        session.add(acao)

session.commit()
print("✅ Histórico de 60 dias criado!")

# ================================
# MÉTRICAS DOS VENDEDORES
# ================================

print("📊 Criando métricas dos vendedores...")

for vendedor, vd in vendedores:
    multiplicador = vd["multiplicador"]

    # Calcular totais do mês
    leads_mes = int(META_LEADS_DIA * 30 * multiplicador * random.uniform(0.9, 1.1))
    entrevistas_mes = int(META_ENTREVISTAS_DIA * 30 * multiplicador * random.uniform(0.9, 1.1))
    conversoes_mes = int(META_CONVERSOES_MES * multiplicador * random.uniform(0.8, 1.2))
    vendas_mes = int(META_VENDAS_MES * multiplicador * random.uniform(0.8, 1.2))

    # Nota média de conversas (top performers têm notas maiores)
    if vd["perfil"] == "top":
        nota_media = random.uniform(8.5, 9.5)
    elif vd["perfil"] == "high":
        nota_media = random.uniform(7.5, 8.5)
    elif vd["perfil"] == "mid":
        nota_media = random.uniform(6.0, 7.5)
    else:  # low
        nota_media = random.uniform(4.5, 6.0)

    metricas = MetricasVendedor(
        vendedor_id=vendedor.id,
        meta_leads=META_LEADS_DIA * 30,
        meta_entrevistas=META_ENTREVISTAS_DIA * 30,
        meta_conversoes=META_CONVERSOES_MES,
        meta_vendas=META_VENDAS_MES,
        meta_ticket=5000.0,
        leads_mes=leads_mes,
        entrevistas_mes=entrevistas_mes,
        conversoes_mes=conversoes_mes,
        vendas_mes=vendas_mes,
        faturamento_mes=vendas_mes * random.uniform(4000, 6000),
        nota_media_conversas=nota_media,
        total_conversas_analisadas=random.randint(30, 100),
        taxa_aprovacao_script=random.uniform(0.6, 0.95),
        dias_consecutivos_meta=random.randint(0, 15),
        melhor_streak=random.randint(5, 30)
    )
    session.add(metricas)

session.commit()
print("✅ Métricas criadas!")

# ================================
# CONVERSAS ANALISADAS (MOCKADAS)
# ================================

print("💬 Criando conversas analisadas...")

conversas_exemplos = [
    {
        "transcricao": """
Vendedor: Bom dia! Tudo bem? Meu nome é {vendedor}, sou consultor da SalesQuest.

Cliente: Oi, bom dia. Tudo sim.

Vendedor: Que bom! Estou entrando em contato porque vi que você se cadastrou no nosso site. Você está procurando uma solução de gamificação para sua equipe de vendas, correto?

Cliente: Sim, exatamente. Nossa equipe está desmotivada e as metas não estão sendo batidas.

Vendedor: Entendo perfeitamente. Deixa eu te fazer uma pergunta: qual é o principal desafio que vocês enfrentam hoje com a motivação da equipe?

Cliente: Acho que é falta de visibilidade. Eles não sabem como estão performando comparado aos outros.

Vendedor: Perfeito! É exatamente isso que nossa plataforma resolve. Com o SalesQuest, cada vendedor vê em tempo real seu ranking, pontos, níveis e badges. Além disso, temos um Coach de IA que envia mensagens motivacionais personalizadas. Você gostaria de ver uma demonstração?

Cliente: Interessante! Quanto custa?

Vendedor: Nosso plano é R$ 99 por usuário/mês. Para uma equipe de 10 pessoas sairia R$ 990/mês. Considerando que você aumenta produtividade em pelo menos 20%, o ROI é garantido. Posso agendar uma demo para amanhã às 14h?

Cliente: Perfeito! Vamos agendar sim.

Vendedor: Ótimo! Vou te enviar um convite de calendário agora. Qualquer dúvida, me chama no WhatsApp. Até amanhã!
""",
        "resultado": "agendamento",
        "nota_esperada": 9.0
    },
    {
        "transcricao": """
Vendedor: Oi! Como posso ajudar?

Cliente: Queria saber mais sobre o produto.

Vendedor: Legal! A gente tem uma plataforma muito boa de gamificação.

Cliente: Quanto custa?

Vendedor: R$ 99 por usuário.

Cliente: Muito caro. Obrigado.

Vendedor: Ok, tchau.
""",
        "resultado": "perdido",
        "nota_esperada": 3.5
    },
    {
        "transcricao": """
Vendedor: Boa tarde! Aqui é {vendedor} da SalesQuest. Tudo bem?

Cliente: Boa tarde. Tudo sim, e você?

Vendedor: Ótimo, obrigado! Estou ligando porque você baixou nosso e-book sobre gamificação de vendas. Achou útil?

Cliente: Sim, muito interessante.

Vendedor: Que bom! Me conta uma coisa: na sua empresa, vocês já usam alguma ferramenta de gamificação ou tracking de performance?

Cliente: Não, hoje é tudo manual. Usamos Excel.

Vendedor: Entendo. E como está funcionando? Os vendedores conseguem ver como estão performando?

Cliente: Não muito bem, na verdade. Eu que tenho que compilar tudo e enviar relatório semanal.

Vendedor: Imagino que dá bastante trabalho, né? Nossa solução automatiza tudo isso. Você configura as metas uma vez e o sistema atualiza em tempo real. Além disso, os próprios vendedores veem o ranking ao vivo. Isso gera uma competição saudável.

Cliente: Interessante. Mas tenho receio de ser muito complexo de implementar.

Vendedor: Entendo sua preocupação! É super comum nossos clientes pensarem isso antes de começar. Mas na prática, a implementação é bem simples. Em 1 dia a gente conecta com seu CRM, sobe a plataforma e já está funcionando. Além disso, nosso suporte te ajuda em qualquer dúvida. Posso te mostrar como funciona em uma demonstração de 30 minutos?

Cliente: Pode ser. Qual seria o investimento?

Vendedor: Para 15 usuários, fica R$ 1.200/mês. Parcelamos em até 12x no cartão. Considerando que o sistema aumenta em média 30% na produtividade da equipe, você recupera o investimento rapidinho. Te mando uma proposta comercial?

Cliente: Manda sim. Vou analisar com a diretoria.

Vendedor: Perfeito! Te envio agora e te ligo na quinta-feira para alinhar. Obrigado pelo tempo!
""",
        "resultado": "interesse",
        "nota_esperada": 8.2
    }
]

for vendedor, vd in vendedores[:10]:  # Apenas primeiros 10 vendedores
    # Cada vendedor tem 3-8 conversas
    num_conversas = random.randint(3, 8)

    for _ in range(num_conversas):
        exemplo = random.choice(conversas_exemplos)
        transcricao = exemplo["transcricao"].replace("{vendedor}", vendedor.nome.split()[0])

        # Variar notas baseado no perfil
        if vd["perfil"] == "top":
            nota_base = exemplo["nota_esperada"] + random.uniform(0, 1.0)
        elif vd["perfil"] == "high":
            nota_base = exemplo["nota_esperada"] + random.uniform(-0.5, 0.5)
        elif vd["perfil"] == "mid":
            nota_base = exemplo["nota_esperada"] - random.uniform(0, 1.0)
        else:
            nota_base = exemplo["nota_esperada"] - random.uniform(0.5, 1.5)

        nota_base = max(0, min(10, nota_base))  # Limitar entre 0-10

        conversa = ConversaAnalisada(
            vendedor_id=vendedor.id,
            cliente_nome=f"Cliente {random.randint(1000, 9999)}",
            cliente_telefone=f"5511{random.randint(90000000, 99999999)}",
            tipo_conversa=random.choice(["whatsapp", "ligacao"]),
            transcricao=transcricao,
            duracao_segundos=random.randint(120, 600) if random.random() > 0.5 else None,
            data_conversa=datetime.now() - timedelta(days=random.randint(1, 30)),
            nota_geral=round(nota_base, 1),
            nota_etapas=round(nota_base + random.uniform(-0.5, 0.5), 1),
            nota_qualidade=round(nota_base + random.uniform(-0.3, 0.7), 1),
            nota_objecoes=round(nota_base + random.uniform(-1.0, 0.5), 1),
            nota_resultado=round(nota_base + random.uniform(-0.5, 1.0), 1),
            etapas_cumpridas='["saudacao", "identificacao", "descoberta", "solucao"]',
            pontos_melhoria='["Melhorar tratamento de objeções", "Ser mais assertivo no fechamento"]',
            resultado=exemplo["resultado"],
            analisado=True,
            analisado_em=datetime.now()
        )
        session.add(conversa)

session.commit()
print("✅ Conversas analisadas criadas!")

# ================================
# RESUMO FINAL
# ================================

print("\n" + "="*60)
print("🎉 BANCO POPULADO COM SUCESSO!")
print("="*60)
print(f"👥 Vendedores: {len(vendedores)}")
print(f"📅 Dias de histórico: 60")
print(f"💬 Conversas analisadas: ~{len(vendedores[:10]) * 5}")
print("\n📊 PERFIS:")
print("  🔥 Top Performers (120-150%): 3 vendedores")
print("  ⭐ High Performers (90-119%): 4 vendedores")
print("  📈 Mid Performers (60-89%): 5 vendedores")
print("  ⚠️  Low Performers (30-59%): 3 vendedores")
print("\n🌐 Acesse: http://localhost:5200")
print("="*60)
