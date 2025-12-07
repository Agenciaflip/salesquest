"""
Serviço de Gamificação - Lógica de pontos, níveis, rankings
"""
import sys
from datetime import date, timedelta
from sqlalchemy import func, desc
sys.path.append('/Users/felipezanonimini/Desktop/automacoes/salesquest')

from backend.models import (
    Vendedor, AcaoDiaria, Pontuacao, Ranking, Missao, Conquista,
    get_session
)
from backend.config import Config

class GamificationService:
    """Serviço de gamificação"""

    @staticmethod
    def calcular_pontos_acao(tipo_acao, quantidade, detalhes=None):
        """
        Calcula pontos de uma ação com multiplicadores

        Args:
            tipo_acao: lead, entrevista_agendada, entrevista_realizada, conversao, venda
            quantidade: número de ações
            detalhes: dict com informações extras (ticket, meta_atingida, etc)
        """
        pontos_base = Config.PONTOS.get(tipo_acao, 0) * quantidade
        multiplicador = 1.0

        if detalhes:
            # Bonus meta diária
            if detalhes.get('meta_atingida'):
                multiplicador *= Config.PONTOS['bonus_meta_diaria']

            # Bonus mesmo dia (entrevista agendada e realizada no mesmo dia)
            if detalhes.get('mesmo_dia'):
                multiplicador *= Config.PONTOS['bonus_mesmo_dia']

            # Bonus conversão
            if tipo_acao == 'entrevista_realizada' and detalhes.get('converteu'):
                multiplicador *= Config.PONTOS['bonus_conversao']

            # Bonus ticket alto
            if tipo_acao == 'venda':
                ticket = detalhes.get('ticket', 0)
                if ticket > 5000:
                    multiplicador *= Config.PONTOS['bonus_ticket_alto']

                # Bonus por cada R$1000
                bonus_ticket = int(ticket / 1000) * Config.PONTOS['bonus_ticket_por_mil']
                multiplicador += bonus_ticket

        pontos_final = int(pontos_base * multiplicador)
        return pontos_final

    @staticmethod
    def atualizar_nivel_vendedor(vendedor_id):
        """Atualiza nível do vendedor baseado no XP total"""
        session = get_session()
        vendedor = session.query(Vendedor).filter_by(id=vendedor_id).first()

        if not vendedor:
            session.close()
            return None

        # Busca nível correto baseado no XP
        for nivel_info in Config.NIVEIS:
            if nivel_info['xp_min'] <= vendedor.xp_total <= nivel_info['xp_max']:
                nivel_anterior = vendedor.nivel
                vendedor.nivel = nivel_info['nivel']

                # Se subiu de nível, verifica badges
                if vendedor.nivel > nivel_anterior:
                    GamificationService._verificar_badge_nivel(vendedor_id, vendedor.nivel)

                session.commit()
                session.close()
                return {
                    'nivel': vendedor.nivel,
                    'nome_nivel': nivel_info['nome'],
                    'subiu': vendedor.nivel > nivel_anterior
                }

        session.close()
        return None

    @staticmethod
    def _verificar_badge_nivel(vendedor_id, nivel):
        """Verifica e concede badges por alcançar níveis"""
        session = get_session()

        badges_nivel = {
            5: ('Prospector Completo', '🎖️', 'Completou todos os níveis Prospector'),
            10: ('Hunter Completo', '🏹', 'Completou todos os níveis Hunter'),
            15: ('Closer Completo', '🎯', 'Completou todos os níveis Closer'),
            20: ('Master Completo', '👑', 'Completou todos os níveis Master'),
        }

        if nivel in badges_nivel:
            badge_nome, badge_icon, badge_desc = badges_nivel[nivel]

            # Verifica se já tem o badge
            existe = session.query(Conquista).filter_by(
                vendedor_id=vendedor_id,
                badge_nome=badge_nome
            ).first()

            if not existe:
                conquista = Conquista(
                    vendedor_id=vendedor_id,
                    badge_nome=badge_nome,
                    badge_icon=badge_icon,
                    badge_descricao=badge_desc,
                    raridade='epico'
                )
                session.add(conquista)
                session.commit()

        session.close()

    @staticmethod
    def calcular_ranking(periodo='dia'):
        """
        Calcula ranking dos vendedores

        Args:
            periodo: 'dia', 'semana' ou 'mes'
        """
        session = get_session()
        hoje = date.today()

        # Define range de datas
        if periodo == 'dia':
            data_inicio = hoje
        elif periodo == 'semana':
            data_inicio = hoje - timedelta(days=hoje.weekday())  # segunda-feira
        elif periodo == 'mes':
            data_inicio = hoje.replace(day=1)
        else:
            data_inicio = hoje

        # Busca pontuações no período
        ranking_data = session.query(
            Vendedor.id,
            Vendedor.nome,
            Vendedor.avatar,
            Vendedor.nivel,
            Vendedor.xp_total,
            func.sum(Pontuacao.pontos).label('pontos_periodo')
        ).join(Pontuacao).filter(
            Pontuacao.data >= data_inicio,
            Pontuacao.data <= hoje
        ).group_by(
            Vendedor.id
        ).order_by(
            desc('pontos_periodo')
        ).all()

        # Monta resultado
        ranking = []
        for idx, (vid, nome, avatar, nivel, xp_total, pontos) in enumerate(ranking_data, 1):
            ranking.append({
                'posicao': idx,
                'vendedor_id': vid,
                'nome': nome,
                'avatar': avatar,
                'nivel': nivel,
                'xp_total': xp_total,
                'pontos_periodo': int(pontos or 0),
            })

        session.close()
        return ranking

    @staticmethod
    def registrar_acao(vendedor_id, tipo_acao, quantidade=1, detalhes=None):
        """
        Registra uma ação e calcula pontos

        Args:
            vendedor_id: ID do vendedor
            tipo_acao: tipo da ação realizada
            quantidade: quantidade de ações
            detalhes: informações extras
        """
        session = get_session()

        # Calcula pontos
        pontos = GamificationService.calcular_pontos_acao(tipo_acao, quantidade, detalhes)

        # Registra pontuação
        pontuacao = Pontuacao(
            vendedor_id=vendedor_id,
            data=date.today(),
            pontos=pontos,
            tipo_acao=tipo_acao,
            detalhes=f'{quantidade}x {tipo_acao}'
        )
        session.add(pontuacao)

        # Atualiza XP total do vendedor
        vendedor = session.query(Vendedor).filter_by(id=vendedor_id).first()
        if vendedor:
            vendedor.xp_total += pontos

        session.commit()
        session.close()

        # Atualiza nível
        nivel_info = GamificationService.atualizar_nivel_vendedor(vendedor_id)

        return {
            'pontos_ganhos': pontos,
            'nivel_info': nivel_info,
            'tipo_acao': tipo_acao
        }

    @staticmethod
    def atualizar_progresso_missao(vendedor_id, tipo_acao, quantidade=1):
        """Atualiza progresso de missões ativas do vendedor"""
        session = get_session()

        # Mapeamento de tipo_acao para tipo de missão
        mapeamento = {
            'lead_alcancado': 'leads',
            'entrevista_realizada': 'entrevistas',
            'venda': 'vendas',
        }

        tipo_missao = mapeamento.get(tipo_acao)
        if not tipo_missao:
            session.close()
            return []

        # Busca missões ativas que correspondem
        missoes = session.query(Missao).filter_by(
            vendedor_id=vendedor_id,
            status='ativa'
        ).filter(
            Missao.titulo.contains(tipo_missao.capitalize())
        ).all()

        missoes_concluidas = []

        for missao in missoes:
            missao.progresso += quantidade

            # Verifica se completou
            if missao.progresso >= missao.meta:
                missao.status = 'concluida'

                # Concede recompensa XP
                vendedor = session.query(Vendedor).filter_by(id=vendedor_id).first()
                if vendedor:
                    vendedor.xp_total += missao.recompensa_xp

                missoes_concluidas.append({
                    'titulo': missao.titulo,
                    'recompensa_xp': missao.recompensa_xp
                })

        session.commit()
        session.close()

        return missoes_concluidas

    @staticmethod
    def get_stats_vendedor(vendedor_id, periodo='mes'):
        """Retorna estatísticas do vendedor"""
        session = get_session()
        hoje = date.today()

        # Define período
        if periodo == 'dia':
            data_inicio = hoje
        elif periodo == 'semana':
            data_inicio = hoje - timedelta(days=7)
        elif periodo == 'mes':
            data_inicio = hoje - timedelta(days=30)
        else:
            data_inicio = hoje - timedelta(days=30)

        # Busca dados
        vendedor = session.query(Vendedor).filter_by(id=vendedor_id).first()

        if not vendedor:
            session.close()
            return None

        # Soma ações no período
        acoes = session.query(
            func.sum(AcaoDiaria.leads_alcancados).label('total_leads'),
            func.sum(AcaoDiaria.entrevistas_realizadas).label('total_entrevistas'),
            func.sum(AcaoDiaria.conversoes).label('total_conversoes'),
            func.sum(AcaoDiaria.vendas).label('total_vendas'),
            func.sum(AcaoDiaria.faturamento).label('total_faturamento'),
        ).filter(
            AcaoDiaria.vendedor_id == vendedor_id,
            AcaoDiaria.data >= data_inicio
        ).first()

        # Pontos no período
        pontos_periodo = session.query(
            func.sum(Pontuacao.pontos)
        ).filter(
            Pontuacao.vendedor_id == vendedor_id,
            Pontuacao.data >= data_inicio
        ).scalar() or 0

        # Missões ativas
        missoes_ativas = session.query(Missao).filter_by(
            vendedor_id=vendedor_id,
            status='ativa'
        ).count()

        # Badges
        total_badges = session.query(Conquista).filter_by(
            vendedor_id=vendedor_id
        ).count()

        session.close()

        return {
            'vendedor': {
                'id': vendedor.id,
                'nome': vendedor.nome,
                'nivel': vendedor.nivel,
                'xp_total': vendedor.xp_total,
                'avatar': vendedor.avatar,
            },
            'periodo': periodo,
            'leads': int(acoes.total_leads or 0),
            'entrevistas': int(acoes.total_entrevistas or 0),
            'conversoes': int(acoes.total_conversoes or 0),
            'vendas': int(acoes.total_vendas or 0),
            'faturamento': float(acoes.total_faturamento or 0),
            'pontos': int(pontos_periodo),
            'missoes_ativas': missoes_ativas,
            'badges': total_badges,
        }
