import pandas as pd
import os
from dotenv import load_dotenv
from pandasai import SmartDataframe
from langchain_groq.chat_models import ChatGroq

# Carregar variáveis de ambiente
load_dotenv()

# Solicitar o caminho do arquivo parquet
while True:
    parquet_path = input("\nInforme o caminho do arquivo Parquet (ou 'exit' para sair): ")
    if parquet_path.lower() in ["exit", "sair", "quit"]:
        print("Encerrando. Até mais!")
        exit()

    if os.path.exists(parquet_path):
        try:
            data = pd.read_parquet(parquet_path)
            print("\n✅ Arquivo carregado com sucesso!")
            print(data.head())
            break
        except Exception as e:
            print(f"\n❌ Erro ao ler o arquivo: {e}")
    else:
        print("\n❌ Caminho inválido. Tente novamente.")

# 🔗 Definir o LLM
llm = ChatGroq(
    model_name="llama3-70b-8192",
    api_key=os.environ["api_key"]
)

# Prompt personalizado
custom_prompt = """
You are a data analysis assistant.

All your responses must be based solely on the data provided in the current dataframe.

Do not use any external knowledge beyond what is present in the dataframe.

If the request cannot be answered with the available data, respond with the following exact sentence:

"No information is available in the dataframe to answer this request. Please try again with another question."

If the information is present, provide a clear and objective answer directly based on the dataframe.

Always respond in plain text, without generating any Python code or code snippets.

The response should be a natural language explanation or answer, not code.
"""

#  Criar SmartDataframe no modo texto
df = SmartDataframe(
    data,
    config={
        "llm": llm,
        "custom_prompt": custom_prompt,
        "use_code": False,
        "llm_type": "chat"
    }
)

#  Loop interativo de perguntas
while True:
    pergunta = input("\nDigite sua pergunta (ou 'exit' para sair): ")
    if pergunta.lower() in ["exit", "sair", "quit"]:
        print("Encerrando interação. Até mais!")
        break
    try:
        resposta = df.chat(pergunta)
        print("\nResposta:", resposta)
    except Exception as e:
        print(f"\n❌ Ocorreu um erro: {e}")
