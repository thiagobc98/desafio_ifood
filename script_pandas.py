from pyspark.sql import SparkSession
import requests
import json
import dotenv
import os
import pandas as pd

dotenv.load_dotenv()

# Carregar token do ambiente
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
            data = response_follower.json()
            followers_data.append({
                "Nome": data.get("name", "Não informado"),
                "Username": data.get("login", "Não informado"),
                "Empresa": data.get("company", "Não informado"),
                "Blog": data.get("blog", "Não informado"),
                "Email": data.get("email", "Não informado"),
                "Biografia": data.get("bio", "Não informado"),
                "Repositórios Públicos": data.get("public_repos"),
                "Seguidores": data.get("followers"),
                "Seguindo": data.get("following"),
                "Criado em": data.get("created_at"),
            })
        else:
            print(f"Erro ao buscar detalhes de {follower['login']}")
    
    return followers_data

def salvar_dados(df, filename="github_followers.csv"):
    """Salva os dados em CSV."""
    df.to_csv(filename, index=False)
    print(f"\n✅ Dados salvos em '{filename}'!")

def main():
    username = 'marciocl'
    if not username:
        return
    
    followers = obter_seguidores(username)
    if not followers:
        return
    
    followers_data = obter_detalhes_seguidores(followers)
    df = pd.DataFrame(followers_data)
    
    # Processamento de dados
    df["Empresa"] = df["Empresa"].str.lstrip("@")
    df["Criado em"] = pd.to_datetime(df["Criado em"]).dt.strftime("%d/%m/%Y")
    
    salvar_dados(df)

if __name__ == "__main__":
    main()
