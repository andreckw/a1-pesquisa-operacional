import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os


if not os.path.exists("graficos"):
    os.mkdir("graficos")

df = pd.read_csv("datasets/routes.csv")

# Segundo o autor do dataset ele usou \N como um caracter para valores nulos, entao esta sendo este caracter sera alterado para nan para exclusao futura
df = df.replace([r"\\N", r"\\n"], value=np.nan, regex=True)

print(f"Valores nulos no DF: \n {df.isnull().sum()}")

# Corrige os nomes das colunas do DF
df.columns = df.columns.str.strip()

# Codeshare tem pouco dado e nao sao uteis por mostrar que TALVEZ foi com outro tipo de tranporte
# Dados nulos sao retirados juntos para nao serem utilizados
df = df.drop(columns=["codeshare"]).dropna()

# Mostra os aeroportos de origem mais utilizados, o principal aeroporto de destino sendo o ATL
df['source airport'].value_counts().head(10).plot(kind='bar')
plt.savefig("graficos/source-airport.png")

# Mostra os aeroportos de destino mais utilizados, o principal aeroporto de destino sendo o ATL
plt.figure()
df['destination apirport'].value_counts().head(10).plot(kind='bar')
plt.savefig("graficos/destination-apirport.png")

# Mostra a distribuição do número de paradas, a maioria das rotas sendo direta
plt.figure()
df['stops'].value_counts().plot(kind='bar')
plt.savefig("graficos/stops.png")

plt.show()

