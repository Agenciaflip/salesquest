"""
Gerador de dados fictícios para demo do SalesQuest
"""
import random
import sys
from datetime import datetime, timedelta, date
sys.path.append('/Users/felipezanonimini/Desktop/automacoes/salesquest')

from backend.models import (
    Vendedor, AcaoDiaria, Pontuacao, Ranking, Missao, Conquista,
    criar_tabelas, get_session
)
from backend.config import Config

# 5 vendedores fictícios
VENDEDORES = [
    {
        'nome': 'Diego Santos',
        'telefone': '5511987654321',
        'email': 'diego.santos@salesquest.com',
        'avatar': '🔥',
        'nivel': 15,
        'xp_total': 2847,
    },
    {
        'nome': 'Mariana Costa',
        'telefone': '5511987654322',
        'email': 'mariana.costa@salesquest.com',
        'avatar': '⭐',
        'nivel': 12,
        'xp_total': 1923,
    },
    {
        'nome': 'Carlos Almeida',
        'telefone': '5511987654323',
        'email': 'carlos.almeida@salesquest.com',
        'avatar': '🎯',
        'nivel': 8,
        'xp_total': 876,
    },
    {
        'nome': 'Ana Paula',
        'telefone': '5511987654324',
        'email': 'ana.paula@salesquest.com',
        'avatar': '💎',
        'nivel': 5,
        'xp_total': 456,
    },
    {
        'nome': 'Rafael Souza',
        'telefone': '5511987654325',
        'email': 'rafael.souza@salesquest.com',
        'avatar': '👑',
        'nivel': 18,
        'xp_total': 4102,
    },
]

# Badges disponíveis
BADGES = {
    'First Blood': {'icon': '🩸', 'descricao': 'Primeira venda realizada', 'raridade': 'comum'},
    'Hat Trick': {'icon': '🎩', 'descricao': '3 vendas em um único dia', 'raridade': 'raro'},
    'Speed Demon': {'icon': '⚡', 'descricao': 'Conversão em menos de 24h', 'raridade': 'raro'},
    'Closer King': {'icon': '👑', 'descricao': '10 vendas em uma semana', 'raridade': 'epico'},
    'Marathon Runner': {'icon': '🏃', 'descricao': '30 dias consecutivos ativos', 'raridade': 'epico'},
    'Steady Eddie': {'icon': '🎯', 'descricao': 'Bater meta 7 dias seguidos', 'raridade': 'raro'},
    'Rising Star': {'icon': '🌟', 'descricao': 'Subir 3 níveis em 1 mês', 'raridade': 'raro'},
    'Rookie': {'icon': '🐣', 'descricao': 'Primeira semana completa', 'raridade': 'comum'},
    'Legend': {'icon': '🏆', 'descricao': 'Alcançar nível 20+', 'raridade': 'lendario'},
    'Unstoppable': {'icon': '🔥', 'descricao': '50 vendas totais', 'raridade': 'epico'},
    'Team Leader': {'icon': '👨‍💼', 'descricao': '#1 no ranking mensal', 'raridade': 'epico'},
}

def calcular_nivel_por_xp(xp):
    """Retorna nível baseado no XP"""
    for nivel_info in Config.NIVEIS:
        if nivel_info['xp_min'] <= xp <= nivel_info['xp_max']:
            return nivel_info['nivel']
    return 25  # max

def gerar_dados_diarios(vendedor_id, dias=30):
    """Gera dados diários fictícios para um vendedor"""
    session = get_session()
    data_hoje = date.today()

    # Performance base por vendedor (para variação realista)
    performance_base = {
        1: {'leads': (40, 60), 'entrevistas': (3, 5), 'conversoes': (1, 3), 'vendas': (1, 2)},  # Diego - top
        2: {'leads': (35, 50), 'entrevistas': (2, 4), 'conversoes': (1, 2), 'vendas': (0, 2)},  # Mariana - consistente
        3: {'leads': (25, 40), 'entrevistas': (1, 3), 'conversoes': (0, 2), 'vendas': (0, 1)},  # Carlos - crescendo
        4: {'leads': (20, 35), 'entrevistas': (1, 2), 'conversoes': (0, 1), 'vendas': (0, 1)},  # Ana - iniciante
        5: {'leads': (45, 65), 'entrevistas': (4, 6), 'conversoes': (2, 3), 'vendas': (1, 3)},  # Rafael - veterano
    }

    perf = performance_base.get(vendedor_id, performance_base[3])

    for i in range(dias):
        data = data_hoje - timedelta(days=dias - i - 1)

        # Gera dados aleatórios dentro do range
        leads = random.randint(*perf['leads'])
        entrevistas_agendadas = random.randint(*perf['entrevistas'])
        entrevistas_realizadas = random.randint(0, entrevistas_agendadas)
        conversoes = random.randint(*perf['conversoes'])
        vendas = random.randint(*perf['vendas'])
        ticket_medio = random.randint(3000, 15000) if vendas > 0 else 0
        faturamento = ticket_medio * vendas

        # Calcula pontos gerados
        pontos = (
            leads * Config.PONTOS['lead_alcancado'] +
            entrevistas_agendadas * Config.PONTOS['entrevista_agendada'] +
            entrevistas_realizadas * Config.PONTOS['entrevista_realizada'] +
            conversoes * Config.PONTOS['conversao'] +
            vendas * Config.PONTOS['venda']
        )

        acao = AcaoDiaria(
            vendedor_id=vendedor_id,
            data=data,
            leads_alcancados=leads,
            entrevistas_agendadas=entrevistas_agendadas,
            entrevistas_realizadas=entrevistas_realizadas,
            conversoes=conversoes,
            vendas=vendas,
            ticket_medio=ticket_medio,
            faturamento=faturamento,
            pontos_gerados=pontos
        )
        session.add(acao)

        # Registra pontuações individuais
        if leads > 0:
            session.add(Pontuacao(
                vendedor_id=vendedor_id,
                data=data,
                pontos=leads * Config.PONTOS['lead_alcancado'],
                tipo_acao='leads',
                detalhes=f'{leads} leads alcançados'
            ))

        if vendas > 0:
            session.add(Pontuacao(
                vendedor_id=vendedor_id,
                data=data,
                pontos=vendas * Config.PONTOS['venda'],
                tipo_acao='venda',
                detalhes=f'{vendas} vendas (R$ {faturamento:,.2f})'
            ))

    session.commit()
    session.close()
    print(f"  ✅ {dias} dias de dados criados para vendedor #{vendedor_id}")

