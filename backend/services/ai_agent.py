"""
Agente IA Coach - Gamificação Proativa
"""
import sys
from datetime import datetime
from openai import OpenAI
sys.path.append('/Users/felipezanonimini/Desktop/automacoes/salesquest')

from backend.config import Config
from backend.models import get_session, InteracaoIA
from backend.services.gamification import GamificationService

class CoachAI:
    """Agente IA Coach do SalesQuest"""

    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = "gpt-4o"

    def gerar_mensagem_motivacional_matinal(self, vendedor_id):
        """Gera mensagem motivacional para início do dia"""
        stats = GamificationService.get_stats_vendedor(vendedor_id, periodo='dia')

        if not stats:
            return None

        vendedor = stats['vendedor']

        prompt = f"""Você é o Coach Quest, um coach de vendas gamificado, enérgico e motivador.

VENDEDOR: {vendedor['nome']}
NÍVEL: {vendedor['nivel']} ({vendedor['xp_total']} XP)
AVATAR: {vendedor['avatar']}

Gere uma mensagem de BOM DIA motivacional para WhatsApp que:
- Seja curta (máximo 4 linhas)
- Use emojis apropriados
- Mencione as metas do dia: {Config.META_LEADS_DIA} leads, {Config.META_ENTREVISTAS_DIA} entrevistas
- Seja enérgica e competitiva
- Termine com um call-to-action

Tom: Encorajador, direto, sem formalidade excessiva."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
            max_tokens=150
        )

        mensagem = response.choices[0].message.content.strip()
        self._salvar_interacao(vendedor_id, mensagem, 'motivacao')

        return mensagem

    def gerar_feedback_imediato(self, vendedor_id, tipo_acao, pontos_ganhos, nivel_info=None):
        """Gera feedback imediato após uma ação"""
        stats = GamificationService.get_stats_vendedor(vendedor_id, periodo='dia')

        if not stats:
            return None

        vendedor = stats['vendedor']

        # Mensagens rápidas por tipo de ação
        templates = {
            'lead_alcancado': f"⚡ +{pontos_ganhos} XP! Lead registrado! Continue assim!",
            'entrevista_agendada': f"📅 +{pontos_ganhos} XP! Entrevista agendada! Boa!",
            'entrevista_realizada': f"💥 +{pontos_ganhos} XP! Entrevista realizada! Show!",
            'conversao': f"🎯 +{pontos_ganhos} XP! CONVERSÃO! Você é fera!",
            'venda': f"🔥 +{pontos_ganhos} XP! VENDA FECHADA! MONSTRUOSO!",
        }

        mensagem_base = templates.get(tipo_acao, f"+{pontos_ganhos} XP!")

        # Se subiu de nível, adiciona
        if nivel_info and nivel_info.get('subiu'):
            mensagem_base += f"\n\n🎊 LEVEL UP! Você alcançou o Nível {nivel_info['nivel']}!"

        self._salvar_interacao(vendedor_id, mensagem_base, 'parabens')

        return mensagem_base

    def gerar_alerta_performance(self, vendedor_id):
        """Gera alerta quando vendedor está abaixo da meta"""
        stats = GamificationService.get_stats_vendedor(vendedor_id, periodo='dia')

        if not stats:
            return None

        vendedor = stats['vendedor']
        leads_hoje = stats['leads']
        meta_leads = Config.META_LEADS_DIA

        # Calcula % da meta
        percentual = (leads_hoje / meta_leads) * 100 if meta_leads > 0 else 0

        # Só alerta se estiver abaixo de 70%
        if percentual >= 70:
            return None

        prompt = f"""Você é o Coach Quest, um coach de vendas gamificado.

VENDEDOR: {vendedor['nome']}
LEADS HOJE: {leads_hoje}
META: {meta_leads}
PERFORMANCE: {percentual:.0f}% da meta

Gere um ALERTA curto (máx 3 linhas) que:
- Seja direto mas encorajador
- Mencione a diferença para a meta
- Sugira ação imediata
- Use emoji adequado (⏰, ⚠️, etc)

