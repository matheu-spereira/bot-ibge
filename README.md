# 📊 IBGE IPCA Data Pipeline

Este projeto consiste em um **robô de captura, transformação, análise de qualidade e armazenamento de dados do IPCA (Índice Nacional de Preços ao Consumidor Amplo)**, obtidos diretamente do site do **IBGE**.

Os dados são extraídos da API pública do IBGE (SIDRA), processados e armazenados em formato Parquet, juntamente com geração de logs e relatório de qualidade dos dados.

---

##  Funcionalidades

- 🔗 **Captura automática de dados do IPCA via API do IBGE (SIDRA)**.
- 🔄 **Transformação dos dados JSON em DataFrame estruturado e limpo**.
- 🏗️ **Armazenamento dos dados em formato Parquet**, com particionamento por data de extração.
- 🗒️ **Geração de relatório de qualidade dos dados**, incluindo:
  - Quantidade de valores únicos por coluna
  - Quantidade de valores nulos por coluna
  - Porcentagem de valores ausentes
  - Tipagem das colunas
  - Mín
  - Max
- 📑 **Geração de logs de execução detalhados** em formato Parquet, com:
  - Timestamp da execução
  - Etapa executada
  - Status (INICIO, OK, ERRO)
  - Mensagens e detalhes adicionais
- ✅ **Pipeline automatizado de ponta a ponta**, que executa:
  1. Captura dos dados
  2. Transformação
  3. Relatório de qualidade
  4. Salvamento dos dados e logs
- 🕒 **Execução agendada**, conforme [etapa](https://github.com/matheu-spereira/bot-ibge?tab=readme-ov-file#agendamento-do-bot-cron-no-linux):
  - Execução agendada por meio do CRON


---

##  Estrutura do Projeto
```bash

└──bot-ibge
   ├──app/
   │  ├──.env
   │  ├──ipca_bot.py 
   │  ├──main.py 
   │  └──chat_bot.py
   ├──data/
   │  ├──ipca/ 
   │  │   ├──DataExtracao=YYYYMMDDHHMMSS/ 
   │  │   │   └──{arquivo}.parquet
   │  │   └──resport_data_quality_ipca.csv
   │  └── logs_execucao/ 
   │      └──{YYYYMMDD_HHMMSS}.parquet
   ├──.gitignore
   ├──README.md 
   ├──requirements.txt
   ├──script.sh
   └──solucao.txt

```


---
## **IMPORTANTE** Pré - Requisitos Ambiente Linux
- Python >= 3.10
- python3.{versão}-dev
- build-essential

Por exemplo, rodar: apt-get update && apt-get install python3.{versão}-dev build-essential


##  Bibliotecas necessárias (Presente no requirements)

- pyarrow 15.0.2
- requests 2.31.0
- pandasai 2.3.0
- groq 0.25.0
- langchain_groq 0.3.2

---

## Como Executar Localmente

### 1. Clone o repositório:

```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio/app
```

### 2. Crie e ative um ambiente virtual (opcional, mas recomendado):

```bash
python3 -m venv venv
source venv/bin/activate  
```

### 3. Instale as dependências:

```bash
pip install -r requirements.txt 
```

### 4. Execute o script:

```bash
cd app && python3 main.py
```

## Estrutura de Saída
- Dados IPCA são salvos particionados pela data de extração, em:

```bash
/data/
└── ipca/
    └── DataExtracao=YYYYMMDDHHMMSS/
        └── {arquivo}.parquet
```

- Relatório de qualidade salvo em:
```bash
/data/
└── ipca/
    └── report_data_quality_ipca.csv
```

- Logs de execução salvos em:
```bash
/data/
└── logs_execucao/
    └── {YYYYMMDD_HHMMSS}.parquet
```

## Agendamento do Bot (CRON no Linux)
Se desejar que a extração de dados seja executada automaticamente em horários programados, é possível utilizar o CRON, um agendador nativo do Linux. Para isso, siga os passos abaixo:

### 1. Verifique o script de execução [script.sh](https://github.com/matheu-spereira/bot-ibge/blob/main/script.sh)

Configure o script conforme o ambiente local para:

* Ativar o ambiente virtual Python.

* Navegar até o diretório do projeto.

* Executar o arquivo main.py

### 2. Conceda permissão de execução ao script
```bash
chmod +x {caminho}/script.sh
```

### 3. Acesse o CRON do usuário
```bash
crontab -e
```

### 4. Adicione a linha de agendamento no CRON
Exemplo: executar o bot todos os dias às 14h30:
```bash
30 14 * * * /home/matheus/bot-ibge/script.sh
```
