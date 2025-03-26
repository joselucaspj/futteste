import pandas as pd
import numpy as np
from scipy.stats import poisson
from utils.match_simulator import simulate_match

def predict_all_matches(data_dict, model_gols, model_winner, n_simulations=10000, last_n_games=5):
    """Executa todas as previsões"""
    fixtures = data_dict['fixtures']
    historical = data_dict['historical']
    
    # Calcular médias de gols
    fixtures = calculate_goal_averages(fixtures, historical, last_n_games)
    
    # Prever gols
    features = [...] # Sua lista original de features
    X = fixtures[features]
    fixtures[['Predicted_Goals_H', 'Predicted_Goals_A']] = model_gols.predict(X)
    
    # Simular partidas
    results = []
    for _, row in fixtures.iterrows():
        match_result = simulate_match_result(row, n_simulations)
        results.append(match_result)
    
    return pd.concat(results)

def calculate_goal_averages(fixtures, historical, n_games):
    """Calcula médias de gols para cada time"""
    
    for col in ['Media_GM_H_HA', 'Media_GS_H_HA', 'Media_GM_A_HA', 'Media_GS_A_HA']:
        fixtures[col] = 0.0
    
    for idx, row in fixtures.iterrows():
            df_equipe_mandante = historical[((historical['Home_Team_ID'] == fixtures[idx, 'Home_Team_ID']) | (historical['Away_Team_ID'] == fixtures[idx, 'Home_Team_ID'])) & (historical['League_ID'] == fixtures[idx, 'League_ID'])].tail(n)
            df_equipe_visitante = historical[((historical['Home_Team_ID'] == fixtures[idx, 'Away_Team_ID']) | (historical['Away_Team_ID'] == fixtures[idx, 'Away_Team_ID'])) & (historical['League_ID'] == fixtures[idx, 'League_ID'])].tail(n)
            #display(df_equipe)
            if df_equipe.shape[0] == 0:
                fixtures[idx, 'Media_GM_H_HA'] = 0
                fixtures[idx, 'Media_GS_H_HA'] = 0
                fixtures[idx, 'Media_GM_A_HA'] = 0
                fixtures[idx, 'Media_GS_A_HA'] = 0
            else:
                fixtures[idx, 'Media_GM_H_HA'] = round((df_equipe_mandante[(df_equipe_mandante['Home_Team_ID'] == fixtures[idx, 'Home_Team_ID'])]['FTHG'].sum() + df_equipe_mandante[(df_equipe_mandante['Away_Team_ID'] == fixtures[idx, 'Home_Team_ID'])]['FTAG'].sum()) / df_equipe_mandante.shape[0], 2)
                fixtures[idx, 'Media_GS_H_HA'] = round((df_equipe_mandante[(df_equipe_mandante['Home_Team_ID'] == fixtures[idx, 'Home_Team_ID'])]['FTAG'].sum() + df_equipe_mandante[(df_equipe_mandante['Away_Team_ID'] == fixtures[idx, 'Home_Team_ID'])]['FTHG'].sum()) / df_equipe_mandante.shape[0], 2)
                fixtures[idx, 'Media_GM_A_HA'] = round((df_equipe_visitante[(df_equipe_visitante['Home_Team_ID'] == fixtures[idx, 'Away_Team_ID'])]['FTHG'].sum() + df_equipe_visitante[(df_equipe_visitante['Away_Team_ID'] == fixtures[idx, 'Away_Team_ID'])]['FTAG'].sum()) / df_equipe_visitante.shape[0], 2)
                fixtures[idx, 'Media_GS_A_HA'] = round((df_equipe_visitante[(df_equipe_visitante['Home_Team_ID'] == fixtures[idx, 'Away_Team_ID'])]['FTAG'].sum() + df_equipe_visitante[(df_equipe_visitante['Away_Team_ID'] == fixtures[idx, 'Away_Team_ID'])]['FTHG'].sum()) / df_equipe_mandante.shape[0], 2)
            
            simulated_results = simulate_match(row['Media_GM_H_HA'], row['Media_GS_H_HA'], row['Media_GM_A_HA'], row['Media_GS_A_HA'])
            simulated_results = drop_reset_index(simulated_results)
        
            results = top_results_df(simulated_results,100)
            results = drop_reset_index(results)
            resultados = contar_resultados(results)
            fixtures.at[idx,'Probabilidade_placar_mandante_media_HA'] = resultados['Probabilidade placares mandante']
            fixtures.at[idx,'Probabilidade_placar_visitante_media_AH'] = resultados['Probabilidade placares visitante']
            fixtures.at[idx,'Probabilidade_placar_empate_media_HA'] = resultados['Probabilidade placares empate']     
            
        pass
    
    return fixtures

def simulate_match_result(row, n_simulations):
    """Simula um único jogo"""
    # Implementar sua lógica original de simulação
    pass

def simulate_match(home_goals_for, home_goals_against, away_goals_for, away_goals_against, num_simulations=10000, random_seed=42):
    np.random.seed(random_seed)
    estimated_home_goals = (home_goals_for + away_goals_against) / 2
    estimated_away_goals = (away_goals_for + home_goals_against) / 2

    home_goals = poisson(estimated_home_goals).rvs(num_simulations)
    away_goals = poisson(estimated_away_goals).rvs(num_simulations)

    results = pd.DataFrame({
        'Home_Goals': home_goals,
        'Away_Goals': away_goals
    })

    return results

def contar_resultados(dataframe):
    vitoria_mandante = 0
    soma_probabilidade_placar_mandante = 0
    vitoria_visitante = 0
    soma_probabilidade_placar_visitante = 0
    empate = 0
    soma_probabilidade_placar_empate = 0

    for indice, linha in dataframe.iterrows():
        if linha['Home_Goals'] > linha['Away_Goals']:
            vitoria_mandante += 1
            soma_probabilidade_placar_mandante = soma_probabilidade_placar_mandante + linha['Probability']
        elif linha['Home_Goals'] < linha['Away_Goals']:
            vitoria_visitante += 1
            soma_probabilidade_placar_visitante = soma_probabilidade_placar_visitante + linha['Probability']
        else:
            empate += 1
            soma_probabilidade_placar_empate = soma_probabilidade_placar_empate + linha['Probability']

    return {'Vitória do Mandante': vitoria_mandante, 'Vitória do Visitante': vitoria_visitante, 'Empate': empate, 'Probabilidade placares mandante': soma_probabilidade_placar_mandante, 'Probabilidade placares visitante': soma_probabilidade_placar_visitante, 'Probabilidade placares empate': soma_probabilidade_placar_empate }

def drop_reset_index(df):
    df = df.dropna()
    df = df.reset_index(drop=True)
    df.index += 1
    return df
def top_results_df(simulated_results, top_n):

    result_counts = simulated_results.value_counts().head(top_n).reset_index()
    result_counts.columns = ['Home_Goals', 'Away_Goals', 'Count']

    sum_top_counts = result_counts['Count'].sum()
    result_counts['Probability'] = result_counts['Count'] / sum_top_counts

    return result_counts
