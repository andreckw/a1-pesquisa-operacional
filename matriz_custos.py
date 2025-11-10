import numpy as np
import pandas as pd
from math import radians, sin, cos, sqrt, atan2

def haversine(lat1, lon1, lat2, lon2):
    """
    Calcula a distância (em km) entre dois pontos (lat/lon) na Terra
    """
    R = 6371  # Raio da Terra em km

    if any(pd.isna([lat1, lon1, lat2, lon2])):
        return np.inf

    dLat = radians(lat2 - lat1)
    dLon = radians(lon2 - lon1)
    lat1 = radians(lat1)
    lat2 = radians(lat2)

    a = sin(dLat / 2)**2 + cos(lat1) * cos(lat2) * sin(dLon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance

def gerar_matriz_custos():
    
    # --- Carregar Datasets ---
    try:
        df_routes = pd.read_csv("datasets/routes.csv")
        # Carregar o novo dataset de aeroportos para pegar coordenadas
        df_airports = pd.read_csv("datasets/airport.csv")
    except FileNotFoundError:
        print("Erro: 'routes.csv' ou 'airport.csv' não encontrados na pasta 'datasets/'.")
        return
    except Exception as e:
        print(f"Erro ao ler os CSVs: {e}")
        return

    df_routes = df_routes.replace([r"\\N", r"\\n"], value=np.nan, regex=True)
    df_routes.columns = df_routes.columns.str.strip()
    df_routes = df_routes.rename(columns={"destination apirport": "destination airport"})
    df_routes = df_routes.drop(columns=["codeshare"])
    df_routes["stops"] = pd.to_numeric(df_routes["stops"], errors="coerce")
    df_routes = df_routes.dropna(subset=["source airport", "destination airport", "stops"])
    df_routes["stops"] = df_routes["stops"].astype(int)

    print("--- Script de Matriz de Custos (Baseado em Distância) ---")

    df_airports_coords = df_airports[["iata", "latitude", "longitude"]].copy()
    df_airports_coords.dropna(inplace=True)
    # Definir o IATA como índice para um 'join' rápido
    df_airports_coords = df_airports_coords.set_index("iata")

    # --- Pegar Top 10 Aeroportos ---
    top_10_aeroportos = (
        df_routes["source airport"].value_counts().head(10).index.tolist()
    )
    print("Top 10 Aeroportos:")
    print(top_10_aeroportos)

    # --- Filtrar Rotas ---
    df_top10 = df_routes[
        df_routes["source airport"].isin(top_10_aeroportos)
        & df_routes["destination airport"].isin(top_10_aeroportos)
    ].copy()

    
    # Pegar lat/lon da ORIGEM
    # (junta 'df_top10' com 'df_airports_coords' usando 'source airport' como chave)
    df_top10 = df_top10.join(
        df_airports_coords, on="source airport"
    )
    
    # Pegar lat/lon do DESTINO
    # (junta novamente, usando 'destination airport' e adicionando um sufixo)
    df_top10 = df_top10.join(
        df_airports_coords, on="destination airport", rsuffix="_dest"
    )
    
    # Remover rotas onde não encontramos as coordenadas (ex: IATA não estava no airports.csv)
    df_top10.dropna(
        subset=["latitude", "longitude", "latitude_dest", "longitude_dest"],
        inplace=True,
    )

    # --- Calcular o Custo Real (Distância) ---
    
    # Criar a coluna 'custo' aplicando a função haversine
    df_top10["custo"] = df_top10.apply(
        lambda row: haversine(
            row["latitude"],
            row["longitude"],
            row["latitude_dest"],
            row["longitude_dest"],
        ),
        axis=1,
    )
    
    # Adicionar uma "penalidade" por paradas (se houver)
    # (Ex: Distância + 5000km de penalidade por 1 parada)
    # Isso torna voos diretos SEMPRE preferíveis
    df_top10["custo"] = df_top10["custo"] + (df_top10["stops"] * 5000)

    # --- Montar a Matriz ---
    custos_minimos = df_top10.groupby(
        ["source airport", "destination airport"]
    )["custo"].min()

    matriz_custos = pd.DataFrame(
        np.inf, index=top_10_aeroportos, columns=top_10_aeroportos
    )

    for (origem, destino), custo in custos_minimos.items():
        if origem in matriz_custos.index and destino in matriz_custos.columns:
             matriz_custos.loc[origem, destino] = custo

    np.fill_diagonal(matriz_custos.values, 0)

    print("\n--- MATRIZ DE CUSTOS (Baseada em KM) ---")
    print(matriz_custos.round(0))

    matriz_custos.to_csv("matriz_custos.csv")
    print("\nMatriz salva em matriz_custos.csv")