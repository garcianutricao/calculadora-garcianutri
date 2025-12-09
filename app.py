import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Calculadora de Substituição", page_icon="🧮")

# --- CARREGAMENTO ---
pasta_atual = os.path.dirname(os.path.abspath(__file__))
caminho_excel = os.path.join(pasta_atual, "tabela_alimentos.xlsx")

@st.cache_data
def carregar_dados():
    return pd.read_excel(caminho_excel)

try:
    df = carregar_dados()
except FileNotFoundError:
    st.error("❌ Arquivo não encontrado! Verifique o nome do arquivo Excel.")
    st.stop()

# --- MAPA DE COLUNAS ---
colunas_necessarias = ['Alimento', 'Grupo', 'Kcal'] 
mapa_colunas = {
    'Alimento': 'Alimento',
    'Grupo': 'Grupo',
    'Kcal': 'Kcal',
    'Carbo': 'Carbo',
    'Prot': 'Prot',
    'Gord': 'Gord'
}

# --- INTERFACE ---
st.title("🧮 Calculadora de Troca - Garcia Nutrição")
st.markdown("---")

# Filtro de Grupo
grupos = df[mapa_colunas['Grupo']].dropna().unique()
grupo_selecionado = st.selectbox("Selecione o Grupo Alimentar:", grupos)

# Filtra o dataframe pelo grupo
df_grupo = df[df[mapa_colunas['Grupo']] == grupo_selecionado]

st.markdown("---")

# --- ÁREA DE CÁLCULO (2 COLUNAS) ---
col1, col_seta, col2 = st.columns([1, 0.2, 1])

# --- COLUNA 1: O QUE EU TENHO ---
with col1:
    st.subheader("1. Tenho na dieta:")
    alimento_base = st.selectbox(
        "Alimento Atual:", 
        df_grupo[mapa_colunas['Alimento']].unique(),
        key="base"
    )
    # Alterado para int (inteiro) e step=10 (inteiro) para evitar decimais na entrada
    qtd_base = st.number_input(
        f"Quantidade (g):", 
        value=100, 
        step=10, 
        format="%d"
    )

    # Pega dados da base
    dados_base = df_grupo[df_grupo[mapa_colunas['Alimento']] == alimento_base].iloc[0]
    kcal_base_100g = float(dados_base[mapa_colunas['Kcal']])
    total_kcal = (kcal_base_100g / 100) * qtd_base
    
    st.caption(f"Total: {int(total_kcal)} kcal")

# --- Seta visual no meio ---
with col_seta:
    st.markdown("<br><br><div style='text-align: center; font-size: 30px;'>➡️</div>", unsafe_allow_html=True)

# --- COLUNA 2: PELO QUE VOU TROCAR ---
with col2:
    st.subheader("2. Quero comer:")
    
    lista_substitutos = df_grupo[df_grupo[mapa_colunas['Alimento']] != alimento_base]
    
    alimento_alvo = st.selectbox(
        "Novo Alimento:", 
        lista_substitutos[mapa_colunas['Alimento']].unique(),
        key="alvo"
    )

    dados_alvo = df_grupo[df_grupo[mapa_colunas['Alimento']] == alimento_alvo].iloc[0]
    kcal_alvo_100g = float(dados_alvo[mapa_colunas['Kcal']])

# --- RESULTADO EM DESTAQUE ---
st.markdown("---")

if kcal_alvo_100g > 0:
    # CÁLCULO FINAL
    qtd_final = (total_kcal / kcal_alvo_100g) * 100
    
    st.success("✅ **Cálculo de Equivalência Realizado:**")
    
    # --- AQUI ESTÁ A MUDANÇA PRINCIPAL DE FONTE ---
    # Usando HTML puro para controlar o tamanho exato da fonte
    st.markdown(f"""
        <div style="text-align: center; padding: 10px; border-radius: 10px; background-color: #424345;">
            <p style="font-size: 24px; font-weight: bold; margin-bottom: 5px;">Quantidade de {alimento_alvo}:</p>
            <p style="font-size: 60px; font-weight: bold; color: #2e7d32; margin: 0;">{int(qtd_final)} g</p>
            <p style="font-size: 16px; color: white; margin-top: 5px;">(Equivale a {int(qtd_base)}g de {alimento_base})</p>
        </div>
    """, unsafe_allow_html=True)

else:
    st.error("Erro: O alimento selecionado parece ter 0 kcal.")

# --- TABELA COMPARATIVA ---
st.markdown("### 📊 Comparação Nutricional")

# Função auxiliar para evitar repetição de código e garantir inteiros
def calc_macro(dados, macro_key, qtd):
    valor_por_100 = dados.get(macro_key, 0)
    return int((valor_por_100 / 100) * qtd)

comparacao = pd.DataFrame({
    "Nutriente": ["Calorias (kcal)", "Carboidratos (g)", "Proteínas (g)", "Gorduras (g)"],
    f"{alimento_base} ({int(qtd_base)}g)": [
        int(total_kcal), 
        calc_macro(dados_base, 'Carbo', qtd_base),
        calc_macro(dados_base, 'Prot', qtd_base),
        calc_macro(dados_base, 'Gord', qtd_base)
    ],
    f"{alimento_alvo} ({int(qtd_final)}g)": [
        int((kcal_alvo_100g/100)*qtd_final),
        calc_macro(dados_alvo, 'Carbo', qtd_final),
        calc_macro(dados_alvo, 'Prot', qtd_final),
        calc_macro(dados_alvo, 'Gord', qtd_final)
    ]
})

st.table(comparacao.set_index("Nutriente"))