# 🎮 SalesQuest - Plataforma de Gamificação Comercial

Sistema completo de gamificação para equipes de vendas com IA proativa, ranking em tempo real, missões dinâmicas e integração WhatsApp.

---

## ✨ Funcionalidades

### 🎯 **Core Features**
- ✅ **Sistema de Pontuação Automático** - Pontos por leads, entrevistas, conversões e vendas
- ✅ **Níveis e XP** - 25 níveis (Prospector → Hunter → Closer → Master → Legend)
- ✅ **Ranking Tempo Real** - Dia / Semana / Mês
- ✅ **Badges e Conquistas** - Sistema de recompensas gamificadas
- ✅ **Missões Dinâmicas** - Diárias, semanais e side quests
- ✅ **Dashboard Web Responsivo** - Visualização completa de métricas

### 🤖 **IA Coach Proativa**
- 🌅 **Mensagens Matinais** - Motivação + metas do dia
- ⚡ **Feedback Imediato** - Notificação instantânea ao completar ações
- 📊 **Alertas de Performance** - Quando está abaixo da meta
- 🏆 **Provocações Saudáveis** - Estimula competição
- 🌙 **Relatório Noturno** - Resumo do dia automático

### 📱 **Integração WhatsApp**
- Mensagens automáticas via Evolution API
- Coach envia feedback direto no WhatsApp do vendedor
- Sistema de fila de mensagens

---

## 🚀 URLs de Acesso

### **Produção (VPS)**
- 🌐 **Dashboard**: http://212.85.23.66:5200
- 📊 **API Docs**: http://212.85.23.66:5200/api/health
- 🏆 **Ranking**: http://212.85.23.66:5200/api/ranking

### **Localmente**
- 🌐 **Dashboard**: http://localhost:5200
- 📊 **API**: http://localhost:5200/api/health

---

## 📊 Vendedores Fictícios (Demo)

| Nome | Avatar | Nível | XP Total | Badges |
|------|--------|-------|----------|--------|
| **Rafael Souza** | 👑 | 18 (Master III) | 4.102 XP | 5 badges (Legend, Unstoppable, Team Leader) |
| **Diego Santos** | 🔥 | 15 (Closer V) | 2.847 XP | 4 badges (Hat Trick, Speed Demon, Closer King) |
| **Mariana Costa** | ⭐ | 12 (Closer II) | 1.923 XP | 3 badges (Marathon Runner, Steady Eddie) |
| **Carlos Almeida** | 🎯 | 8 (Hunter III) | 876 XP | 2 badges (First Blood, Rising Star) |
| **Ana Paula** | 💎 | 5 (Prospector V) | 456 XP | 2 badges (Rookie, First Blood) |

**Dados**: 30 dias de histórico completo por vendedor (leads, entrevistas, vendas)

---

## 🎮 Sistema de Pontuação

### **Pontos Base**
| Ação | Pontos | Multiplicadores |
|------|--------|-----------------|
| Lead alcançado | 2 XP | +50% se passar meta diária |
| Entrevista agendada | 10 XP | +25% se agendar mesmo dia |
| Entrevista realizada | 15 XP | +50% se converter |
| Conversão | 30 XP | +100% se ticket > R$5k |
| Venda fechada | 50 XP | +20% por cada R$1k de ticket |
| Constância (5 dias) | 100 XP | Bonus semanal |

### **Metas Diárias Padrão**
- 📞 40 leads
- 🎯 3 entrevistas
- 💰 1 conversão

---

## 🏆 Badges Disponíveis

| Badge | Icon | Raridade | Conquista |
|-------|------|----------|-----------|
| First Blood | 🩸 | Comum | Primeira venda |
| Hat Trick | 🎩 | Raro | 3 vendas em 1 dia |
| Speed Demon | ⚡ | Raro | Conversão < 24h |
| Closer King | 👑 | Épico | 10 vendas/semana |
| Marathon Runner | 🏃 | Épico | 30 dias consecutivos |
| Steady Eddie | 🎯 | Raro | Meta 7 dias seguidos |
| Rising Star | 🌟 | Raro | +3 níveis em 1 mês |
| Legend | 🏆 | Lendário | Nível 20+ |
| Unstoppable | 🔥 | Épico | 50 vendas totais |
| Team Leader | 👨‍💼 | Épico | #1 ranking mensal |

