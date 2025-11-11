import time
import numpy as np
import pandas as pd
import streamlit as st
from dados import gerar_dados
from matriz_custos import gerar_matriz_custos
from frente_2_bnb import rodar_branch_and_bound
import folium
from streamlit_folium import st_folium

gerar_dados()
gerar_matriz_custos()

# --- Configuração da Página ---
st.set_page_config(layout="wide", page_title="Otimizador de Rotas (B&B)")

st.title("PROJETO: Sistema de Otimização com Branch and Bound")
st.write(
    "Projeto da disciplina de Pesquisa Operacional para resolver o Problema do Caixeiro Viajante (TSP) em rotas aéreas."
)

# --- DADOS: Carregar a matriz de custos ---
@st.cache_data
def carregar_dados():
    try:
        matriz = pd.read_csv("matriz_custos.csv", index_col=0)
        matriz = matriz.replace("inf", np.inf)
        matriz = matriz.astype(float)
        return matriz
    except FileNotFoundError:
        return None

# --- FUNÇÃO PARA CARREGAR COORDENADAS ---
@st.cache_data
def carregar_coordenadas():
    """
    Carrega o 'airports.csv' e cria um dicionário
    mapeando IATA -> [latitude, longitude]
    """
    try:
        df_airports = pd.read_csv("datasets/airport.csv")
    
        df_coords = df_airports[["iata", "latitude", "longitude"]].dropna()
        
        # Criar um dicionário para lookup rápido: {'ATL': [33.6, -84.4]}
        coord_dict = df_coords.set_index("iata").T.to_dict('list')
        return coord_dict
    except FileNotFoundError:
        st.error("Arquivo 'datasets/airports.csv' não encontrado.")
        return {}
    except Exception as e:
        st.error(f"Erro ao ler 'airports.csv': {e}")
        return {}


def rodar_vizinho_mais_proximo(matriz_custos, aeroporto_inicio):
    """
    Executa a heurística do Vizinho Mais Próximo (Nearest Neighbor).
    """
    start_time = time.time()
    
    aeroportos = matriz_custos.index.tolist()
    lookup = {nome: i for i, nome in enumerate(aeroportos)}
    matriz = matriz_custos.to_numpy()
    N = len(aeroportos)
    
    start_idx = lookup[aeroporto_inicio]
    
    rota_indices = [start_idx]
    rota_nomes = [aeroporto_inicio]
    custo_total = 0
    
    visitados = np.zeros(N, dtype=bool)
    visitados[start_idx] = True
    
    atual_idx = start_idx
    
    for _ in range(N - 1):
        custos_vizinhos = matriz[atual_idx, :].copy()
        custos_vizinhos[visitados] = np.inf
        
        proximo_idx = np.argmin(custos_vizinhos)
        
        custo_ida = custos_vizinhos[proximo_idx]
        if custo_ida == np.inf:
            return {
                "custo": np.inf,
                "rota": " -> ".join(rota_nomes) + " -> [Rota incompleta]",
                "tempo_execucao": time.time() - start_time
            }
        
        custo_total += custo_ida
        rota_indices.append(proximo_idx)
        rota_nomes.append(aeroportos[proximo_idx])
        visitados[proximo_idx] = True
        atual_idx = proximo_idx

    custo_retorno = matriz[atual_idx, start_idx]
    if custo_retorno == np.inf:
        custo_total = np.inf
        rota_nomes.append(f"[{aeroporto_inicio} - RETORNO IMPOSSÍVEL]")
    else:
        custo_total += custo_retorno
        rota_nomes.append(aeroporto_inicio)

    tempo_total = time.time() - start_time
    return {
        "custo": custo_total,
        "rota": " -> ".join(rota_nomes),
        "tempo_execucao": tempo_total
    }

matriz_custos = carregar_dados()
COORDENADAS = carregar_coordenadas()


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
        st.subheader("Matriz de Custos (em KM)")
        st.write(
            "Esta tabela mostra o custo (Distância em KM) de ir do aeroporto de Origem (linhas) para o Destino (colunas). `inf` significa que não há rota direta."
        )
        # Mostra a matriz com formatação (arredondada)
        st.dataframe(matriz_custos.round(1))

        st.subheader("Gráficos Exploratórios (EDA)")
        st.write(
            "Estes são os gráficos gerados pela (`dados.py`) que justificam a escolha dos dados."
        )
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

        budget_inicial = st.number_input(
            "Budget Máximo (KM):", 
            min_value=0.0, 
            value=500000.0,
            format="%.0f",
            help="Defina um teto de custo inicial. O B&B podará rotas que excedam isso."
        )

        submitted = st.form_submit_button("▶️ Rodar Algoritmo B&B")

    if submitted:
        st.info(
            f"Executando B&B e Heurística... (Iniciando em: {aeroporto_inicio}, Busca: {tipo_busca}, Limite: {tempo_limite}s, Budget: {budget_inicial}km)"
        )
        with st.spinner("Calculando melhor rota... Isso pode demorar."):
            resultado_bnb = rodar_branch_and_bound(
                matriz_custos, aeroporto_inicio, tipo_busca, tempo_limite, budget_inicial
            )
            
            resultado_heuristica = rodar_vizinho_mais_proximo(
                matriz_custos, aeroporto_inicio
            )

        st.success("Execução concluída!")
        
        if 'nos_explorados' in resultado_bnb:
            st.write(f"Nós explorados (B&B): {resultado_bnb['nos_explorados']}")
            
        st.write(f"Tempo B&B: {resultado_bnb['tempo_execucao']:.4f}s | Tempo Heurística: {resultado_heuristica['tempo_execucao']:.4f}s")
        st.write("Os resultados estão disponíveis na Aba 3.")
        st.session_state['resultado_bnb'] = resultado_bnb
        st.session_state['resultado_heuristica'] = resultado_heuristica


