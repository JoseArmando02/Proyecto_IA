# Enemy.py

import pygame
import numpy as np
from A_Star_Pathfinder import get_path, d
from Utils import gen_next_route, d, snap_to_grid
import threading


class Enemy(pygame.sprite.Sprite):
    def __init__(self, game, position, initial_target_pos):
        super().__init__()
        self.game = game
        self.image = pygame.image.load('imagenes/enemigo.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, game.settings.enemy_size)
        self.rect = self.image.get_rect(center=position)
        self.position = np.array(position, dtype=float)

        self.ia_model = None
        self.scaler = None
        self.path = []
        self.path_positions = []
        self.recalculating = False
        self.last_path_update_time = pygame.time.get_ticks()
        ### CAMBIO: self.graph_nodes ya no es necesario.
        # self.graph_nodes = None

    def set_model(self, model, scaler):
        self.ia_model = model
        self.scaler = scaler

    def update(self, player_position, walls):
        self.decide_move(player_position, walls)

        if self.path_positions:
            next_pos = self.path_positions.pop(0)
            self.position = next_pos
            self.rect.center = self.position

    def decide_move(self, target_position, walls):
        current_time = pygame.time.get_ticks()

        recalculate_needed = (
                    current_time - self.last_path_update_time > self.game.settings.enemy_recalculate_path_interval or
                    not self.path or
                    d(self.position, target_position) < self.game.settings.tile_size / 2)

        if recalculate_needed and not self.recalculating:
            threading.Thread(target=self.calculate_path_async, args=(target_position, walls)).start()
            self.last_path_update_time = current_time

        if self.path and not self.path_positions:
            gen_next_route(self, self.game.settings.enemy_speed, m=5)

    ### CAMBIO: La firma del método y la llamada a get_path se actualizan.
    def calculate_path_async(self, target_position, walls):
        self.recalculating = True

        start_pos = snap_to_grid(self.position, self.game.settings.tile_size)
        end_pos = snap_to_grid(target_position, self.game.settings.tile_size)

        # La llamada a get_path usa la nueva firma (solo necesita la lista de obstáculos).
        path = get_path(self.game, start_pos, end_pos, walls)

        if path:
            self.path = path

        self.recalculating = False

    ### CAMBIO: El método generate_graph_nodes_from_map ya no es necesario y se elimina.