Tom: Alerta mas não desmotivador."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=100
        )

        mensagem = response.choices[0].message.content.strip()
        self._salvar_interacao(vendedor_id, mensagem, 'alerta')

        return mensagem

    def gerar_provocacao_ranking(self, vendedor_id):
        """Gera provocação saudável baseada no ranking"""
        session = get_session()

        # Busca ranking do dia
        ranking = GamificationService.calcular_ranking('dia')

        if not ranking or len(ranking) < 2:
            session.close()
            return None

        # Encontra vendedor no ranking
        posicao_atual = None
        vendedor_atual = None
        for item in ranking:
            if item['vendedor_id'] == vendedor_id:
                posicao_atual = item['posicao']
                vendedor_atual = item
                break

        if not posicao_atual:
            session.close()
            return None

        # Se está em 1º, parabeniza
        if posicao_atual == 1:
            diferenca = vendedor_atual['pontos_periodo'] - ranking[1]['pontos_periodo']
            mensagem = f"👑 Você está em #1 no ranking!\n"
            mensagem += f"Diferença: {diferenca} pontos do 2º lugar.\n"
            mensagem += f"Mantenha a liderança! 🔥"

        # Se não está em 1º, provoca
        else:
            lider = ranking[0]
            diferenca = lider['pontos_periodo'] - vendedor_atual['pontos_periodo']

            mensagem = f"🏆 {lider['nome']} está em #1!\n"
            mensagem += f"Diferença: {diferenca} pontos.\n"
            mensagem += f"Você está em #{posicao_atual}. Vai deixar? 😏"

        self._salvar_interacao(vendedor_id, mensagem, 'provocacao')
        session.close()

        return mensagem

    def gerar_relatorio_noturno(self, vendedor_id):
        """Gera relatório do dia ao final do expediente"""
        stats = GamificationService.get_stats_vendedor(vendedor_id, periodo='dia')

        if not stats:
            return None

        vendedor = stats['vendedor']
        ranking = GamificationService.calcular_ranking('dia')

        # Encontra posição no ranking
        posicao = None
        for item in ranking:
            if item['vendedor_id'] == vendedor_id:
                posicao = item['posicao']
                break

        mensagem = f"📊 *Resultado do dia, {vendedor['nome']}*\n\n"

        # Leads
        percentual_leads = (stats['leads'] / Config.META_LEADS_DIA) * 100
        emoji_leads = "✅" if percentual_leads >= 100 else "⚠️" if percentual_leads >= 70 else "❌"
        mensagem += f"{emoji_leads} {stats['leads']} leads ({percentual_leads:.0f}% da meta)\n"

        # Entrevistas
        if stats['entrevistas'] > 0:
            mensagem += f"✅ {stats['entrevistas']} entrevistas realizadas\n"

        # Conversões
        if stats['conversoes'] > 0:
            mensagem += f"✅ {stats['conversoes']} conversões (+{stats['conversoes'] * 30} XP)\n"

        # Vendas
        if stats['vendas'] > 0:
            mensagem += f"🔥 {stats['vendas']} vendas (R$ {stats['faturamento']:,.2f})\n"

        # Total XP
        mensagem += f"\n🎯 Total: +{stats['pontos']} XP hoje\n"
        mensagem += f"Posição: #{posicao} no ranking\n"

        # Motivação final
        if posicao == 1:
            mensagem += f"\n👑 Você é o líder! Mantenha o ritmo! 🚀"
        elif posicao == 2:
            mensagem += f"\n🔥 Você está quase lá! Amanhã pode ser #1! 💪"
        else:
            mensagem += f"\n💪 Amanhã você sobe no ranking! Bora! 🚀"

        self._salvar_interacao(vendedor_id, mensagem, 'relatorio')

        return mensagem

    def _salvar_interacao(self, vendedor_id, mensagem, tipo):
        """Salva interação no banco para histórico"""
        session = get_session()

        interacao = InteracaoIA(
            vendedor_id=vendedor_id,
            mensagem=mensagem,
            tipo=tipo,
            enviado=False
        )

        session.add(interacao)
        session.commit()
        session.close()
