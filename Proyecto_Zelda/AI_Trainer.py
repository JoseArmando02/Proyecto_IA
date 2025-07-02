# AI_Trainer.py

import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from A_Star_Pathfinder import d, get_path
import random
import pygame
from Mapa import MAP_DATA, MURO, BLOQUE


def generate_training_data(num_samples, map_walls, tile_size, screen_width, screen_height, max_retries_per_sample=10):
    """
    Genera datos sintéticos para entrenar la IA.
    """
    X = []
    y = []

    graph_nodes = []
    map_height_pixels = screen_height
    map_width_pixels = screen_width

    # Este bucle sigue siendo útil para encontrar puntos de inicio/fin válidos que no estén en una pared.
    for y_coord in range(0, map_height_pixels, tile_size):
        for x_coord in range(0, map_width_pixels, tile_size):
            temp_rect = pygame.Rect(x_coord, y_coord, tile_size, tile_size)
            if temp_rect.collidelist(map_walls) == -1:
                # Almacenamos directamente la posición (tupla) en lugar de un objeto Nodo.
                graph_nodes.append((x_coord, y_coord))

    if not graph_nodes:
        print("Error: No se pudieron generar nodos de grafo válidos. Revise el mapa y el tamaño de los tiles.")
        return np.array([]), np.array([]), StandardScaler()

    print(f"  Generando {num_samples} muestras de entrenamiento...")
    for i in range(num_samples):
        start_node_pos = random.choice(graph_nodes)
        end_node_pos = random.choice(graph_nodes)

        retries = 0
        while start_node_pos == end_node_pos and retries < max_retries_per_sample:
            end_node_pos = random.choice(graph_nodes)
            retries += 1
        if start_node_pos == end_node_pos:
            continue

        class MockGame:
            def __init__(self, tile_size_val, width, height):
                self.settings = self.MockSettings(tile_size_val, width, height)

            class MockSettings:
                def __init__(self, tile_size_val, width, height):
                    self.tile_size = tile_size_val
                    self.screen_width = width
                    self.screen_height = height

        # Pasamos las dimensiones de la pantalla al mock_game para que A* pueda verificar los límites.
        mock_game = MockGame(tile_size, screen_width, screen_height)

        start_pos = start_node_pos
        end_pos = end_node_pos

        ### CAMBIO: Corregir la llamada a get_path para que coincida con la nueva firma de 4 argumentos.
        # Se elimina el argumento 'graph_nodes' que ya no es necesario.
        optimal_path = get_path(mock_game, start_pos, end_pos, map_walls)

        if optimal_path and len(optimal_path) > 1:
            next_step_pos = optimal_path[1]
            current_pos = optimal_path[0]

            dx_abs = abs(next_step_pos[0] - current_pos[0])
            dy_abs = abs(next_step_pos[1] - current_pos[1])

            direction = -1
            if dx_abs > 0:
                if next_step_pos[0] > current_pos[0]:
                    direction = 2  # Derecha
                else:
                    direction = 3  # Izquierda
            elif dy_abs > 0:
                if next_step_pos[1] > current_pos[1]:
                    direction = 1  # Abajo
                else:
                    direction = 0  # Arriba
            else:
                continue

            features = [
                current_pos[0], current_pos[1],
                end_node_pos[0], end_node_pos[1],
                d(current_pos, end_node_pos)
            ]
            X.append(features)
            y.append(direction)

    if not X:
        print("Advertencia: No se generaron datos de entrenamiento. Asegúrese de que el mapa permite rutas.")
        return np.array([]), np.array([]), StandardScaler()

    X = np.array(X)
    y = np.array(y)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    return X_scaled, y, scaler


def train_ia(num_samples, map_walls, tile_size, screen_width, screen_height):
    """
    Entrena un modelo de IA (MLPClassifier) con datos generados.
    """
    X, y, scaler = generate_training_data(num_samples, map_walls, tile_size, screen_width, screen_height)

    if X.size == 0 or y.size == 0:
        print("No hay datos suficientes para entrenar la IA. Abortando entrenamiento.")
        return None, None

    model = MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=2000, activation='relu', solver='adam', random_state=1)

    print("  Entrenando el modelo de IA. Esto puede tomar un momento...")
    model.fit(X, y)
    print("  Entrenamiento del modelo de IA finalizado.")

    return model, scaler


if __name__ == '__main__':
    class MockSettings:
        def __init__(self):
            self.tile_size = 32
            self.screen_width = len(MAP_DATA[0]) * self.tile_size
            self.screen_height = len(MAP_DATA) * self.tile_size


    settings = MockSettings()


    class MockMap:
        def __init__(self, map_data, tile_s):
            self.map_data = map_data
            self.tile_size = tile_s
            self.walls_rects = []
            for y_idx, row in enumerate(self.map_data):
                for x_idx, char in enumerate(row):
                    if char == MURO or char == BLOQUE:
                        self.walls_rects.append(pygame.Rect(x_idx * tile_s, y_idx * tile_s, tile_s, tile_s))

        def get_collidable_rects(self):
            return self.walls_rects


    temp_map_instance = MockMap(MAP_DATA, settings.tile_size)
    test_map_walls = temp_map_instance.get_collidable_rects()

    screen_width_for_training = len(MAP_DATA[0]) * settings.tile_size
    screen_height_for_training = len(MAP_DATA) * settings.tile_size

    print("Iniciando entrenamiento de prueba para AI_Trainer.py...")
    model, scaler = train_ia(100, test_map_walls, settings.tile_size, screen_width_for_training,
                             screen_height_for_training)
    if model and scaler:
        print("Entrenamiento de la IA de prueba finalizado.")
        # Generamos los datos de prueba de la misma forma que los de entrenamiento
        X_test_scaled, y_test, _ = generate_training_data(10, test_map_walls, settings.tile_size,
                                                          screen_width_for_training,
                                                          screen_height_for_training)

        # El escalador ya está ajustado (fitted), así que podemos usarlo si es necesario.
        # En este caso, generate_training_data ya devuelve los datos escalados.
        if X_test_scaled.size > 0:
            print(f"Precisión del modelo en datos de prueba: {model.score(X_test_scaled, y_test):.2f}")
        else:
            print("No se pudieron generar datos de prueba para evaluar la precisión.")
    else:
        print("El entrenamiento de la IA de prueba no se completó debido a la falta de datos.")