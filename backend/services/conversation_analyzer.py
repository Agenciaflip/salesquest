"""
Service de Análise de Conversas com IA
Analisa conversas de WhatsApp e ligações usando GPT-4o
"""
import json
from datetime import datetime
from openai import OpenAI
from backend.config import Config
from backend.models import ConversaAnalisada, ScriptVendas, EtapaScript, get_session

client = OpenAI(api_key=Config.OPENAI_API_KEY)

# Script de vendas padrão
SCRIPT_VENDAS_PADRAO = {
    "nome": "Script Consultivo Padrão",
    "etapas": [
        {
            "ordem": 1,
            "nome": "Saudação Profissional",
            "descricao": "Cumprimento educado + apresentação pessoal",
            "peso": 1.0,
            "exemplos": ["Bom dia!", "Olá, como vai?", "Prazer em falar com você"]
        },
        {
            "ordem": 2,
            "nome": "Identificação",
            "descricao": "Nome + empresa + motivo do contato",
            "peso": 1.5,
            "exemplos": ["Meu nome é X da empresa Y", "Estou entrando em contato porque..."]
        },
        {
            "ordem": 3,
            "nome": "Descoberta de Necessidades",
            "descricao": "Perguntas abertas para entender a dor do cliente",
            "peso": 2.0,
            "exemplos": ["Qual é seu maior desafio?", "Como funciona hoje?", "O que você gostaria de melhorar?"]
        },
        {
            "ordem": 4,
            "nome": "Apresentação de Solução",
            "descricao": "Explicar 3 benefícios principais do produto/serviço",
            "peso": 2.0,
            "exemplos": ["Nossa solução oferece...", "Com isso você consegue...", "Os principais benefícios são..."]
        },
        {
            "ordem": 5,
            "nome": "Tratamento de Objeções",
            "descricao": "Responder dúvidas e objeções com empatia",
            "peso": 1.5,
            "exemplos": ["Entendo sua preocupação...", "Deixa eu explicar melhor...", "Muitos clientes pensam assim..."]
        },
        {
            "ordem": 6,
            "nome": "Fechamento com CTA",
            "descricao": "Propor próximo passo claro",
            "peso": 2.0,
            "exemplos": ["Podemos agendar uma demonstração?", "Vamos fechar?", "Qual seria o melhor dia?"]
        },
        {
            "ordem": 7,
            "nome": "Follow-up",
            "descricao": "Combinar próximo contato ou enviar material",
            "peso": 1.0,
            "exemplos": ["Vou te enviar o contrato", "Te ligo amanhã às 10h", "Coloquei na agenda"]
        }
    ]
}

