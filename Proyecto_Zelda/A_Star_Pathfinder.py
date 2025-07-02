# A_Star_Pathfinder.py

import heapq
import numpy as np
import pygame ### CAMBIO: Importar pygame para usar Rect

class Nodo:
    """
    Representa un nodo estático en el grafo. Solo contiene su posición.
    Toda la información de la búsqueda A* se manejará fuera de esta clase.
    """

    def __init__(self, pos):
        self.pos = pos

    def __eq__(self, other):
        return self.pos == other.pos

    def __hash__(self):
        return hash(self.pos)


def d(p1, p2):
    """Calcula la distancia euclidiana (heurística) entre dos puntos."""
    return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


### CAMBIO: La función ahora solo necesita una lista de todos los obstáculos.
def get_path(game, start_pos, end_pos, all_obstacles):
    """
    Implementación de A* "sin estado" que maneja obstáculos dinámicos.
    Los nodos del grafo no se modifican. Todos los datos de la búsqueda
    se almacenan en diccionarios locales.
    """
    open_list = []
    heapq.heappush(open_list, (0, start_pos))  # La cola guarda (f_cost, position)

    closed_set = set()

    # Diccionarios para almacenar los datos de la búsqueda
    g_costs = {start_pos: 0}
    parents = {start_pos: None}

    while open_list:
        current_f, current_pos = heapq.heappop(open_list)

        if current_pos in closed_set:
            continue

        closed_set.add(current_pos)

        # Si hemos llegado al final, reconstruir el camino
        if current_pos == end_pos:
            path = []
            while current_pos:
                path.append(current_pos)
                current_pos = parents[current_pos]
            return path[::-1]  # Devolver el camino invertido

        # Explorar vecinos
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            neighbor_pos = (current_pos[0] + dx * game.settings.tile_size,
                            current_pos[1] + dy * game.settings.tile_size)

            ### CAMBIO: Verificación de colisiones en tiempo real en lugar de usar un grafo pre-calculado.
            # 1. Comprobar si el vecino está dentro de los límites de la pantalla.
            if not (0 <= neighbor_pos[0] < game.settings.screen_width and
                    0 <= neighbor_pos[1] < game.settings.screen_height):
                continue

            # 2. Crear un rect para el vecino para la detección de colisiones.
            neighbor_rect = pygame.Rect(neighbor_pos[0], neighbor_pos[1], game.settings.tile_size, game.settings.tile_size)

            # 3. Comprobar si el vecino choca con CUALQUIER obstáculo (muros, enemigo, etc.).
            if neighbor_rect.collidelist(all_obstacles) != -1:
                continue
            ### FIN DEL CAMBIO

            # El coste para moverse al vecino es siempre el tamaño del tile
            new_g = g_costs[current_pos] + game.settings.tile_size

            # Si el vecino no ha sido visitado o encontramos un camino mejor
            if neighbor_pos not in g_costs or new_g < g_costs[neighbor_pos]:
                g_costs[neighbor_pos] = new_g
                h_cost = d(neighbor_pos, end_pos)
                f_cost = new_g + h_cost
                parents[neighbor_pos] = current_pos
                heapq.heappush(open_list, (f_cost, neighbor_pos))

    return []  # No se encontró un camino