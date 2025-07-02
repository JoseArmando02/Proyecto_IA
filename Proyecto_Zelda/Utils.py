# utils.py

import numpy as np
import pygame
import math  # Asegúrate de que math esté importado


# Genera la siguiente ruta paso a paso desde la posición actual hasta un subconjunto del camino total.
# Divide la ruta en pequeños pasos de acuerdo a la velocidad para movimiento suave.
def gen_next_route(entity, speed, m=5):
    """
    Genera una secuencia de posiciones intermedias para un movimiento suave.

    Args:
        entity: El objeto (Player o Enemy) que se va a mover.
        speed: La velocidad de movimiento de la entidad.
        m: El número de nodos A* del camino a considerar para generar los pasos suaves.
    """
    current_pos = entity.position
    # Itera sobre los primeros 'm' nodos del camino A* de la entidad
    for i, node_pos in enumerate(entity.path[:min(len(entity.path), m)]):
        dx = abs(node_pos[0] - current_pos[0])
        dy = abs(node_pos[1] - current_pos[1])

        # Calcula el número de pasos necesarios para moverse entre los nodos
        # Asegura al menos 1 paso si la distancia es muy pequeña o cero
        num_steps = max(
            int(dx / speed),
            int(dy / speed),
            1
        )

        # Interpola coordenadas entre el punto actual y el nodo destino para cada paso
        x_arr = np.linspace(current_pos[0], node_pos[0], num_steps).tolist()
        y_arr = np.linspace(current_pos[1], node_pos[1], num_steps).tolist()

        # Agrega las posiciones interpoladas al buffer de movimiento de la entidad
        # zip combina x e y, y list(par) convierte cada tupla (x,y) en una lista [x,y]
        entity.path_positions.extend([list(par) for par in zip(x_arr, y_arr)])

        # Actualiza la posición de referencia para el siguiente segmento de interpolación
        current_pos = node_pos

    # Elimina los nodos del camino A* que ya han sido procesados
    entity.path = entity.path[min(len(entity.path), m):]


# Actualiza la posición del objeto y su rectángulo en pantalla (función auxiliar)
def set_pos(entity, position):
    """
    Establece la posición de una entidad y actualiza su rectángulo.

    Args:
        entity: El objeto (Player o Enemy) cuya posición se va a establecer.
        position (list/tuple): La nueva posición [x, y].
    """
    entity.position = np.array(position, dtype=float)
    entity.rect.center = entity.position


# Calcula distancia euclidiana entre dos puntos
def d(p_a, p_b):
    """
    Calcula la distancia euclidiana entre dos puntos (p_a, p_b).

    Args:
        p_a (tuple/list): Coordenadas del primer punto (x, y).
        p_b (tuple/list): Coordenadas del segundo punto (x, y).

    Returns:
        float: La distancia euclidiana.
    """
    dx = p_a[0] - p_b[0]
    dy = p_a[1] - p_b[1]
    distance = (dx ** 2 + dy ** 2) ** 0.5
    return distance


def show_text(screen, text, x, y, font_size=24, color=(255, 255, 255)):
    """
    Muestra texto en la pantalla de Pygame.

    Args:
        screen: Superficie de Pygame donde dibujar.
        text (str): El texto a mostrar.
        x (int): Coordenada X del texto.
        y (int): Coordenada Y del texto.
        font_size (int): Tamaño de la fuente.
        color (tuple): Color del texto en formato RGB.
    """
    font = pygame.font.Font(None, font_size)  # Puedes usar una fuente específica si quieres
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(topleft=(x, y))
    screen.blit(text_surface, text_rect)


def snap_to_grid(pos, tile_size):
    """
    Ajusta una posición continua (flotante) a la esquina superior izquierda del tile de la cuadrícula.

    Args:
        pos (tuple/list): La posición (x, y) continua.
        tile_size (int): El tamaño de cada tile en la cuadrícula.

    Returns:
        tuple: La posición (x, y) ajustada a la esquina superior izquierda del tile.
    """
    x = int(math.floor(pos[0] / tile_size)) * tile_size
    y = int(math.floor(pos[1] / tile_size)) * tile_size
    return (x, y)