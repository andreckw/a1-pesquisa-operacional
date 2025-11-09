Projeto de Pesquisa Operacional: Otimizador de Rotas Aéreas (Branch & Bound)
Este projeto tem como objetivo desenvolver um sistema em Python que utiliza o algoritmo Branch and Bound para resolver um problema de otimização de roteamento (Problema do Caixeiro Viajante - TSP), baseado em um conjunto de dados públicos de rotas aéreas.

Disciplina: Pesquisa Operacional Professor: Tiago Batista Pedra Grupo: [TODO: Adicionar nome dos integrantes]

1. Aquisição e Preparo de Dados (Frente 1)
Esta etapa cobre a seleção, limpeza e transformação dos dados para modelagem.

1.1. Seleção do Dataset
Fonte: OpenFlights - Route Database

Arquivo Utilizado: routes.csv

Descrição: O dataset contém 67.663 rotas de voo entre aeroportos, indicando a companhia aérea, o aeroporto de origem, o aeroporto de destino e o número de paradas.

1.2. Limpeza e Padronização
Para garantir a qualidade dos dados, as seguintes etapas de pré-processamento foram executadas (ver dados.py):

Valores Nulos: O caractere \N foi substituído pelo padrão np.nan para tratamento adequado.

Remoção de Colunas: A coluna codeshare foi removida, pois não era relevante para o problema de roteamento e continha muitos valores ausentes.

Remoção de Linhas: Linhas com dados nulos em colunas essenciais (como source airport id ou stops) foram removidas. Esta ação removeu 914 linhas (aprox. 1,35% do total), preservando a integridade da análise.

Padronização de Nomes: Nomes de colunas foram corrigidos (ex: destination apirport para destination airport) para clareza e padronização do código.

1.3. Mapeamento para um Problema de Otimização
Problema: Foi modelado como um Problema do Caixeiro Viajante (TSP).

Ajuste de Escopo: Para garantir um tempo de execução viável para o B&B, o problema foi reduzido aos Top 10 aeroportos com maior tráfego (identificados na EDA).

Definição do Custo: Como não possuímos distâncias em Km, o "custo" da rota foi derivado da coluna stops:

Custo = (Número de Paradas + 1)

Resultado: Foi gerada uma Matriz de Custos 10x10 (matriz_custos.csv), onde o custo inf (infinito) representa a ausência de rota direta (ou com poucas paradas) entre dois aeroportos no conjunto de dados. Esta matriz é a entrada principal para o algoritmo.

1.4. Análise Exploratória de Dados (EDA)
Os gráficos da análise exploratória (distribuição de paradas, aeroportos mais usados) estão disponíveis na pasta /graficos.

2. Modelagem do Problema (Frente 2)
[TODO: Seção para a Frente 2 preencher]

Variáveis de Decisão: ...

Função Objetivo: ...

Restrições: ...

Hipótese de Relaxação (Bound): ...

3. Implementação do Branch and Bound (Frente 2)
[TODO: Seção para a Frente 2 preencher]

Estrutura do Algoritmo: (Fila de prioridade? Pilha?)

Critérios de Poda: ...

4. Front-End e Dashboards (Frente 3)
[TODO: Seção para a Frente 3 preencher]

Ferramenta: (Streamlit? Dash?)

Dashboards: (Descrição das telas)

5. Evidências e Validação (Frente 4)
[TODO: Seção para a Frente 4 preencher]

Heurística de Comparação: ...

Testes Unitários: ...




Como Executar o Projeto
1. Instalar Dependências
Certifique-se de ter o Python 3.9+ instalado. Recomendamos o uso de um ambiente virtual (venv).

py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

(Ou linux e mac)
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

Gerar a Matriz de Custos
python matriz_custos.py

Executar a Aplicação (Dashboard)
[TODO: Adicionar o comando para rodar o app, ex: streamlit run app.py]
