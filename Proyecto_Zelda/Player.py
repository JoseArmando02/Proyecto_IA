# Player.py

import pygame
import numpy as np
from A_Star_Pathfinder import get_path, d
from Utils import gen_next_route, d, snap_to_grid
import threading


class Player(pygame.sprite.Sprite):
    def __init__(self, game, position, goal_pos):
        super().__init__()
        self.game = game
        self.image = pygame.image.load('imagenes/jugador.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, game.settings.player_size)
        self.rect = self.image.get_rect(center=position)
        self.position = np.array(position, dtype=float)
        self.goal_pos = goal_pos

        self.ia_model = None
        self.scaler = None
        self.path = []
        self.path_positions = []
        self.recalculating = False
        # self.last_path_update_time ya no es necesario para la lógica principal de recálculo

    def set_model(self, model, scaler):
        self.ia_model = model
        self.scaler = scaler

    def update(self, walls, dynamic_obstacles):
        self.decide_move(walls, dynamic_obstacles)

        # Si hay pasos de movimiento en el buffer, ejecutar el siguiente.
        if self.path_positions:
            next_pos = self.path_positions.pop(0)
            self.position = next_pos
            self.rect.center = self.position

    def decide_move(self, walls, dynamic_obstacles):
        player_tile_pos = snap_to_grid(self.position, self.game.settings.tile_size)
        goal_tile_pos = snap_to_grid(self.goal_pos, self.game.settings.tile_size)

        # Lógica para el movimiento final de aproximación a la meta.
        if player_tile_pos == goal_tile_pos:
            if not self.path_positions and not self.recalculating:
                self.path.clear()
                self.path.append(self.goal_pos)
                gen_next_route(self, self.game.settings.player_speed, m=1)
            return

        ### --- LÓGICA DE MOVIMIENTO Y RECÁLCULO CORREGIDA --- ###

        # 1. Si NO nos estamos moviendo Y NO estamos ya calculando una ruta...
        if not self.path_positions and not self.recalculating:

            # 2. Y si el camino A* está vacío (necesitamos una nueva ruta)...
            if not self.path:
                # 3. Entonces, calcular una nueva ruta.
                all_obstacles = walls + dynamic_obstacles
                threading.Thread(target=self.calculate_path_async, args=(self.goal_pos, all_obstacles)).start()

            # 4. Si después de todo, TENEMOS una ruta A* (ya sea recién calculada o una que sobró)...
            if self.path:
                # 5. Generar los pasos suaves para comenzar a movernos.
                gen_next_route(self, self.game.settings.player_speed, m=5)

    def calculate_path_async(self, target_position, all_obstacles):
        self.recalculating = True

        start_pos = snap_to_grid(self.position, self.game.settings.tile_size)
        end_pos = snap_to_grid(target_position, self.game.settings.tile_size)

        path = get_path(self.game, start_pos, end_pos, all_obstacles)

        if path:
            self.path = path
        else:
            # Si A* falla, limpiar la ruta para forzar un nuevo intento en el siguiente ciclo.
            self.path.clear()

        self.recalculating = False