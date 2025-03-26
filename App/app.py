import streamlit as st
import gdown
import os
import joblib
import pandas as pd
from utils.data_loader import load_and_process_data
from utils.models import predict_matches

# Configuração inicial
st.set_page_config(layout="wide", page_title="Previsão de Jogos")

@st.cache_resource
def load_models():
    """Carrega modelos do Google Drive com cache"""
    if not os.path.exists('modelo_predict_gols.pkl'):
        gdown.download(
            'https://drive.google.com/uc?id=SEU_ID_MODELO_GOLS',
            'modelo_predict_gols.pkl', 
            quiet=False
        )
    
    if not os.path.exists('modelo_predict_winner.pkl'):
        gdown.download(
            'https://drive.google.com/uc?id=SEU_ID_MODELO_WINNER',
            'modelo_predict_winner.pkl',
            quiet=False
        )
    
    return (
        joblib.load('modelo_predict_gols.pkl'),
        joblib.load('modelo_predict_winner.pkl')
    )

def main():
    st.title("🔮 Previsão de Jogos de Futebol")
    
    # Carregar modelos
    with st.spinner("Carregando modelos de previsão..."):
        model_gols, model_winner = load_models()
    
    # Carregar e processar dados
    df_matches = load_and_process_data()
    
    # Fazer previsões
    if st.button("Calcular Previsões"):
        results = predict_matches(df_matches, model_gols, model_winner)
        
        st.subheader("📊 Resultados das Previsões")
        st.dataframe(
            results.style.background_gradient(cmap="Blues"),
            use_container_width=True
        )
        
        st.download_button(
            "Baixar Previsões",
            data=results.to_csv(index=False),
            file_name="previsoes_jogos.csv"
        )

if __name__ == "__main__":
    main()
