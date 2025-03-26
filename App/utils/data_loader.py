import pandas as pd
import requests
from io import StringIO

def download_football_data(urls):
    """Baixa dados de múltiplas fontes"""
    all_data = []
    for league_name, league_urls in urls.items():
        for url in league_urls:
            try:
                response = requests.get(url)
                df = pd.read_csv(StringIO(response.text))
                df['League'] = league_name
                all_data.append(df)
            except Exception as e:
                print(f"Erro ao baixar {url}: {str(e)}")
    return pd.concat(all_data) if all_data else pd.DataFrame()

def load_match_data():
    """Carrega todos os dados necessários"""
    # URLs originais (manter seu dicionário)
    urls = {...} 
    
    # Carregar dados históricos
    historical_data = download_football_data(urls)
    
    # Carregar jogos do dia
    fixtures = pd.read_csv("https://www.football-data.co.uk/fixtures.csv")
    
    # Carregar dicionários
    league_dict = pd.read_csv("assets/ligas_dicionario.csv")
    team_dict = pd.read_csv("assets/times_dicionario.csv")
    
    return {
        'historical': historical_data,
        'fixtures': fixtures,
        'league_dict': league_dict,
        'team_dict': team_dict
    }