---

## 📡 API Endpoints

### **Vendedores**
```bash
GET /api/vendedores              # Lista todos
GET /api/vendedores/:id          # Detalhes + stats
```

### **Ranking**
```bash
GET /api/ranking?periodo=dia     # Ranking do dia
GET /api/ranking?periodo=semana  # Ranking da semana
GET /api/ranking?periodo=mes     # Ranking do mês
```

### **Ações (Registrar atividade)**
```bash
POST /api/acoes/registrar
Body: {
  "vendedor_id": 1,
  "tipo_acao": "lead_alcancado",
  "quantidade": 5,
  "detalhes": {"meta_atingida": false}
}
```

**Tipos de ação**: `lead_alcancado`, `entrevista_agendada`, `entrevista_realizada`, `conversao`, `venda`

### **Coach IA**
```bash
GET /api/coach/motivacao/:id     # Mensagem motivacional
GET /api/coach/alerta/:id        # Alerta de performance
GET /api/coach/provocacao/:id    # Provocação ranking
GET /api/coach/relatorio/:id     # Relatório noturno
```

### **WhatsApp**
```bash
POST /api/whatsapp/enviar
Body: {
  "vendedor_id": 1,
  "mensagem": "Teste"
}

POST /api/whatsapp/processar-pendentes  # Envia todas pendentes
```

### **Stats Gerais**
```bash
GET /api/stats/geral             # Estatísticas do dia
GET /api/health                  # Health check
```

---

## 🛠️ Tech Stack

**Backend**:
- Python 3.11+
- Flask (API REST)
- SQLAlchemy (ORM)
- SQLite (banco de dados)
- OpenAI API (GPT-4o para Coach IA)

**Frontend**:
- HTML5 + CSS3 + JavaScript (Vanilla)
- Chart.js (opcional - futuro)
- Fetch API (requisições)

**Infraestrutura**:
- PM2 (gerenciamento processos)
- VPS (212.85.23.66)
- Evolution API (WhatsApp)

---

## 📦 Estrutura do Projeto

```
salesquest/
├── backend/
│   ├── app.py                    # Flask app principal
│   ├── config.py                 # Configurações
│   ├── models.py                 # Models SQLAlchemy
│   └── services/
│       ├── gamification.py       # Lógica pontos/níveis
│       ├── ai_agent.py           # Coach IA
│       └── whatsapp.py           # WhatsApp sender
├── frontend/
│   ├── index.html                # Dashboard
│   ├── css/styles.css            # Estilos
│   └── js/main.js                # JavaScript
├── data/
│   └── mock_crm.py               # Popular banco
├── salesquest.db                 # Banco SQLite
├── requirements.txt              # Dependências Python
└── README.md                     # Este arquivo
```

---

## 🚀 Como Rodar

### **VPS (Produção)**
Sistema já está rodando no PM2:

```bash
# Ver status
pm2 list | grep salesquest

# Ver logs
pm2 logs salesquest

# Restart
pm2 restart salesquest

# Stop
pm2 stop salesquest
```

### **Localmente (Desenvolvimento)**

1. **Instalar dependências**:
```bash
pip3 install -r requirements.txt
```

2. **Popular banco de dados**:
```bash
python3 data/mock_crm.py
```

3. **Iniciar servidor**:
```bash
python3 backend/app.py
```

4. **Acessar**:
- Dashboard: http://localhost:5200
- API: http://localhost:5200/api/health

---

## 🎯 Próximos Passos

### **Fase 1: Melhorias UI** 🎨
- [ ] Gráficos de evolução (Chart.js)
- [ ] Página de perfil detalhada
- [ ] Animações de confete ao ganhar XP
- [ ] Notificações browser (Web Push)

### **Fase 2: Features Avançadas** 🚀
- [ ] Missões coletivas do time
- [ ] Desafios semanais dinâmicos
- [ ] Sistema de recompensas reais
- [ ] Integração com CRM real (Pipedrive, RD Station)

### **Fase 3: Automação** 🤖
- [ ] Tarefas agendadas (APScheduler)
- [ ] Mensagens automáticas matinais
- [ ] Relatórios enviados automaticamente
- [ ] Webhook para receber dados CRM

