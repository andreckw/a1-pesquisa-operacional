import numpy as np
import pandas as pd


def gerar_matriz_custos():
    # --- Reutilizando o início do dados.py ---
    df = pd.read_csv("datasets/routes.csv")
    df = df.replace([r"\\N", r"\\n"], value=np.nan, regex=True)
    df.columns = df.columns.str.strip()
    df = df.rename(columns={"destination apirport": "destination airport"})
    df = df.drop(columns=["codeshare"])
    # aqui convertemos 'stops' para número, tratando erros
    df["stops"] = pd.to_numeric(df["stops"], errors="coerce")
    df = df.dropna(subset=["source airport", "destination airport", "stops"])
    # Convertemos stops para inteiro
    df["stops"] = df["stops"].astype(int)

    print("--- Script de Matriz de Custos ---")

    # 1. PEGAR OS TOP 10 AEROPORTOS
    top_10_aeroportos = (
        df["source airport"].value_counts().head(10).index.tolist()
    )

    print("Top 10 Aeroportos:")
    print(top_10_aeroportos)

    # 2. FILTRAR O DATAFRAME
    df_top10 = df[
        df["source airport"].isin(top_10_aeroportos)
        & df["destination airport"].isin(top_10_aeroportos)
    ].copy()

    # 3. VER O RESULTADO DO FILTRO
    print("\nRotas encontradas ENTRE esses Top 10 aeroportos:")
    print(df_top10)

    # 4. DEFINIR O CUSTO (paradas + 1)
    # O custo de um voo com 0 paradas é 1 (o próprio voo)
    # O custo de um voo com 1 parada é 2 (voo A->B + voo B->C)
    df_top10["custo"] = df_top10["stops"] + 1

    # 5. GARANTIR O CUSTO MÍNIMO
    # Pode haver duas rotas de ATL para ORD (uma com 0, outra com 1 parada).
    #  garantir que pegamos SÓ a mais barata (o custo mínimo).
    # e agrupamos por origem/destino e pegamos o menor 'custo' de cada.
    custos_minimos = df_top10.groupby(
        ["source airport", "destination airport"]
    )["custo"].min()

    # 6. CRIAR A MATRIZ DE CUSTOS VAZIA (10x10)
    matriz_custos = pd.DataFrame(
        np.inf, index=top_10_aeroportos, columns=top_10_aeroportos
    )

    # 7. PREENCHER A MATRIZ com os custos mínimos
    for (origem, destino), custo in custos_minimos.items():
        matriz_custos.loc[origem, destino] = custo

    # 8. PREENCHER A DIAGONAL (A->A = 0)
    np.fill_diagonal(matriz_custos.values, 0)

    # 9. EXIBIR A MATRIZ FINAL!
    print("\n--- MATRIZ DE CUSTOS (Pronta para o B&B) ---")
    print(matriz_custos)

    # salvar a matriz para usar depois
    matriz_custos.to_csv("matriz_custos.csv")
    print("\nMatriz salva em matriz_custos.csv")