def atribuir_badges(vendedor_id, nome_vendedor):
    """Atribui badges fictícios aos vendedores"""
    session = get_session()

    # Badges por vendedor (baseado no perfil)
    badges_por_vendedor = {
        'Diego Santos': ['Hat Trick', 'Speed Demon', 'Closer King', 'First Blood'],
        'Mariana Costa': ['Marathon Runner', 'Steady Eddie', 'First Blood'],
        'Carlos Almeida': ['First Blood', 'Rising Star'],
        'Ana Paula': ['Rookie', 'First Blood'],
        'Rafael Souza': ['Legend', 'Unstoppable', 'Team Leader', 'Hat Trick', 'Closer King'],
    }

    badges = badges_por_vendedor.get(nome_vendedor, ['Rookie'])

    for badge_nome in badges:
        badge_info = BADGES[badge_nome]
        conquista = Conquista(
            vendedor_id=vendedor_id,
            badge_nome=badge_nome,
            badge_icon=badge_info['icon'],
            badge_descricao=badge_info['descricao'],
            raridade=badge_info['raridade'],
            data_conquista=datetime.now() - timedelta(days=random.randint(1, 25))
        )
        session.add(conquista)

    session.commit()
    session.close()
    print(f"  ✅ {len(badges)} badges atribuídos para {nome_vendedor}")

def criar_missoes_ativas(vendedor_id):
    """Cria missões ativas para o vendedor"""
    session = get_session()

    missoes_templates = [
        {
            'titulo': 'Alcance 40 leads hoje',
            'descricao': 'Meta diária de prospecção',
            'tipo': 'diaria',
            'meta': 40,
            'progresso': random.randint(0, 35),
            'recompensa_xp': 50,
        },
        {
            'titulo': 'Realize 3 entrevistas',
            'descricao': 'Converta leads em entrevistas',
            'tipo': 'diaria',
            'meta': 3,
            'progresso': random.randint(0, 2),
            'recompensa_xp': 75,
        },
        {
            'titulo': 'Feche 5 vendas esta semana',
            'descricao': 'Objetivo semanal de vendas',
            'tipo': 'semanal',
            'meta': 5,
            'progresso': random.randint(0, 4),
            'recompensa_xp': 200,
        },
        {
            'titulo': 'Converta 3 entrevistas seguidas',
            'descricao': 'Side quest de performance',
            'tipo': 'side_quest',
            'meta': 3,
            'progresso': random.randint(0, 2),
            'recompensa_xp': 150,
        },
    ]

    for missao_data in missoes_templates:
        missao = Missao(
            vendedor_id=vendedor_id,
            titulo=missao_data['titulo'],
            descricao=missao_data['descricao'],
            tipo=missao_data['tipo'],
            meta=missao_data['meta'],
            progresso=missao_data['progresso'],
            recompensa_xp=missao_data['recompensa_xp'],
            status='ativa',
            data_inicio=date.today(),
            data_fim=date.today() + timedelta(days=1 if missao_data['tipo'] == 'diaria' else 7)
        )
        session.add(missao)

    session.commit()
    session.close()
    print(f"  ✅ {len(missoes_templates)} missões criadas para vendedor #{vendedor_id}")

def popular_banco():
    """Popula o banco com dados fictícios completos"""
    print("\n🎮 POPULANDO BANCO DE DADOS - SALESQUEST\n")

    # 1. Criar tabelas
    print("📦 Criando tabelas...")
    criar_tabelas()

    # 2. Criar vendedores
    print("\n👥 Criando vendedores...")
    session = get_session()

    for vendedor_data in VENDEDORES:
        vendedor = Vendedor(**vendedor_data)
        session.add(vendedor)
        session.commit()
        print(f"  ✅ {vendedor_data['nome']} criado (Nível {vendedor_data['nivel']}, {vendedor_data['xp_total']} XP)")

        # 3. Gerar dados diários
        print(f"\n📊 Gerando dados diários para {vendedor_data['nome']}...")
        gerar_dados_diarios(vendedor.id, dias=30)

        # 4. Atribuir badges
        print(f"\n🏆 Atribuindo badges para {vendedor_data['nome']}...")
        atribuir_badges(vendedor.id, vendedor_data['nome'])

        # 5. Criar missões
        print(f"\n🎯 Criando missões para {vendedor_data['nome']}...")
        criar_missoes_ativas(vendedor.id)

    session.close()

    print("\n✅ BANCO POPULADO COM SUCESSO!")
    print(f"📊 {len(VENDEDORES)} vendedores criados")
    print("📅 30 dias de histórico para cada vendedor")
    print("🏆 Badges distribuídos")
    print("🎯 Missões ativas criadas")
    print("\n🚀 Sistema pronto para uso!\n")

if __name__ == '__main__':
    popular_banco()
