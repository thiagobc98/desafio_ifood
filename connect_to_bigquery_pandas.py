from google.cloud import bigquery
import pandas as pd
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'C:/Users/Thiago/Desktop/GPC/dadosgithub-d15fe6a43acc.json'

def leitura_tratamento_dados():
    # Criar DataFrame de exemplo
    df = pd.read_csv('github_followers.csv')
    df["Criado em"] = pd.to_datetime(df["Criado em"], errors="coerce").dt.date
    return df

def criando_df_bigquery():
    # Definir cliente do BigQuery
    client = bigquery.Client()
    # Nome do dataset
    dataset_id = "data_git"

    # Referência ao dataset
    dataset_ref = client.dataset(dataset_id)

    # Criar o dataset se não existir
    dataset = bigquery.Dataset(dataset_ref)
    dataset.location = "US"  # Escolha a região onde deseja armazenar os dados

    dataset = client.create_dataset(dataset, exists_ok=True)
    print(f"Dataset {dataset_id} criado ou já existente.")
    return client, dataset_id

def criando_tabela_bigquery(client, dataset_id):
    
    # Definir o esquema da tabela (Exemplo com 2 colunas)
    schema = [
        bigquery.SchemaField("Nome", "STRING"),
        bigquery.SchemaField("Username", "STRING"),
        bigquery.SchemaField("Empresa", "STRING"),
        bigquery.SchemaField("Blog", "STRING"),
        bigquery.SchemaField("Email", "STRING"),
        bigquery.SchemaField("Biografia", "STRING"),
        bigquery.SchemaField("Repositórios Públicos", "INTEGER"),
        bigquery.SchemaField("Seguidores", "INTEGER"),
        bigquery.SchemaField("Seguindo", "INTEGER"),
        bigquery.SchemaField("Criado em", "DATE"),

    ]

    tabela_id = "github_contas"
    tabela_ref = client.dataset(dataset_id).table(tabela_id)

    try:
        client.get_table(tabela_ref)  # Verifica se a tabela já existe
        print(f"Tabela '{tabela_id}' já existe.")
    except Exception:
        tabela = bigquery.Table(tabela_ref, schema=schema)
        client.create_table(tabela)
        print(f"Tabela '{tabela_id}' criada com sucesso.")
    
    return tabela_id

def upload_bigquery():
    df = leitura_tratamento_dados()
    client, dataset_id = criando_df_bigquery()
    tabela_id = criando_tabela_bigquery(client, dataset_id)

    tabela_ref = client.dataset(dataset_id).table(tabela_id)

    # Subir os dados do DataFrame para o BigQuery
    job = client.load_table_from_dataframe(df, tabela_ref)

    # Esperar a carga ser concluída
    job.result()

    print("Upload concluído com sucesso!")

if __name__ == "__main__":
    upload_bigquery()
