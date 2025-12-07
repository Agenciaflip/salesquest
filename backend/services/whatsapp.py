"""
Serviço de envio WhatsApp (Evolution API)
"""
import requests
import sys
from datetime import datetime
sys.path.append('/Users/felipezanonimini/Desktop/automacoes/salesquest')

from backend.config import Config
from backend.models import get_session, InteracaoIA

class WhatsAppService:
    """Serviço de envio de mensagens WhatsApp"""

    def __init__(self):
        self.api_url = Config.EVOLUTION_API_URL
        self.api_key = Config.EVOLUTION_API_KEY
        self.instance = Config.EVOLUTION_INSTANCE

    def enviar_mensagem(self, telefone, mensagem):
        """
        Envia mensagem de texto via Evolution API

        Args:
            telefone: número com DDI (ex: 5511987654321)
            mensagem: texto da mensagem
        """
        url = f"{self.api_url}/message/sendText/{self.instance}"

        headers = {
            "apikey": self.api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "number": telefone,
            "text": mensagem
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)

            if response.status_code == 201:
                return {
                    'sucesso': True,
                    'mensagem': 'Mensagem enviada com sucesso',
                    'data': response.json()
                }
            else:
                return {
                    'sucesso': False,
                    'mensagem': f'Erro ao enviar: {response.status_code}',
                    'data': response.text
                }

        except Exception as e:
            return {
                'sucesso': False,
                'mensagem': f'Erro na requisição: {str(e)}',
                'data': None
            }

    def enviar_mensagens_pendentes(self):
        """Envia todas as mensagens pendentes do banco"""
        session = get_session()

        # Busca mensagens não enviadas
        mensagens_pendentes = session.query(InteracaoIA).filter_by(enviado=False).all()

        total_enviadas = 0
        total_erros = 0

        for interacao in mensagens_pendentes:
            # Busca telefone do vendedor
            from backend.models import Vendedor
            vendedor = session.query(Vendedor).filter_by(id=interacao.vendedor_id).first()

            if not vendedor:
                continue

            # Envia mensagem
            resultado = self.enviar_mensagem(vendedor.telefone, interacao.mensagem)

            if resultado['sucesso']:
                interacao.enviado = True
                interacao.enviado_em = datetime.now()
                total_enviadas += 1
            else:
                total_erros += 1
                print(f"❌ Erro ao enviar para {vendedor.nome}: {resultado['mensagem']}")

        session.commit()
        session.close()

        return {
            'total_enviadas': total_enviadas,
            'total_erros': total_erros
        }

    def enviar_para_vendedor(self, vendedor_id, mensagem):
        """Envia mensagem diretamente para um vendedor"""
        session = get_session()

        from backend.models import Vendedor
        vendedor = session.query(Vendedor).filter_by(id=vendedor_id).first()

        if not vendedor:
            session.close()
            return {'sucesso': False, 'mensagem': 'Vendedor não encontrado'}

        resultado = self.enviar_mensagem(vendedor.telefone, mensagem)
        session.close()

        return resultado
