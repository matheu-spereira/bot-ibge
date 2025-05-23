# ipca_bot.py
import requests
import pandas as pd
import pyarrow.parquet as pq
import pyarrow as pa
from datetime import datetime
import pytz
import os

fuso_brasilia = pytz.timezone('America/Sao_Paulo')

class IPCABot:
    """
    Robô para capturar dados do IPCA do IBGE, salvar como Parquet e gerar logs da execução.
    """

    def __init__(self, url: str, caminho_logs: str = "./logs/logs_execucao.parquet"):
        """
        Inicializa o bot com a URL da API e o caminho para salvar logs.

        Args:
            url (str): URL para capturar os dados JSON do IPCA.
            caminho_logs (str, opcional): Caminho do arquivo para salvar os logs em formato Parquet.
        """
        self.url = url
        self.logs = []
        self.caminho_logs = caminho_logs

    def log(self, etapa: str, status: str, mensagem: str, extras: dict = None):
        """
        Registra um evento de log durante a execução.

        Args:
            etapa (str): Nome da etapa atual do processo (ex: "CapturaDados", "Transformacao").
            status (str): Status da etapa (ex: "INICIO", "OK", "ERRO").
            mensagem (str): Mensagem descritiva da etapa ou erro.
            extras (dict, opcional): Informações adicionais relevantes para o log.
        """
        registro = {
            "Timestamp": datetime.now(fuso_brasilia),
            "Etapa": etapa,
            "Status": status,
            "Mensagem": mensagem,
            "Extras": extras or {}
        }
        self.logs.append(registro)

    def salvar_logs(self):
        """
        Salva os logs acumulados em um arquivo Parquet no disco local.
        Cria diretórios necessários se não existirem.
        """
        df_logs = pd.DataFrame(self.logs)
        os.makedirs(os.path.dirname(self.caminho_logs), exist_ok=True)
        tabela = pa.Table.from_pandas(df_logs)
        pq.write_table(tabela, self.caminho_logs)

    def capturar_dados(self) -> dict:
        """
        Captura os dados da API IPCA do IBGE no formato JSON.

        Returns:
            dict: Dados JSON capturados da API.

        Raises:
            Exception: Se houver falha na requisição HTTP ou na obtenção dos dados.
        """
        self.log("CapturaDados", "INICIO", "Iniciando captura de dados.")
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            self.log("CapturaDados", "OK", "Captura concluída com sucesso.")
            return response.json()
        except Exception as e:
            self.log("CapturaDados", "ERRO", f"Erro na captura: {str(e)}")
            raise

    def transformar_em_dataframe(self, dados_json: dict) -> pd.DataFrame:
        """
        Transforma os dados JSON capturados em um DataFrame pandas estruturado.

        Args:
            dados_json (dict): Dados no formato JSON obtidos da API.

        Returns:
            pd.DataFrame: DataFrame contendo os dados estruturados.

        Raises:
            Exception: Se ocorrer erro na transformação dos dados.
        """
        self.log("Transformacao", "INICIO", "Iniciando transformação dos dados.")
        try:
            periodos = dados_json.get("Periodos", {}).get("Periodos", [])
            df_periodos = pd.DataFrame(periodos)

            if "DataLiberacao" in df_periodos.columns:
                df_periodos["DataLiberacao"] = pd.to_datetime(df_periodos["DataLiberacao"])

            df_periodos["DataExtracao"] = datetime.now(fuso_brasilia).strftime('%Y%m%d%H%M%S')

            self.log(
                "Transformacao",
                "OK",
                "Transformação concluída.",
                extras={"QtdLinhas": len(df_periodos)}
            )
            return df_periodos
        except Exception as e:
            self.log("Transformacao", "ERRO", f"Erro na transformação: {str(e)}")
            raise

    def salvar_parquet(self, df: pd.DataFrame, caminho_arquivo: str):
        """
        Salva o DataFrame no formato Parquet particionado pela coluna 'DataExtracao'.

        Args:
            df (pd.DataFrame): DataFrame a ser salvo.
            caminho_arquivo (str): Diretório raiz onde o dataset será salvo.

        Raises:
            ValueError: Se a coluna 'DataExtracao' não estiver presente no DataFrame.
            Exception: Para erros na escrita do arquivo Parquet.
        """
        self.log("SalvarParquet", "INICIO", f"Salvando dados particionado em {caminho_arquivo}")
        try:
            if 'DataExtracao' not in df.columns:
                raise ValueError("A coluna 'DataExtracao' não está presente no DataFrame.")

            tabela = pa.Table.from_pandas(df)

            os.makedirs(caminho_arquivo, exist_ok=True)
            pq.write_to_dataset(
                tabela,
                root_path=caminho_arquivo,
                partition_cols=['DataExtracao']
            )

            self.log(
                "SalvarParquet",
                "OK",
                "Dados salvos com sucesso.",
                extras={"QtdLinhas": len(df)}
            )

        except Exception as e:
            self.log("SalvarParquet", "ERRO", f"Erro ao salvar Parquet: {str(e)}")
            raise

    def gerar_relatorio_qualidade(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Gera um relatório básico de qualidade dos dados.

        Args:
            df (pd.DataFrame): DataFrame a ser avaliado.

        Returns:
            pd.DataFrame: DataFrame contendo métricas de qualidade para cada coluna.
        """
        total_linhas = len(df)
        
        relatorio = pd.DataFrame({
            'coluna': df.columns,
            'tipo': df.dtypes.astype(str),
            'qtd_nulos': df.isnull().sum().values,
            'pct_nulos': (df.isnull().mean() * 100).values,
            'qtd_unicos': df.nunique().values
        })

        # Estatísticas básicas só para colunas numéricas
        estatisticas = df.describe().T[['mean', 'min', 'max']]
        relatorio = relatorio.set_index('coluna')
        relatorio = relatorio.join(estatisticas)
        relatorio.reset_index(inplace=True)

        # Duplicatas
        relatorio['duplicatas'] = df.duplicated().sum()

        return relatorio

    def executar_pipeline(self, caminho_saida: str):
        """
        Orquestra o pipeline completo de captura, transformação e armazenamento dos dados,
        geração do relatório de qualidade e salvamento dos logs de execução.

        Args:
            caminho_saida (str): Diretório onde os dados Parquet serão salvos.

        Raises:
            Exception: Caso qualquer etapa do pipeline falhe.
        """
        try:
            self.log("Pipeline", "INICIO", "Início do pipeline completo.")
            dados = self.capturar_dados()
            df = self.transformar_em_dataframe(dados)

            # Gera relatório de qualidade e salva CSV
            relatorio_qualidade = self.gerar_relatorio_qualidade(df)
            os.makedirs(caminho_saida, exist_ok=True)
            relatorio_path = os.path.join(caminho_saida, "report_data_quality_ipca.csv")
            relatorio_qualidade.to_csv(relatorio_path, index=False)
            print(f"📊 Relatório de qualidade dos dados salvo em:{relatorio_path}")
            self.log("QualidadeDados", "OK", f"Relatório de qualidade salvo em {relatorio_path}")

            self.salvar_parquet(df, caminho_saida)
            self.log("Pipeline", "OK", "Pipeline executado com sucesso.")
        except Exception as e:
            self.log("Pipeline", "ERRO", f"Erro no pipeline: {str(e)}")
            raise
        finally:
            self.salvar_logs()
