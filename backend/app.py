"""
SalesQuest - Plataforma de Gamificação Comercial
API Flask Principal
"""
import sys
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from datetime import date
sys.path.append('/Users/felipezanonimini/Desktop/automacoes/salesquest')

from backend.config import Config
from backend.models import get_session, Vendedor, AcaoDiaria, Missao, Conquista
from backend.services.gamification import GamificationService
from backend.services.ai_agent import CoachAI
from backend.services.whatsapp import WhatsAppService
from backend.services.conversation_analyzer import get_nota_media_vendedor, get_conversas_recentes

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)
app.config.from_object(Config)

# Instâncias dos serviços
gamification = GamificationService()
coach = CoachAI()
whatsapp = WhatsAppService()

# ================================
# ROTAS FRONTEND
# ================================

@app.route('/')
def index():
    """Página inicial"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_files(path):
    """Arquivos estáticos"""
    return send_from_directory(app.static_folder, path)

# ================================
# API - VENDEDORES
# ================================

@app.route('/api/vendedores', methods=['GET'])
def listar_vendedores():
    """Lista todos os vendedores"""
    session = get_session()
    vendedores = session.query(Vendedor).filter_by(ativo=True).all()

    resultado = []
    for v in vendedores:
        # Busca nível info
        nivel_info = next(
            (n for n in Config.NIVEIS if n['nivel'] == v.nivel),
            {'nome': 'Unknown', 'xp_min': 0, 'xp_max': 0}
        )

        resultado.append({
            'id': v.id,
            'nome': v.nome,
            'telefone': v.telefone,
            'nivel': v.nivel,
            'nivel_nome': nivel_info['nome'],
            'xp_total': v.xp_total,
            'xp_min': nivel_info['xp_min'],
            'xp_max': nivel_info['xp_max'],
            'avatar': v.avatar,
        })

    session.close()
    return jsonify(resultado)

@app.route('/api/vendedores/<int:vendedor_id>', methods=['GET'])
def get_vendedor(vendedor_id):
    """Retorna detalhes de um vendedor"""
    stats = gamification.get_stats_vendedor(vendedor_id, periodo='mes')

    if not stats:
        return jsonify({'erro': 'Vendedor não encontrado'}), 404

    # Busca missões ativas
    session = get_session()
    missoes = session.query(Missao).filter_by(
        vendedor_id=vendedor_id,
        status='ativa'
    ).all()

    missoes_data = [{
        'id': m.id,
        'titulo': m.titulo,
        'descricao': m.descricao,
        'tipo': m.tipo,
        'meta': m.meta,
        'progresso': m.progresso,
        'percentual': (m.progresso / m.meta * 100) if m.meta > 0 else 0,
        'recompensa_xp': m.recompensa_xp,
    } for m in missoes]

    # Busca badges
    badges = session.query(Conquista).filter_by(vendedor_id=vendedor_id).all()

    badges_data = [{
        'nome': b.badge_nome,
        'icon': b.badge_icon,
        'descricao': b.badge_descricao,
        'raridade': b.raridade,
        'data_conquista': b.data_conquista.isoformat(),
    } for b in badges]

    session.close()

    return jsonify({
        **stats,
        'missoes': missoes_data,
        'badges_list': badges_data,
    })

# ================================
# API - RANKING
# ================================

@app.route('/api/ranking', methods=['GET'])
def get_ranking():
    """Retorna ranking dos vendedores"""
    periodo = request.args.get('periodo', 'dia')  # dia, semana, mes

    ranking = gamification.calcular_ranking(periodo)

    return jsonify({
        'periodo': periodo,
        'ranking': ranking
    })

# ================================
# API - AÇÕES (Registrar atividade)
# ================================

@app.route('/api/acoes/registrar', methods=['POST'])
def registrar_acao():
    """
    Registra uma ação do vendedor

    Body:
    {
        "vendedor_id": 1,
        "tipo_acao": "lead_alcancado",
        "quantidade": 5,
        "detalhes": {"meta_atingida": false}
    }
    """
    data = request.json

    vendedor_id = data.get('vendedor_id')
    tipo_acao = data.get('tipo_acao')
    quantidade = data.get('quantidade', 1)
    detalhes = data.get('detalhes', {})

    if not vendedor_id or not tipo_acao:
        return jsonify({'erro': 'vendedor_id e tipo_acao são obrigatórios'}), 400

    # Registra ação
    resultado = gamification.registrar_acao(vendedor_id, tipo_acao, quantidade, detalhes)

    # Atualiza progresso de missões
    missoes_concluidas = gamification.atualizar_progresso_missao(vendedor_id, tipo_acao, quantidade)

    # Gera feedback do coach
    mensagem_coach = coach.gerar_feedback_imediato(
        vendedor_id,
        tipo_acao,
        resultado['pontos_ganhos'],
        resultado['nivel_info']
    )

    return jsonify({
        **resultado,
        'missoes_concluidas': missoes_concluidas,
        'mensagem_coach': mensagem_coach,
    })

# ================================
# API - COACH (Mensagens)
# ================================

@app.route('/api/coach/motivacao/<int:vendedor_id>', methods=['GET'])
def get_motivacao(vendedor_id):
    """Gera mensagem motivacional para o vendedor"""
    mensagem = coach.gerar_mensagem_motivacional_matinal(vendedor_id)

    if not mensagem:
        return jsonify({'erro': 'Vendedor não encontrado'}), 404

    return jsonify({'mensagem': mensagem})

@app.route('/api/coach/alerta/<int:vendedor_id>', methods=['GET'])
def get_alerta(vendedor_id):
    """Gera alerta de performance"""
    mensagem = coach.gerar_alerta_performance(vendedor_id)

    if not mensagem:
        return jsonify({'mensagem': 'Performance OK, nenhum alerta necessário'})

    return jsonify({'mensagem': mensagem})

@app.route('/api/coach/provocacao/<int:vendedor_id>', methods=['GET'])
def get_provocacao(vendedor_id):
    """Gera provocação baseada no ranking"""
    mensagem = coach.gerar_provocacao_ranking(vendedor_id)

    if not mensagem:
        return jsonify({'mensagem': 'Não há provocação disponível'})

    return jsonify({'mensagem': mensagem})

@app.route('/api/coach/relatorio/<int:vendedor_id>', methods=['GET'])
def get_relatorio(vendedor_id):
    """Gera relatório noturno"""
    mensagem = coach.gerar_relatorio_noturno(vendedor_id)

    if not mensagem:
        return jsonify({'erro': 'Vendedor não encontrado'}), 404

    return jsonify({'mensagem': mensagem})

# ================================
# API - WHATSAPP
# ================================

@app.route('/api/whatsapp/enviar', methods=['POST'])
def enviar_whatsapp():
    """
    Envia mensagem WhatsApp para um vendedor

    Body:
    {
        "vendedor_id": 1,
        "mensagem": "Teste"
    }
    """
    data = request.json

    vendedor_id = data.get('vendedor_id')
    mensagem = data.get('mensagem')

    if not vendedor_id or not mensagem:
        return jsonify({'erro': 'vendedor_id e mensagem são obrigatórios'}), 400

    resultado = whatsapp.enviar_para_vendedor(vendedor_id, mensagem)

    return jsonify(resultado)

@app.route('/api/whatsapp/processar-pendentes', methods=['POST'])
def processar_pendentes():
    """Processa e envia todas as mensagens pendentes"""
    resultado = whatsapp.enviar_mensagens_pendentes()

    return jsonify(resultado)

# ================================
# API - STATS
# ================================

@app.route('/api/stats/geral', methods=['GET'])
def stats_geral():
    """Retorna estatísticas gerais da plataforma"""
    session = get_session()

    total_vendedores = session.query(Vendedor).filter_by(ativo=True).count()

    # Soma de ações hoje
    hoje = date.today()
    acoes_hoje = session.query(AcaoDiaria).filter_by(data=hoje).all()

    total_leads_hoje = sum(a.leads_alcancados for a in acoes_hoje)
    total_entrevistas_hoje = sum(a.entrevistas_realizadas for a in acoes_hoje)
    total_vendas_hoje = sum(a.vendas for a in acoes_hoje)
    total_faturamento_hoje = sum(a.faturamento for a in acoes_hoje)

    session.close()

    return jsonify({
        'total_vendedores': total_vendedores,
        'hoje': {
            'leads': total_leads_hoje,
            'entrevistas': total_entrevistas_hoje,
            'vendas': total_vendas_hoje,
            'faturamento': total_faturamento_hoje,
        }
    })

# ================================
# API - ANÁLISE DE CONVERSAS
# ================================

@app.route('/api/analise/vendedor/<int:vendedor_id>', methods=['GET'])
def get_analise_vendedor(vendedor_id):
    """
    Retorna análise completa de conversas do vendedor
    """
    session = get_session()

    # Busca vendedor
    vendedor = session.query(Vendedor).get(vendedor_id)
    if not vendedor:
        return jsonify({'erro': 'Vendedor não encontrado'}), 404

    # Busca métricas
    from backend.models import MetricasVendedor
    metricas = session.query(MetricasVendedor).filter_by(vendedor_id=vendedor_id).first()

    # Nota média de conversas
    nota_media = get_nota_media_vendedor(vendedor_id)

    # Últimas conversas
    conversas = get_conversas_recentes(vendedor_id, limit=10)

    conversas_data = [{
        'id': c.id,
        'cliente_nome': c.cliente_nome,
        'tipo_conversa': c.tipo_conversa,
        'nota_geral': c.nota_geral,
        'nota_etapas': c.nota_etapas,
        'nota_qualidade': c.nota_qualidade,
        'nota_objecoes': c.nota_objecoes,
        'nota_resultado': c.nota_resultado,
        'resultado': c.resultado,
        'data_conversa': c.data_conversa.isoformat(),
        'duracao_segundos': c.duracao_segundos,
    } for c in conversas]

    # Performance vs meta
    performance = {}
    if metricas:
        performance = {
            'leads': {
                'meta': metricas.meta_leads,
                'atual': metricas.leads_mes,
                'percentual': round((metricas.leads_mes / metricas.meta_leads * 100), 1) if metricas.meta_leads > 0 else 0
            },
            'entrevistas': {
                'meta': metricas.meta_entrevistas,
                'atual': metricas.entrevistas_mes,
                'percentual': round((metricas.entrevistas_mes / metricas.meta_entrevistas * 100), 1) if metricas.meta_entrevistas > 0 else 0
            },
            'conversoes': {
                'meta': metricas.meta_conversoes,
                'atual': metricas.conversoes_mes,
                'percentual': round((metricas.conversoes_mes / metricas.meta_conversoes * 100), 1) if metricas.meta_conversoes > 0 else 0
            },
            'vendas': {
                'meta': metricas.meta_vendas,
                'atual': metricas.vendas_mes,
                'percentual': round((metricas.vendas_mes / metricas.meta_vendas * 100), 1) if metricas.meta_vendas > 0 else 0
            },
        }

    session.close()

    return jsonify({
        'vendedor': {
            'id': vendedor.id,
            'nome': vendedor.nome,
            'avatar': vendedor.avatar,
            'nivel': vendedor.nivel,
        },
        'nota_media_conversas': nota_media,
        'total_conversas_analisadas': len(conversas),
        'performance': performance,
        'conversas_recentes': conversas_data,
    })

# ================================
# ROTA TESTE
# ================================

@app.route('/api/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'status': 'online',
        'plataforma': 'SalesQuest',
        'versao': '2.0.0'
    })

# ================================
# MAIN
# ================================

if __name__ == '__main__':
    print("\n🎮 SALESQUEST - Plataforma de Gamificação Comercial")
    print(f"🌐 Servidor: http://{Config.HOST}:{Config.PORT}")
    print(f"📊 Dashboard: http://{Config.HOST}:{Config.PORT}")
    print(f"🤖 API Docs: http://{Config.HOST}:{Config.PORT}/api/health\n")

    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