# =============================================================================
# ABA 3: Dashboard de Resultados (Item 4.4)
# =============================================================================
with tab3:
    st.header("Resultados da Otimização")

    st.info(
        "Esta aba mostrará a solução ótima encontrada pelo B&B e a comparará com a heurística simples (Frente 4)."
    )
    st.subheader("Solução Final Encontrada")

    col1, col2 = st.columns(2)

    # --- Coluna da Solução B&B (DADOS REAIS DA ABA 2) ---
    with col1:
        st.markdown("### 🏆 Branch and Bound (Ótimo)")
        
        if 'resultado_bnb' in st.session_state:
            res_bnb = st.session_state['resultado_bnb']
            
            # Arredonda o custo para 2 casas decimais se não for 'inf'
            custo_formatado = f"{res_bnb['custo']:.2f} km" if res_bnb['custo'] != np.inf else "inf"
            
            st.metric("Custo Total (Distância)", custo_formatado)
            st.write("**Rota:**")
            st.code(res_bnb['rota']) # Rota REAL
        else:
            st.warning("Execute o algoritmo na 'Aba 2' para ver os resultados.")
            st.metric("Custo Total (Distância)", "-")
            st.code("N/A")

    # --- Coluna da Solução Heurística (FRENTE 4) ---
    with col2:
        st.markdown("### 🏃‍♂️ Heurística Gulosa (Vizinho Próximo)")
        
        if 'resultado_heuristica' in st.session_state:
            res_heu = st.session_state['resultado_heuristica']
            custo_formatado_heu = f"{res_heu['custo']:.2f} km" if res_heu['custo'] != np.inf else "inf"
            
            st.metric("Custo Total (Distância)", custo_formatado_heu)
            st.write("**Rota:**")
            st.code(res_heu['rota'])
        else:
            st.metric("Custo Total (Distância)", "Aguardando...")
            st.write("**Rota:**")
            st.code("Aguardando...")

    st.subheader("Comparação de Desempenho")
    
    # --- INÍCIO DA MODIFICAÇÃO (Gráfico) ---
    if 'resultado_bnb' in st.session_state and 'resultado_heuristica' in st.session_state:
        res_bnb = st.session_state['resultado_bnb']
        res_heu = st.session_state['resultado_heuristica']
        
        custo_bnb = res_bnb.get('custo', 0)
        custo_heu = res_heu.get('custo', 0)

        df_comparacao = pd.DataFrame(
            {
                "Algoritmo": ["Branch and Bound", "Heurística Gulosa"],
                "Custo (KM)": [
                    custo_bnb if custo_bnb != np.inf else 0, 
                    custo_heu if custo_heu != np.inf else 0
                ],
            }
        )
        st.bar_chart(df_comparacao.set_index("Algoritmo"))
    
    else:
        # Gráfico placeholder se nada rodou ainda
        df_comparacao = pd.DataFrame(
            { "Algoritmo": ["Branch and Bound", "Heurística Gulosa"], "Custo (KM)": [0, 0] }
        )
        st.bar_chart(df_comparacao.set_index("Algoritmo"))


    st.subheader("Visualização da Rota no Mapa")

    if 'resultado_bnb' in st.session_state:
        res_bnb = st.session_state['resultado_bnb']
        
        if res_bnb['custo'] != np.inf:
            
            lista_iatas = res_bnb['rota'].split(" -> ")
            
            lista_coords = []
            iatas_nao_encontrados = []
            
            for iata in lista_iatas:
                if iata in COORDENADAS:
                    lista_coords.append(COORDENADAS[iata])
                else:
                    iatas_nao_encontrados.append(iata)
            
            if iatas_nao_encontrados:
                st.warning(f"Não foi possível encontrar coordenadas para: {', '.join(iatas_nao_encontrados)}")

            if lista_coords:
                mapa = folium.Map(location=lista_coords[0], zoom_start=3)
                
                for iata, coords in zip(lista_iatas, lista_coords):
                    folium.Marker(
                        location=coords,
                        popup=f"Aeroporto: {iata}",
                        tooltip=iata
                    ).add_to(mapa)
                
                folium.PolyLine(
                    locations=lista_coords,
                    color="red",
                    weight=2,
                    tooltip="Rota Ótima"
                ).add_to(mapa)
                
                st_folium(mapa, width=700, height=400)
        
        else:
            st.info("Não é possível exibir o mapa, pois nenhuma rota foi encontrada (custo infinito).")
    else:
        st.info("Execute o algoritmo na 'Aba 2' para gerar o mapa.")