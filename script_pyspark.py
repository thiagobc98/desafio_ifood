from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date
from pyspark.sql.functions import regexp_replace
from pyspark.sql.functions import to_date, date_format
import requests
import json
import dotenv
import os

# 🔹 Carregar variáveis de ambiente
dotenv.load_dotenv()

# 🔹 Criar sessão do Spark
spark = SparkSession.builder.appName("GitHubFollowers").config("spark.sql.execution.arrow.pyspark.enabled", "true") \
    .config("spark.driver.memory", "4g") \
    .config("spark.executor.memory", "4g") \
    .config("spark.sql.shuffle.partitions", "8") \
    .config("spark.python.worker.memory", "4g").getOrCreate()

# 🔹 Carregar token do GitHub
TOKEN = os.getenv("token_git")
HEADERS = {"Authorization": f"token {TOKEN}"}

def obter_seguidores(username):
    """Obtém a lista de seguidores de um usuário do GitHub."""
    url_followers = f"https://api.github.com/users/{username}/followers"
    response = requests.get(url_followers, headers=HEADERS)
    
    if response.status_code == 200:
        followers = response.json()
        print(f"🔹 {len(followers)} seguidores encontrados para {username}\n")
        return followers
    else:
        print(f"Erro ao buscar seguidores: {response.status_code}")
        return []

def obter_detalhes_seguidores(followers):
    """Obtém detalhes dos seguidores a partir da API."""
    followers_data = []
    
    for follower in followers:
        follower_url = follower["url"]  # URL do perfil do seguidor
        response_follower = requests.get(follower_url, headers=HEADERS)

        
        if response_follower.status_code == 200:
            print('Conectado!')
            data = response_follower.json()
            followers_data.append({
                "Nome": data.get("name", "Não informado"),
                "Username": data.get("login", "Não informado"),
                "Empresa": data.get("company", "Não informado"),
                "Blog": data.get("blog", "Não informado"),
                "Email": data.get("email", "Não informado"),
                "Biografia": data.get("bio", "Não informado"),
                "Repositórios_Publicos": data.get("public_repos"),
                "Seguidores": data.get("followers"),
                "Seguindo": data.get("following"),
                "Criado_em": data.get("created_at"),
            })
            print(data)
        else:
            print(f"Erro ao buscar detalhes de {follower['login']}")
    
    return followers_data

def salvar_dados(df, filename="github_followers.parquet"):
    """Salva os dados no formato Parquet."""
    df.write.mode("overwrite").parquet(filename)
    print(f"\n✅ Dados salvos em '{filename}'!")

def main():
    username = 'marciocl'
    if not username:
        return
    
    followers = obter_seguidores(username)
    if not followers:
        return
    
    followers_data = obter_detalhes_seguidores(followers)
    
    # 🔹 Criar DataFrame do PySpark
    df = spark.createDataFrame(followers_data)

    # # # 🔹 Processamento de dados
    df = df.withColumn("Empresa", regexp_replace(df["Empresa"], "^@", ""))
    df = df.withColumn("Criado_em", date_format(to_date(col("Criado_em"), "yyyy-MM-dd'T'HH:mm:ss'Z'"), "dd/MM/yyyy"))


    #🔹 Mostrar alguns dados
    df.show()
    return df

if __name__ == "__main__":
    df = main()
