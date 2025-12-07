"""
Configurações do SalesQuest
"""
import os
from datetime import timedelta
from pathlib import Path

class Config:
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'salesquest-secret-key-2025')

    # Database SQLite (path dinâmico)
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATABASE_URL = f"sqlite:///{BASE_DIR}/salesquest.db"

    # OpenAI API
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')

    # Evolution API (WhatsApp)
    EVOLUTION_API_URL = "https://evolution-nova-versao-evolution-api.78s68s.easypanel.host"
    EVOLUTION_API_KEY = "BA2E418A94D9-40BF-99E6-9F68AEAD8BE2"
    EVOLUTION_INSTANCE = "felipe1234"

    # Telefone Felipe (para testes)
    FELIPE_PHONE = "5511947292318"

    # Servidor
    HOST = '0.0.0.0'
    PORT = 5200
    DEBUG = True

    # Timezone
    TIMEZONE = 'America/Sao_Paulo'

    # Regras de gamificação
    PONTOS = {
        'lead_alcancado': 2,
        'entrevista_agendada': 10,
        'entrevista_realizada': 15,
        'conversao': 30,
        'venda': 50,
        'bonus_meta_diaria': 1.5,  # multiplicador
        'bonus_mesmo_dia': 1.25,
        'bonus_conversao': 1.5,
        'bonus_ticket_alto': 2.0,  # ticket > 5000
        'bonus_ticket_por_mil': 0.2,  # +20% a cada R$1000
        'bonus_constancia_semanal': 100,
    }

    # Níveis
    NIVEIS = [
        {'nivel': 1, 'nome': 'Prospector I', 'xp_min': 0, 'xp_max': 100},
        {'nivel': 2, 'nome': 'Prospector II', 'xp_min': 101, 'xp_max': 200},
        {'nivel': 3, 'nome': 'Prospector III', 'xp_min': 201, 'xp_max': 350},
        {'nivel': 4, 'nome': 'Prospector IV', 'xp_min': 351, 'xp_max': 500},
        {'nivel': 5, 'nome': 'Prospector V', 'xp_min': 501, 'xp_max': 700},
        {'nivel': 6, 'nome': 'Hunter I', 'xp_min': 701, 'xp_max': 900},
        {'nivel': 7, 'nome': 'Hunter II', 'xp_min': 901, 'xp_max': 1100},
        {'nivel': 8, 'nome': 'Hunter III', 'xp_min': 1101, 'xp_max': 1300},
        {'nivel': 9, 'nome': 'Hunter IV', 'xp_min': 1301, 'xp_max': 1500},
        {'nivel': 10, 'nome': 'Hunter V', 'xp_min': 1501, 'xp_max': 1800},
        {'nivel': 11, 'nome': 'Closer I', 'xp_min': 1801, 'xp_max': 2100},
        {'nivel': 12, 'nome': 'Closer II', 'xp_min': 2101, 'xp_max': 2400},
        {'nivel': 13, 'nome': 'Closer III', 'xp_min': 2401, 'xp_max': 2700},
        {'nivel': 14, 'nome': 'Closer IV', 'xp_min': 2701, 'xp_max': 3000},
        {'nivel': 15, 'nome': 'Closer V', 'xp_min': 3001, 'xp_max': 3400},
        {'nivel': 16, 'nome': 'Master I', 'xp_min': 3401, 'xp_max': 3800},
        {'nivel': 17, 'nome': 'Master II', 'xp_min': 3801, 'xp_max': 4200},
        {'nivel': 18, 'nome': 'Master III', 'xp_min': 4201, 'xp_max': 4600},
        {'nivel': 19, 'nome': 'Master IV', 'xp_min': 4601, 'xp_max': 5000},
        {'nivel': 20, 'nome': 'Master V', 'xp_min': 5001, 'xp_max': 6000},
        {'nivel': 21, 'nome': 'Legend I', 'xp_min': 6001, 'xp_max': 7500},
        {'nivel': 22, 'nome': 'Legend II', 'xp_min': 7501, 'xp_max': 9000},
        {'nivel': 23, 'nome': 'Legend III', 'xp_min': 9001, 'xp_max': 11000},
        {'nivel': 24, 'nome': 'Legend IV', 'xp_min': 11001, 'xp_max': 13500},
        {'nivel': 25, 'nome': 'Legend V', 'xp_min': 13501, 'xp_max': 999999},
    ]

    # Metas diárias padrão
    META_LEADS_DIA = 40
    META_ENTREVISTAS_DIA = 3
    META_CONVERSOES_DIA = 1

    # Horários das mensagens automáticas
    HORARIO_MENSAGEM_MATINAL = "08:00"
    HORARIO_ALERTA_TARDE = "14:00"
    HORARIO_RELATORIO_NOITE = "19:00"
