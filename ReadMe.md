# Projeto de Pesquisa Operacional: Otimizador de Rotas Aéreas (Branch & Bound)

Este projeto tem como objetivo desenvolver um sistema em Python que utiliza o algoritmo Branch and Bound para resolver um problema de otimização de roteamento (Problema do Caixeiro Viajante - TSP), baseado em um conjunto de dados públicos de rotas aéreas.

**Disciplina:** Pesquisa Operacional
**Professor:** Tiago Batista Pedra
**Grupo:** [TODO: Adicionar nome dos integrantes]

---

## 1. Aquisição e Preparo de Dados (Frente 1)

Esta etapa cobre a seleção, limpeza e transformação dos dados para modelagem.

### 1.1. Seleção dos Datasets

* **Fonte:** [OpenFlights - Route Database](https://openflights.org/data.html), [Kaggle - Global Aiports](https://www.kaggle.com/datasets/maroofabdullah/airports-csv/data)
* **Arquivos Utilizados:**
    1.  `routes.csv`: Contém 67.663 rotas de voo, indicando aeroporto de origem (IATA) e destino (IATA).
    2.  `airports.csv`: Contém 7.658 aeroportos com seus dados, incluindo código IATA, latitude e longitude.

### 1.2. Limpeza e Padronização

O pré-processamento foi executado (ver `dados.py` e `matriz_custos.py`):

* **Valores Nulos:** O caractere `\N` foi substituído pelo padrão `np.nan`.
* **Remoção de Colunas:** A coluna `codeshare` foi removida.
* **Remoção de Linhas:** Linhas com dados nulos em colunas essenciais (IATA, latitude, longitude, stops) foram removidas.
* **Padronização de Nomes:** Nomes de colunas foram corrigidos (ex: `destination apirport` para `destination airport`) para clareza e padronização.

### 1.3. Mapeamento para um Problema de Otimização (TSP)

O problema foi modelado como um **Problema do Caixeiro Viajante (TSP)**.

* **Ajuste de Escopo:** Para garantir um tempo de execução viável para o B&B, o problema foi reduzido aos **Top 10 aeroportos** com maior tráfego. (Este valor é configurável no script `matriz_custos.py`).

* **Definição do Custo (Distância Real):** O "custo" da rota é a distância real (em Km) entre os aeroportos, calculada usando a **fórmula de Haversine**.
    1.  O script `matriz_custos.py` cruza os dados de `routes.csv` e `airports.csv`.
    2.  Ele une as rotas (ex: `ATL -> DFW`) com as coordenadas de latitude/longitude de ambos os aeroportos.
    3.  A distância (custo) é calculada.
    4.  Uma **penalidade de 5000 km** é adicionada para cada parada (`stops > 0`), tornando voos diretos sempre preferíveis.

* **Resultado:** Foi gerada uma **Matriz de Custos 10x10** (`matriz_custos.csv`), onde o custo é a distância em KM e `inf` (infinito) representa a ausência de rota direta entre dois aeroportos. Esta matriz é a entrada principal para o algoritmo.

### 1.4. Análise Exploratória de Dados (EDA)

Os gráficos da análise exploratória (distribuição de paradas, aeroportos mais usados) são gerados pelo `dados.py` e salvos na pasta `/graficos`.

---

## 2. Modelagem Matemática (Frente 2)

O problema pode ser formulado matematicamente como uma Programação Inteira.

#### Variáveis de Decisão

Seja $C_{ij}$ o custo (distância) de ir do aeroporto $i$ para o aeroporto $j$, conforme definido na `matriz_custos.csv`.

Criamos uma variável de decisão binária $x_{ij}$ para cada par de aeroportos:

$$
x_{ij} = \begin{cases} 1 & \text{se a rota ótima vai do aeroporto } i \text{ para o } j \\ 0 & \text{caso contrário} \end{cases}
$$

#### Função Objetivo (FO)

Nosso objetivo é **minimizar** o custo total da viagem (distância em KM).

$$
\text{Minimizar } Z = \sum_{i=1}^{N} \sum_{j=1}^{N} C_{ij} \cdot x_{ij}
$$

#### Restrições

1.  **Sair de cada aeroporto 1 vez:**
    $$
    \sum_{j=1, j \neq i}^{N} x_{ij} = 1 \quad (\text{para todo } i = 1, ..., N)
    $$

2.  **Chegar em cada aeroporto 1 vez:**
    $$
    \sum_{i=1, i \neq j}^{N} x_{ij} = 1 \quad (\text{para todo } j = 1, ..., N)
    $$

3.  **Eliminação de Sub-tours:** Garantia de que a solução seja um único tour. Esta restrição é implementada implicitamente pela lógica de busca do nosso algoritmo.

---

## 3. Implementação do Branch and Bound (Frente 2)

O algoritmo B&B foi programado em Python (ver `frente_2_bnb.py`) e implementa uma busca em árvore para encontrar a solução ótima.

* **Estrutura do Algoritmo:** O `TspSolver` é uma classe que encapsula o estado da busca. A lógica central é implementada de três formas (selecionáveis na interface):
    1.  **Profundidade (DFS):** Uma função recursiva que usa a pilha de chamadas (eficiente em memória e padrão do projeto).
    2.  **Largura (BFS):** Usa uma `deque` (fila) para explorar nível a nível (ineficiente em memória, mas implementado).
    3.  **Melhor-Primeiro (Best-First):** Usa uma `heapq` (fila de prioridade) para explorar o nó de menor custo parcial (não-admissível, mas implementado).

* **Lógica do Bound (Poda):** A eficiência do B&B vem de "podar" galhos da árvore que não podem conter a solução ótima. Nossos critérios de poda são:
    1.  **Poda por Limite (Bound):** `if custo_parcial >= melhor_custo_global:`. Se o custo do caminho *parcial* já é pior que a melhor rota *completa* encontrada, o ramo é descartado.
    2.  **Poda por Inviabilidade:** `if custo_ida == np.inf:`. O algoritmo descarta rotas que são impossíveis (custo infinito).
    3.  **Poda por Tempo Limite:** `if time.time() - start_time > tempo_limite:`. A busca é interrompida após o tempo limite (ex: 60s) e retorna a melhor solução encontrada *até aquele momento*.

---

## 4. Front-End e Dashboards (Frente 3)

A interface do usuário foi desenvolvida com **Streamlit**, permitindo interatividade e visualização de dados. O app é estruturado em três "páginas" (usando `streamlit-option-menu` para a navegação).

* **Página 1: Análise Exploratória:**
    * Exibe os gráficos da EDA (Top 10 aeroportos, distribuição de paradas).
    * Apresenta a `matriz_custos.csv` final (em KM) em um `st.dataframe` interativo.

* **Página 2: Executar Algoritmo:**
    * Contém o "Painel de Controle". O usuário pode selecionar:
        * Aeroporto de Início (lido dinamicamente da matriz).
        * Tipo de Busca (DFS, BFS, Best-First).
        * Tempo Limite (em segundos).
    * Ao clicar em "Rodar", a função B&B é executada e o resultado é salvo no `st.session_state`.

* **Página 3: Resultados:**
    * Exibe os cartões (`st.metric`) com o **Custo Total (em KM)** e a **Rota Ótima** encontrada.
    * Contém o espaço reservado para a Heurística da Frente 4 (para comparação).
    * Renderiza um **mapa interativo (Folium)** que desenha a rota ótima no globo, com marcadores para cada aeroporto.

---

## 5. Evidências e Validação (Frente 4)

`[TODO: Esta seção será preenchida pela Frente 4]`

* **Heurística de Comparação:** (Implementar um algoritmo guloso, ex: Vizinho Mais Próximo)
* **Testes Unitários:** (Criar testes para a classe `TspSolver`)
* **Análise de Resultados:** (Comparar o Custo/Tempo do B&B vs. Heurística)

---

## Como Executar o Projeto

1.  **Clonar o Repositório:**
    ```bash
    git clone [URL_DO_SEU_REPOSITORIO]
    cd [NOME_DA_PASTA]
    ```

2.  **Instalar Dependências:**
    (Recomendamos o uso de um ambiente virtual)
    ```bash
    # Criar ambiente virtual (opcional)
    python -m venv .venv
    
    # Ativar ambiente
    # Windows: .\.venv\Scripts\activate
    # Linux/Mac: source .venv/bin/activate
    
    # Instalar bibliotecas
    pip install streamlit pandas numpy matplotlib folium streamlit-folium streamlit-option-menu
    ```
    *(Alternativamente, crie um arquivo `requirements.txt` com esses nomes e rode `pip install -r requirements.txt`)*

3.  **Gerar os Dados (Execução ÚNICA):**
    Estes scripts só precisam ser rodados uma vez para gerar os arquivos de análise. **Não** os chame de dentro do `main.py`.
    ```bash
    # Gera os gráficos da EDA
    python dados.py
    
    # Gera o arquivo matriz_custos.csv (com base no airports.csv)
    python matriz_custos.py
    ```

4.  **Executar a Aplicação (Dashboard):**
    ```bash
    streamlit run main.py
    ```
    Abra o endereço `http://localhost:8501` no seu navegador.