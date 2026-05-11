# 🏦 GenAI aplicada à Engenharia de Processos

Aplicação de IA Generativa baseada em arquitetura multiagente utilizando CrewAI para automatizar a triagem, análise e estruturação de solicitações operacionais recebidas pelas áreas de negócio de um banco.

A solução recebe demandas não estruturadas (texto livre, e-mails ou PDFs), identifica gargalos operacionais, classifica criticidade, sugere abordagens iniciais de análise e gera saídas estruturadas para apoio à tomada de decisão e integração com sistemas de backlog.

---

# 🚀 Objetivo do Projeto

A área de Engenharia de Processos de grandes instituições financeiras normalmente recebe alto volume de solicitações operacionais de forma manual e não padronizada, gerando:

- Alto tempo de análise inicial;
- Retrabalho operacional;
- Falta de priorização;
- Dependência de conhecimento tácito;
- Baixa rastreabilidade;
- Dificuldade de governança;
- Falta de padronização nas análises.

Este projeto utiliza IA Generativa e arquitetura multiagente para transformar solicitações não estruturadas em análises estruturadas, rastreáveis e acionáveis.

---

# 🧠 Principais Funcionalidades

## ✅ Recebimento de solicitações não estruturadas

A aplicação aceita:
- Texto livre;
- Conteúdo de e-mails;
- Arquivos PDF.

---

## ✅ Análise inteligente multiagente

A Crew executa:
- Limpeza e normalização da solicitação;
- Identificação de gargalos;
- Diagnóstico operacional;
- Priorização e criticidade;
- Sugestão de abordagem analítica;
- Estruturação executiva da análise.

---

## ✅ Geração de análise executiva

A saída é apresentada:
- em formato visual amigável;
- estruturada em Markdown;
- com opção de download em PDF.

---

## ✅ Integração com backlog operacional

A solução gera automaticamente:
- payload JSON estruturado;
- integração via API REST;
- persistência em Supabase.

---

## ✅ Observabilidade com AgentOps

O projeto possui:
- tracing de agentes;
- monitoramento de execução;
- métricas;
- spans;
- token tracking.

---

# 🏗️ Arquitetura da Solução

```text
Usuário
   ↓
Streamlit UI
   ↓
CrewAI Multi-Agent System
   ↓
LLM (Gemini)
   ↓
Análise Estruturada
   ↓
JSON de Integração
   ↓
Supabase (Backlog)
```

---

# 🤖 Arquitetura Multiagente

A solução utiliza múltiplos agentes especializados:

| Agente | Responsabilidade |
|---|---|
| Intake Analyst Agent | Estruturação inicial da solicitação |
| Process Diagnosis Agent | Identificação de gargalos e causas |
| Prioritization Agent | Classificação de criticidade |
| Solution Strategy Agent | Definição de abordagem recomendada |
| Governance Reporting Agent | Consolidação executiva da análise |

---

# 🛠️ Tecnologias Utilizadas

## Backend / IA
- Python
- CrewAI
- Gemini 2.5 Flash
- AgentOps

## Interface
- Streamlit

## Persistência
- Supabase
- REST API

## Documentos
- ReportLab
- PyPDF

---

# 📂 Estrutura do Projeto

```text
case_engprocessos/
│
├── src/case_engprocessos/
│   ├── crew.py
│   ├── main.py
│   ├── streamlit_app.py
│   ├── tools/
│   ├── config/
│   │   ├── agents.yaml
│   │   └── tasks.yaml
│
├── requirements.txt
├── .env
└── README.md
```

---

# ⚙️ Configuração do Ambiente

## 1. Clonar o repositório

```bash
git clone <URL_DO_REPOSITORIO>
cd case-GenAI_aplicado_a_eng_processos-itau
```

---

## 2. Criar ambiente virtual

### Windows

```bash
python -m venv .venv
```

Ativar:

```bash
.venv\Scripts\activate
```

---

## 3. Instalar dependências

```bash
pip install -r requirements.txt
```

---

# 🔐 Variáveis de Ambiente

Criar arquivo `.env`:

```env
GEMINI_API_KEY=YOUR_GEMINI_KEY
MODEL=gemini/gemini-2.5-flash

AGENTOPS_API_KEY=YOUR_AGENTOPS_KEY

API_BACKLOG_URL=YOUR_SUPABASE_API_URL
API_BACKLOG_TOKEN=YOUR_SUPABASE_TOKEN
```

---

# ▶️ Executando Localmente

## Streamlit

```bash
streamlit run case_engprocessos/src/case_engprocessos/streamlit_app.py
```

---

# ☁️ Deploy

O projeto pode ser publicado utilizando:

- GitHub
- Streamlit Cloud
- Supabase

---

# 🗄️ Integração com Supabase

A aplicação envia automaticamente:
- criticidade;
- impacto operacional;
- resumo executivo;
- payload JSON completo.

Tabela exemplo:

```sql
create table backlog_processos (
  id bigint generated always as identity primary key,
  created_at timestamp with time zone default timezone('utc'::text, now()),
  id_externo text,
  criticidade text,
  score_criticidade numeric,
  processo_impactado text,
  resumo_executivo text,
  impacto_operacional text,
  abordagem_recomendada text,
  payload jsonb
);
```

---

# 📊 Observabilidade

O projeto utiliza AgentOps para:
- tracing;
- monitoramento de workflows;
- token tracking;
- análise de execução multiagente.

---

# 📄 Exemplo de Cenário

```text
“O processo de aprovação de crédito PJ possui alto volume
de retrabalho operacional, múltiplas validações manuais
e atrasos recorrentes no SLA.”
```

A aplicação:
- identifica gargalos;
- sugere hipóteses de causa-raiz;
- classifica criticidade;
- recomenda abordagem;
- gera backlog estruturado.

---

# 🔮 Evoluções Futuras

- RAG corporativo;
- integração com Jira/ServiceNow;
- dashboards operacionais;
- analytics de backlog;
- armazenamento de PDFs no Supabase Storage;
- autenticação corporativa;
- histórico de análises;
- workflow humano no loop.

---

# 👩‍💻 Autora

Nayara Oliveira Sudário Diniz

Projeto desenvolvido como estudo e demonstração prática de aplicação de IA Generativa em Engenharia de Processos Bancários.
