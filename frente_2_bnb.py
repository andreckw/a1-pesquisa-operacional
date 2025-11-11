import numpy as np
import time
import heapq
from collections import deque


class TspSolver:
    def __init__(self, matriz_custos, aeroporto_inicio, tipo_busca, tempo_limite, budget_inicial=np.inf):
        self.aeroportos = matriz_custos.index.tolist()
        self.matriz = matriz_custos.to_numpy()
        self.lookup = {nome: i for i, nome in enumerate(self.aeroportos)}
        self.N = len(self.aeroportos)

        self.start_node_idx = self.lookup[aeroporto_inicio]
        self.start_node_nome = aeroporto_inicio
        self.tipo_busca = tipo_busca
        self.tempo_limite = tempo_limite
        self.melhor_custo = budget_inicial

        self.melhor_custo = np.inf
        self.melhor_rota_indices = []
        self.nos_explorados = 0
        self.start_time = time.time()

    def _converter_indices_para_nomes(self, indices):
        return [self.aeroportos[i] for i in indices]

    def _calcular_custo(self, rota_indices):
        custo = 0
        for i in range(len(rota_indices) - 1):
            custo += self.matriz[rota_indices[i], rota_indices[i + 1]]
        return custo

    # =====================================================================
    #  MÉTODO PRINCIPAL DE RESOLUÇÃO
    # =====================================================================
    def resolver(self):
        visitados_iniciais = np.zeros(self.N, dtype=bool)
        visitados_iniciais[self.start_node_idx] = True

        if self.tipo_busca == "Profundidade (DFS)":
            self._rodar_dfs_recursivo(self.start_node_idx, [self.start_node_idx], 0, visitados_iniciais)
        elif self.tipo_busca == "Largura (BFS)":
            self._rodar_bfs()
        elif self.tipo_busca == "Melhor-Primeiro (Best-First)":
            self._rodar_best_first()
        else:
            print("Tipo de busca não reconhecido. Rodando DFS padrão.")
            self._rodar_dfs_recursivo(self.start_node_idx, [self.start_node_idx], 0, visitados_iniciais)

        tempo_total = time.time() - self.start_time

        if not self.melhor_rota_indices:
            return {
                "custo": np.inf,
                "rota": f"Nenhuma rota completa encontrada partindo de {self.start_node_nome}",
                "tempo_execucao": tempo_total,
                "nos_explorados": self.nos_explorados
            }

        rota_nomes = self._converter_indices_para_nomes(self.melhor_rota_indices)
        return {
            "custo": self.melhor_custo,
            "rota": " -> ".join(rota_nomes),
            "tempo_execucao": tempo_total,
            "nos_explorados": self.nos_explorados
        }

    # =====================================================================
    # DFS (PROFUNDIDADE)
    # =====================================================================
    def _rodar_dfs_recursivo(self, u, rota_parcial_indices, custo_parcial, visitados_mask):
        self.nos_explorados += 1

        if custo_parcial >= self.melhor_custo:
            return
        if (time.time() - self.start_time) > self.tempo_limite:
            return

        if len(rota_parcial_indices) == self.N:
            custo_retorno = self.matriz[u, self.start_node_idx]
            if custo_retorno != np.inf:
                custo_final = custo_parcial + custo_retorno
                if custo_final < self.melhor_custo:
                    self.melhor_custo = custo_final
                    self.melhor_rota_indices = rota_parcial_indices + [self.start_node_idx]
            return

        for v in range(self.N):
            if not visitados_mask[v] and self.matriz[u, v] != np.inf:
                visitados_mask[v] = True
                self._rodar_dfs_recursivo(v, rota_parcial_indices + [v], custo_parcial + self.matriz[u, v], visitados_mask)
                visitados_mask[v] = False

    # =====================================================================
    # BFS (LARGURA)
    # =====================================================================
    def _rodar_bfs(self):
        fila = deque()
        visitados_iniciais = np.zeros(self.N, dtype=bool)
        visitados_iniciais[self.start_node_idx] = True
        fila.append((self.start_node_idx, [self.start_node_idx], 0, visitados_iniciais.copy()))

        while fila:
            u, rota, custo, visitados = fila.popleft()
            self.nos_explorados += 1

            if custo >= self.melhor_custo:
                continue
            if (time.time() - self.start_time) > self.tempo_limite:
                break

            if len(rota) == self.N:
                custo_retorno = self.matriz[u, self.start_node_idx]
                if custo_retorno != np.inf:
                    custo_final = custo + custo_retorno
                    if custo_final < self.melhor_custo:
                        self.melhor_custo = custo_final
                        self.melhor_rota_indices = rota + [self.start_node_idx]
                continue

            for v in range(self.N):
                if not visitados[v] and self.matriz[u, v] != np.inf:
                    novo_visitados = visitados.copy()
                    novo_visitados[v] = True
                    fila.append((v, rota + [v], custo + self.matriz[u, v], novo_visitados))

    # =====================================================================
    # BEST-FIRST (MELHOR-PRIMEIRO)
    # =====================================================================
    def _rodar_best_first(self):
        heap = []
        visitados_iniciais = np.zeros(self.N, dtype=bool)
        visitados_iniciais[self.start_node_idx] = True
        heapq.heappush(heap, (0, self.start_node_idx, [self.start_node_idx], visitados_iniciais.copy()))

        while heap:
            custo, u, rota, visitados = heapq.heappop(heap)
            self.nos_explorados += 1

            if custo >= self.melhor_custo:
                continue
            if (time.time() - self.start_time) > self.tempo_limite:
                break

            if len(rota) == self.N:
                custo_retorno = self.matriz[u, self.start_node_idx]
                if custo_retorno != np.inf:
                    custo_final = custo + custo_retorno
                    if custo_final < self.melhor_custo:
                        self.melhor_custo = custo_final
                        self.melhor_rota_indices = rota + [self.start_node_idx]
                continue

            for v in range(self.N):
                if not visitados[v] and self.matriz[u, v] != np.inf:
                    novo_visitados = visitados.copy()
                    novo_visitados[v] = True
                    heapq.heappush(heap, (custo + self.matriz[u, v], v, rota + [v], novo_visitados))

def rodar_branch_and_bound(matriz_custos, aeroporto_inicio, tipo_busca, tempo_limite, budget_inicial=np.inf):
    solver = TspSolver(matriz_custos, aeroporto_inicio, tipo_busca, tempo_limite, budget_inicial)
    return solver.resolver()
