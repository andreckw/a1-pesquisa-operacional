import time  # Usado para simular o progresso do algoritmo

import numpy as np
import pandas as pd
import streamlit as st

from dados import gerar_dados
from matriz_custos import gerar_matriz_custos

gerar_dados()
gerar_matriz_custos()

# --- Configuração da Página ---
st.set_page_config(layout="wide", page_title="Otimizador de Rotas (B&B)")

st.title("PROJETO: Sistema de Otimização com Branch and Bound")
st.write(
    "Projeto da disciplina de Pesquisa Operacional para resolver o Problema do Caixeiro Viajante (TSP) em rotas aéreas."
)


# --- DADOS: Carregar a matriz de custos ---
# Esta é a principal entrada para o seu app.
@st.cache_data
def carregar_dados():
    try:
        # Usamos index_col=0 para que a primeira coluna (com os nomes dos aeroportos)
        # seja usada como o índice do DataFrame.
        matriz = pd.read_csv("matriz_custos.csv", index_col=0)
        # Substitui 'inf' (que o pandas lê como string aqui) por um valor numérico (Numpy.inf)
        matriz = matriz.replace("inf", np.inf)
        return matriz
    except FileNotFoundError:
        return None


matriz_custos = carregar_dados()

# --- DEFINIÇÃO DAS ABAS ---
tab1, tab2, tab3 = st.tabs(
    [
        "1. Análise Exploratória",
        "2. Executar Algoritmo",
        "3. Resultados",
    ]
)


# =============================================================================
# ABA 1: Dashboard de Análise de Dados (Item 4.2)
# =============================================================================
with tab1:
    st.header("Análise Exploratória dos Dados de Rotas")

    if matriz_custos is None:
        st.error(
            "Erro: Arquivo `matriz_custos.csv` não encontrado. Verifique se ele está na pasta correta."
        )
    else:
        st.subheader("Matriz de Custos (Paradas)")
        st.write(
            "Esta tabela mostra o custo (número de paradas) de ir do aeroporto de Origem (linhas) para o Destino (colunas). `inf` significa que não há rota direta ou com poucas paradas."
        )

        # O st.dataframe já é interativo (filtra, ordena)
        st.dataframe(matriz_custos)

        st.subheader("Gráficos Exploratórios (EDA)")
        st.write(
            "Estes são os gráficos gerados pela (`dados.py`) que justificam a escolha dos dados."
        )

        # Dividir a tela em colunas para os gráficos
        col1, col2 = st.columns(2)

        try:

            col1.image(
                "graficos/source-airport.png",
                caption="Top 10 Aeroportos de Origem",
            )
            col2.image(
                "graficos/stops.png", caption="Distribuição de Paradas (Stops)"
            )
        except FileNotFoundError:
            st.warning(
                "Gráficos (`source-airport.png` ou `stops.png`) não encontrados na pasta `graficos/`. Execute o script `dados.py`."
            )


# =============================================================================
# ABA 2: Dashboard do Algoritmo (Item 4.3)
# =============================================================================
with tab2:
    st.header("Painel de Controle do Algoritmo Branch & Bound")

    with st.form("form_parametros"):
        st.subheader("Parâmetros de Execução")

        # Widgets para os parâmetros
        col1, col2, col3 = st.columns(3)
        aeroporto_inicio = col1.selectbox(
            "Aeroporto de Início:",
            options=(
                matriz_custos.index if matriz_custos is not None else ["ATL"]
            ),
        )
        tipo_busca = col2.selectbox(
            "Tipo de Busca (Estratégia):",
            options=[
                "Profundidade (DFS)",
                "Largura (BFS)",
                "Melhor-Primeiro (Best-First)",
            ],
        )
        tempo_limite = col3.number_input(
            "Tempo Limite (segundos):", min_value=10, max_value=300, value=60
        )

        # O botão que dispara a execução
        submitted = st.form_submit_button("▶️ Rodar Algoritmo B&B")

    if submitted:
        st.info(
            f"Executando B&B... (Iniciando em: {aeroporto_inicio}, Busca: {tipo_busca}, Limite: {tempo_limite}s)"
        )

        #
        # TODO: AQUI É A INTEGRAÇÃO COM A FRENTE 2
        #
        # Quando a Frente 2 criar a função, você vai chamá-la aqui.
        # Exemplo:
        # from frente_2_bnb import rodar_branch_and_bound
        #
        # with st.spinner("Calculando melhor rota... Isso pode demorar."):
        #   resultado_bnb = rodar_branch_and_bound(matriz_custos, aeroporto_inicio, tipo_busca, tempo_limite)
        #

        # Simulação de progresso (REMOVER DEPOIS)
        progress_bar = st.progress(0)
        st.text("Expandindo nós... (Simulação)")
        for i in range(100):
            time.sleep(0.05)
            progress_bar.progress(i + 1)

        st.success("Execução do B&B (simulada) concluída!")
        st.write("Os resultados estão disponíveis na Aba 3.")

        # TODO: Salvar os resultados para a Aba 3 ver
        # st.session_state['resultado_bnb'] = resultado_bnb
        # st.session_state['heuristica'] = resultado_heuristica


# =============================================================================
# ABA 3: Dashboard de Resultados (Item 4.4)
# =============================================================================
with tab3:
    st.header("Resultados da Otimização")

    st.info(
        "Esta aba mostrará a solução ótima encontrada pelo B&B e a comparará com a heurística simples (Frente 4)."
    )

    #
    # TODO: AQUI É A INTEGRAÇÃO COM A FRENTE 4 (e os resultados da 2)
    #
    # Você vai ler os resultados que a Aba 2 salvou no st.session_state
    #

    # Exemplo de como exibir os resultados (usando dados falsos por enquanto):

    st.subheader("Solução Final Encontrada")

    col1, col2 = st.columns(2)

    # --- Coluna da Solução B&B ---
    col1.markdown("### 🏆 Branch and Bound (Ótimo)")
    col1.metric("Custo Total (Paradas)", "12")  # Valor Falso
    col1.write("**Rota:**")
    col1.code("ATL -> ORD -> JFK -> LAX -> ... -> ATL")  # Rota Falsa

    # --- Coluna da Solução Heurística ---
    col2.markdown("### 🏃‍♂️ Heurística Gulosa (Comparação)")
    col2.metric("Custo Total (Paradas)", "15")  # Valor Falso
    col2.write("**Rota:**")
    col2.code("ATL -> DFW -> LAX -> ORD -> ... -> ATL")  # Rota Falsa

    st.subheader("Comparação de Desempenho")

    # Exemplo de gráfico de barras para comparar
    df_comparacao = pd.DataFrame(
        {
            "Algoritmo": ["Branch and Bound", "Heurística Gulosa"],
            "Custo (Paradas)": [12, 15],  # Valores Falsos
        }
    )

    st.bar_chart(df_comparacao.set_index("Algoritmo"))