### **Fase 4: Analytics** 📊
- [ ] Painel de admin completo
- [ ] Exportação de relatórios PDF
- [ ] Predição de performance (IA)
- [ ] Health score do vendedor

---

## 🎮 Como Testar o Sistema

### **Testar via API (Postman/Insomnia)**

1. **Registrar uma venda**:
```bash
curl -X POST http://212.85.23.66:5200/api/acoes/registrar \
  -H "Content-Type: application/json" \
  -d '{
    "vendedor_id": 1,
    "tipo_acao": "venda",
    "quantidade": 1,
    "detalhes": {"ticket": 8000}
  }'
```

2. **Ver ranking atualizado**:
```bash
curl http://212.85.23.66:5200/api/ranking?periodo=dia
```

3. **Gerar mensagem do coach**:
```bash
curl http://212.85.23.66:5200/api/coach/motivacao/1
```

### **Testar WhatsApp** (Evolution API)

```bash
curl -X POST http://212.85.23.66:5200/api/whatsapp/enviar \
  -H "Content-Type: application/json" \
  -d '{
    "vendedor_id": 1,
    "mensagem": "🎯 Teste SalesQuest!"
  }'
```

---

## 💡 Exemplos de Uso

### **Cenário 1: Vendedor fecha uma venda**

**Input (CRM/Sistema)**:
```json
{
  "vendedor_id": 1,
  "tipo_acao": "venda",
  "quantidade": 1,
  "detalhes": {"ticket": 12000}
}
```

**Output (Sistema)**:
- ✅ +50 XP base
- ✅ +20 XP bonus (ticket > R$5k)
- ✅ +24 XP bonus (R$1k extras)
- ✅ **Total: +94 XP**
- 📊 Ranking atualizado
- 🤖 Coach envia: "🔥 +94 XP! VENDA FECHADA! MONSTRUOSO!"
- 📱 Mensagem WhatsApp enviada

### **Cenário 2: Vendedor abaixo da meta (14:00)**

**Sistema detecta**:
- Meta: 40 leads
- Atual: 18 leads (45%)

**Coach gera alerta**:
```
⏰ Atenção, Diego!
Você está 22 leads abaixo da meta.
Revise sua lista de follow-up. Bora! 💪
```

### **Cenário 3: Vendedor sobe de nível**

**Evento**:
- XP anterior: 2.845
- Ação: +15 XP (entrevista)
- XP atual: 2.860
- Passa de Closer IV (2.701-3.000) → Closer V (3.001-3.400)

**Sistema**:
- 🎊 Animação level up
- 🏆 Badge "Closer Completo" desbloqueado
- 📱 WhatsApp: "🎊 LEVEL UP! Você alcançou o Nível 15!"

---

## 🔐 Configurações

### **Editar config.py**

```python
# Porta do servidor
PORT = 5200

# Metas diárias padrão
META_LEADS_DIA = 40
META_ENTREVISTAS_DIA = 3

# Horários das mensagens
HORARIO_MENSAGEM_MATINAL = "08:00"
HORARIO_ALERTA_TARDE = "14:00"
HORARIO_RELATORIO_NOITE = "19:00"

# OpenAI API
OPENAI_API_KEY = "sua-chave-aqui"

# Evolution API (WhatsApp)
EVOLUTION_API_URL = "https://..."
EVOLUTION_API_KEY = "..."
EVOLUTION_INSTANCE = "..."
```

---

## 📞 Suporte

**Desenvolvido por**: Felipe Zanoni
**Contato**: 5511947292318
**Agência**: Café Online

**Logs de erro**: Ver `pm2 logs salesquest`
**Banco de dados**: `/root/salesquest/salesquest.db`

---

## 🎉 Status

✅ **MVP COMPLETO E FUNCIONAL**
- 5 vendedores fictícios
- 30 dias de histórico
- API 100% funcional
- Dashboard responsivo
- Coach IA integrado
- Pronto para uso!

**Versão**: 1.0.0
**Data de criação**: 06/12/2025
**Última atualização**: 06/12/2025 21:30 BRT

---

🎮 **SalesQuest** - Transformando vendas em jogo! 🚀
