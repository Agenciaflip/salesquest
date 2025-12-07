"""
Models do SalesQuest (SQLAlchemy + PostgreSQL)
"""
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from backend.config import Config

Base = declarative_base()
engine = create_engine(Config.DATABASE_URL)
Session = sessionmaker(bind=engine)

class Vendedor(Base):
    __tablename__ = 'salesquest_vendedores'

    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    telefone = Column(String(20), nullable=False, unique=True)
    email = Column(String(100))
    nivel = Column(Integer, default=1)
    xp_total = Column(Integer, default=0)
    avatar = Column(String(50), default='🎯')
    data_entrada = Column(Date, default=datetime.utcnow)
    ativo = Column(Boolean, default=True)

    # Relationships
    acoes = relationship('AcaoDiaria', back_populates='vendedor', cascade='all, delete-orphan')
    pontuacoes = relationship('Pontuacao', back_populates='vendedor', cascade='all, delete-orphan')
    conquistas = relationship('Conquista', back_populates='vendedor', cascade='all, delete-orphan')
    missoes = relationship('Missao', back_populates='vendedor', cascade='all, delete-orphan')

class AcaoDiaria(Base):
    __tablename__ = 'salesquest_acoes_diarias'

    id = Column(Integer, primary_key=True)
    vendedor_id = Column(Integer, ForeignKey('salesquest_vendedores.id'), nullable=False)
    data = Column(Date, nullable=False, default=datetime.utcnow)
    leads_alcancados = Column(Integer, default=0)
    entrevistas_agendadas = Column(Integer, default=0)
    entrevistas_realizadas = Column(Integer, default=0)
    conversoes = Column(Integer, default=0)
    vendas = Column(Integer, default=0)
    ticket_medio = Column(Float, default=0.0)
    faturamento = Column(Float, default=0.0)
    pontos_gerados = Column(Integer, default=0)
    criado_em = Column(DateTime, default=datetime.utcnow)

    # Relationships
    vendedor = relationship('Vendedor', back_populates='acoes')

class Pontuacao(Base):
    __tablename__ = 'salesquest_pontuacoes'

    id = Column(Integer, primary_key=True)
    vendedor_id = Column(Integer, ForeignKey('salesquest_vendedores.id'), nullable=False)
    data = Column(Date, nullable=False, default=datetime.utcnow)
    pontos = Column(Integer, nullable=False)
    tipo_acao = Column(String(50), nullable=False)  # lead, entrevista, conversao, venda
    detalhes = Column(Text)
    criado_em = Column(DateTime, default=datetime.utcnow)

    # Relationships
    vendedor = relationship('Vendedor', back_populates='pontuacoes')

class Ranking(Base):
    __tablename__ = 'salesquest_rankings'

    id = Column(Integer, primary_key=True)
    vendedor_id = Column(Integer, ForeignKey('salesquest_vendedores.id'), nullable=False)
    data = Column(Date, nullable=False, default=datetime.utcnow)
    posicao_dia = Column(Integer)
    posicao_semana = Column(Integer)
    posicao_mes = Column(Integer)
    pontos_dia = Column(Integer, default=0)
    pontos_semana = Column(Integer, default=0)
    pontos_mes = Column(Integer, default=0)
    criado_em = Column(DateTime, default=datetime.utcnow)

class Missao(Base):
    __tablename__ = 'salesquest_missoes'

    id = Column(Integer, primary_key=True)
    vendedor_id = Column(Integer, ForeignKey('salesquest_vendedores.id'), nullable=False)
    titulo = Column(String(200), nullable=False)
    descricao = Column(Text)
    tipo = Column(String(20), nullable=False)  # diaria, semanal, side_quest, coletiva
    meta = Column(Integer, nullable=False)  # número alvo
    progresso = Column(Integer, default=0)
    recompensa_xp = Column(Integer, default=0)
    status = Column(String(20), default='ativa')  # ativa, concluida, expirada
    data_inicio = Column(Date, default=datetime.utcnow)
    data_fim = Column(Date)
    criado_em = Column(DateTime, default=datetime.utcnow)

    # Relationships
    vendedor = relationship('Vendedor', back_populates='missoes')