def analisar_conversa(transcricao: str, vendedor_id: int, cliente_nome: str = None,
                      tipo_conversa: str = "whatsapp", duracao_segundos: int = None) -> dict:
    """
    Analisa uma conversa usando GPT-4o e retorna avaliação detalhada

    Args:
        transcricao: Texto completo da conversa
        vendedor_id: ID do vendedor
        cliente_nome: Nome do cliente (opcional)
        tipo_conversa: whatsapp, ligacao ou email
        duracao_segundos: Duração da ligação (se aplicável)

    Returns:
        dict com nota_geral, etapas_cumpridas, pontos_melhoria, etc
    """

    # Montar prompt para GPT-4o
    prompt = f"""
Você é um especialista em análise de vendas consultivas. Analise a seguinte conversa entre um vendedor e um cliente.

**SCRIPT DE VENDAS ESPERADO:**

{json.dumps(SCRIPT_VENDAS_PADRAO['etapas'], indent=2, ensure_ascii=False)}

**CONVERSA A SER ANALISADA:**

{transcricao}

---

**TAREFA:**

Avalie a conversa em uma escala de 0 a 10 nos seguintes critérios:

1. **Nota Etapas** (0-10): Quantas etapas do script foram cumpridas adequadamente?
2. **Nota Qualidade** (0-10): Qualidade da abordagem (tom profissional, empático, claro)?
3. **Nota Objeções** (0-10): Como tratou as objeções e dúvidas do cliente?
4. **Nota Resultado** (0-10): Conseguiu um resultado positivo (venda, agendamento, interesse)?

**RETORNE UM JSON com a seguinte estrutura:**

{{
  "nota_etapas": 8.5,
  "nota_qualidade": 9.0,
  "nota_objecoes": 7.5,
  "nota_resultado": 8.0,
  "nota_geral": 8.25,
  "etapas_cumpridas": ["saudacao", "identificacao", "descoberta", "solucao", "fechamento"],
  "etapas_faltantes": ["tratamento_objecoes", "follow_up"],
  "pontos_positivos": [
    "Tom profissional e empático",
    "Fez boas perguntas de descoberta",
    "Apresentou benefícios claros"
  ],
  "pontos_melhoria": [
    "Poderia ter aprofundado mais no tratamento de objeções",
    "Faltou combinar follow-up específico"
  ],
  "resultado": "agendamento",
  "resumo": "Conversa bem conduzida, vendedor seguiu maior parte do script. Cliente demonstrou interesse e agendou demonstração. Principais oportunidades: aprofundar tratamento de objeções e garantir follow-up estruturado."
}}

**NOTAS IMPORTANTES:**
- Seja rigoroso mas justo
- A nota_geral deve ser a média ponderada das 4 notas
- Em etapas_cumpridas, liste apenas as que foram REALMENTE cumpridas
- Em resultado, use: "venda_fechada", "agendamento", "interesse", "sem_interesse", "perdido"
"""

    try:
        # Chamar GPT-4o
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Você é um especialista em análise de vendas consultivas. Retorne APENAS JSON válido."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1500
        )

        # Extrair resposta
        analise_texto = response.choices[0].message.content.strip()

        # Tentar parsear JSON
        # Remover possíveis markdown code blocks
        if "```json" in analise_texto:
            analise_texto = analise_texto.split("```json")[1].split("```")[0].strip()
        elif "```" in analise_texto:
            analise_texto = analise_texto.split("```")[1].split("```")[0].strip()

        analise = json.loads(analise_texto)

        # Garantir que tem todos os campos
        analise.setdefault("nota_etapas", 5.0)
        analise.setdefault("nota_qualidade", 5.0)
        analise.setdefault("nota_objecoes", 5.0)
        analise.setdefault("nota_resultado", 5.0)
        analise.setdefault("nota_geral", 5.0)
        analise.setdefault("etapas_cumpridas", [])
        analise.setdefault("pontos_melhoria", [])
        analise.setdefault("resultado", "sem_interesse")

        return analise

    except Exception as e:
        print(f"❌ Erro ao analisar conversa: {e}")
        # Retornar análise padrão em caso de erro
        return {
            "nota_etapas": 5.0,
            "nota_qualidade": 5.0,
            "nota_objecoes": 5.0,
            "nota_resultado": 5.0,
            "nota_geral": 5.0,
            "etapas_cumpridas": [],
            "pontos_melhoria": ["Erro ao analisar conversa"],
            "resultado": "erro"
        }

def salvar_conversa_analisada(vendedor_id: int, transcricao: str,
                              cliente_nome: str = None, cliente_telefone: str = None,
                              tipo_conversa: str = "whatsapp", duracao_segundos: int = None) -> ConversaAnalisada:
    """
    Analisa e salva uma conversa no banco de dados

    Returns:
        ConversaAnalisada object salvo
    """

    # Analisar com GPT-4o
    analise = analisar_conversa(transcricao, vendedor_id, cliente_nome, tipo_conversa, duracao_segundos)

    # Criar objeto de conversa
    session = get_session()

    conversa = ConversaAnalisada(
        vendedor_id=vendedor_id,
        cliente_nome=cliente_nome or "Cliente",
        cliente_telefone=cliente_telefone,
        tipo_conversa=tipo_conversa,
        transcricao=transcricao,
        duracao_segundos=duracao_segundos,
        data_conversa=datetime.utcnow(),

        # Notas
        nota_geral=analise['nota_geral'],
        nota_etapas=analise['nota_etapas'],
        nota_qualidade=analise['nota_qualidade'],
        nota_objecoes=analise['nota_objecoes'],
        nota_resultado=analise['nota_resultado'],

        # Detalhes
        etapas_cumpridas=json.dumps(analise['etapas_cumpridas']),
        pontos_melhoria=json.dumps(analise['pontos_melhoria']),
        resultado=analise['resultado'],

        analisado=True,
        analisado_em=datetime.utcnow()
    )

    session.add(conversa)
    session.commit()

    print(f"✅ Conversa analisada e salva! Nota: {analise['nota_geral']}/10")

    return conversa

def get_nota_media_vendedor(vendedor_id: int, ultimos_dias: int = 30) -> float:
    """Retorna nota média do vendedor nos últimos X dias"""
    session = get_session()

    conversas = session.query(ConversaAnalisada).filter(
        ConversaAnalisada.vendedor_id == vendedor_id,
        ConversaAnalisada.analisado == True
    ).all()

    if not conversas:
        return 0.0

    notas = [c.nota_geral for c in conversas]
    return round(sum(notas) / len(notas), 2)

def get_conversas_recentes(vendedor_id: int, limit: int = 10) -> list:
    """Retorna últimas conversas analisadas do vendedor"""
    session = get_session()

    conversas = session.query(ConversaAnalisada).filter(
        ConversaAnalisada.vendedor_id == vendedor_id
    ).order_by(ConversaAnalisada.data_conversa.desc()).limit(limit).all()

    return conversas
