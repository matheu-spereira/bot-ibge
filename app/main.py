from ipca_bot import IPCABot
from datetime import datetime

# Obtém a data e hora atual formatada para usar nos nomes dos arquivos de log
current_date = datetime.now().strftime("%Y%m%d_%H%M%S")

# URL da API do IBGE para capturar dados do IPCA
url_ipca = "https://sidra.ibge.gov.br/Ajax/jSon/Tabela/1/1737?versao=-1"

# Diretório onde os dados Parquet serão salvos
caminho_saida = "../data/ipca/"

# Caminho do arquivo de logs, incluindo timestamp para versão única
caminho_logs = f"../data/logs_execucao/{current_date}.parquet"

# Cria uma instância do robô IPCABot, passando a URL e o caminho dos logs
bot = IPCABot(url_ipca, caminho_logs=caminho_logs)

try:
    # Executa todo o pipeline: captura, transformação e salvamento dos dados
    bot.executar_pipeline(caminho_saida)
    print(f"✅ Pipeline executado com sucesso. Dados salvos em: {caminho_saida}")
except Exception as e:
    # Caso ocorra erro em alguma etapa, imprime a mensagem de falha
    print(f"❌ Falha na execução do pipeline: {str(e)}")

# Imprime onde os logs da execução foram salvos
print(f"📝 Logs disponíveis em: {caminho_logs}")