class Conquista(Base):
    __tablename__ = 'salesquest_conquistas'

    id = Column(Integer, primary_key=True)
    vendedor_id = Column(Integer, ForeignKey('salesquest_vendedores.id'), nullable=False)
    badge_nome = Column(String(100), nullable=False)
    badge_icon = Column(String(10), default='🏆')
    badge_descricao = Column(Text)
    raridade = Column(String(20), default='comum')  # comum, raro, epico, lendario
    data_conquista = Column(DateTime, default=datetime.utcnow)

    # Relationships
    vendedor = relationship('Vendedor', back_populates='conquistas')

class InteracaoIA(Base):
    __tablename__ = 'salesquest_interacoes_ia'

    id = Column(Integer, primary_key=True)
    vendedor_id = Column(Integer, ForeignKey('salesquest_vendedores.id'), nullable=False)
    mensagem = Column(Text, nullable=False)
    tipo = Column(String(30), nullable=False)  # motivacao, alerta, parabens, provocacao, relatorio
    enviado = Column(Boolean, default=False)
    enviado_em = Column(DateTime)
    criado_em = Column(DateTime, default=datetime.utcnow)

class ConversaAnalisada(Base):
    __tablename__ = 'salesquest_conversas_analisadas'

    id = Column(Integer, primary_key=True)
    vendedor_id = Column(Integer, ForeignKey('salesquest_vendedores.id'), nullable=False)
    cliente_nome = Column(String(100))
    cliente_telefone = Column(String(20))
    tipo_conversa = Column(String(20), nullable=False)  # whatsapp, ligacao, email
    transcricao = Column(Text, nullable=False)
    duracao_segundos = Column(Integer)  # para ligações
    data_conversa = Column(DateTime, nullable=False)

    # Análise
    nota_geral = Column(Float, default=0.0)  # 0-10
    nota_etapas = Column(Float, default=0.0)
    nota_qualidade = Column(Float, default=0.0)
    nota_objecoes = Column(Float, default=0.0)
    nota_resultado = Column(Float, default=0.0)

    etapas_cumpridas = Column(String(200))  # JSON: ["saudacao", "descoberta", ...]
    pontos_melhoria = Column(Text)  # JSON array
    resultado = Column(String(50))  # venda_fechada, agendamento, sem_interesse, etc

    analisado = Column(Boolean, default=False)
    analisado_em = Column(DateTime)
    criado_em = Column(DateTime, default=datetime.utcnow)

class ScriptVendas(Base):
    __tablename__ = 'salesquest_scripts_vendas'

    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text)
    tipo_venda = Column(String(50))  # inbound, outbound, renewal
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.utcnow)

    # Relationships
    etapas = relationship('EtapaScript', back_populates='script', cascade='all, delete-orphan')

class EtapaScript(Base):
    __tablename__ = 'salesquest_etapas_script'

    id = Column(Integer, primary_key=True)
    script_id = Column(Integer, ForeignKey('salesquest_scripts_vendas.id'), nullable=False)
    ordem = Column(Integer, nullable=False)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text)
    obrigatoria = Column(Boolean, default=True)
    peso = Column(Float, default=1.0)  # peso na avaliação

    # Relationships
    script = relationship('ScriptVendas', back_populates='etapas')

class MetricasVendedor(Base):
    __tablename__ = 'salesquest_metricas_vendedor'

    id = Column(Integer, primary_key=True)
    vendedor_id = Column(Integer, ForeignKey('salesquest_vendedores.id'), nullable=False, unique=True)

    # Metas mensais
    meta_leads = Column(Integer, default=1200)
    meta_entrevistas = Column(Integer, default=90)
    meta_conversoes = Column(Integer, default=15)
    meta_vendas = Column(Integer, default=8)
    meta_ticket = Column(Float, default=5000.0)

    # Performance atual (mês)
    leads_mes = Column(Integer, default=0)
    entrevistas_mes = Column(Integer, default=0)
    conversoes_mes = Column(Integer, default=0)
    vendas_mes = Column(Integer, default=0)
    faturamento_mes = Column(Float, default=0.0)

    # Análise de qualidade
    nota_media_conversas = Column(Float, default=0.0)
    total_conversas_analisadas = Column(Integer, default=0)
    taxa_aprovacao_script = Column(Float, default=0.0)  # % etapas cumpridas

    # Streak
    dias_consecutivos_meta = Column(Integer, default=0)
    melhor_streak = Column(Integer, default=0)

    atualizado_em = Column(DateTime, default=datetime.utcnow)

def criar_tabelas():
    """Cria todas as tabelas no banco"""
    Base.metadata.create_all(engine)
    print("✅ Tabelas criadas com sucesso!")

def get_session():
    """Retorna sessão do banco"""
    return Session()
