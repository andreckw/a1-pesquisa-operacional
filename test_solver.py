# test_solver.py

import pandas as pd
import numpy as np
from frente_2_bnb import rodar_branch_and_bound

def criar_matriz_teste():
    """
    Cria uma matriz de custos 4x4 simples para teste.
    
    A -> B -> D -> C -> A: 10 + 25 + 30 + 15 = 80
    A -> C -> D -> B -> A: 15 + 30 + 25 + 10 = 80
    
    Custo ótimo esperado: 80
    """
    aeroportos = ['A', 'B', 'C', 'D']
    
    custos_np = np.array([
        [np.inf, 10, 15, 20],  # Custos saindo de A
        [10, np.inf, 35, 25],  # Custos saindo de B
        [15, 35, np.inf, 30],  # Custos saindo de C
        [20, 25, 30, np.inf]   # Custos saindo de D
    ])
    
    # Converte para DataFrame do pandas com índices e colunas nomeados
    matriz_custos_df = pd.DataFrame(custos_np, index=aeroportos, columns=aeroportos)
    return matriz_custos_df

def testar_solver(matriz_custos, aeroporto_inicio, tipo_busca, tempo_limite):
    """
    Função auxiliar para executar o solver e imprimir os resultados de forma organizada.
    """
    print(f"--- Iniciando Teste ---")
    print(f"  Tipo de Busca: {tipo_busca}")
    print(f"  Aeroporto Inicial: {aeroporto_inicio}")
    print(f"  Tempo Limite: {tempo_limite}s")
    print("  Matriz de Custos:")
    print(matriz_custos)
    print("-" * 25)

    # Chama a função principal do seu arquivo
    resultado = rodar_branch_and_bound(
        matriz_custos=matriz_custos,
        aeroporto_inicio=aeroporto_inicio,
        tipo_busca=tipo_busca,
        tempo_limite=tempo_limite
    )

    # Imprime os resultados formatados
    print("Resultado Final:")
    print(f"  Custo: {resultado['custo']}")
    print(f"  Rota: {resultado['rota']}")
    print(f"  Nós Explorados: {resultado['nos_explorados']}")
    print(f"  Tempo de Execução: {resultado['tempo_execucao']:.6f}s")
    print("=" * 25 + "\n")
    return resultado

if __name__ == "__main__":
    # 1. Criar os dados de teste
    matriz_teste = criar_matriz_teste()
    
    # 2. Definir parâmetros comuns
    aeroporto_inicial = 'A'
    limite_tempo = 10  # 10 segundos

    # 3. Executar o teste para cada tipo de busca
    # Teste 1: Profundidade (DFS)
    testar_solver(matriz_teste, aeroporto_inicial, "Profundidade (DFS)", limite_tempo)

    # Teste 2: Largura (BFS)
    testar_solver(matriz_teste, aeroporto_inicial, "Largura (BFS)", limite_tempo)

    # Teste 3: Melhor-Primeiro (Best-First)
    testar_solver(matriz_teste, aeroporto_inicial, "Melhor-Primeiro (Best-First)", limite_tempo)
    
    # Teste 4: Começando de um aeroporto diferente
    print("Testando com aeroporto inicial 'C'...")
    testar_solver(matriz_teste, 'C', "Profundidade (DFS)", limite_tempo)