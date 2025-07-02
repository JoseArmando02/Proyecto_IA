# Tile.py

import pygame
import os
from Mapa import MURO, CAMINO, BLOQUE, META, JUGADOR, ENEMIGO  # Importar las definiciones de caracteres


class Tile(pygame.sprite.Sprite):
    """
    Representa un solo tile visual en el mapa (muro, camino, bloque, meta).
    """

    def __init__(self, x, y, image, is_collidable=False, is_goal=False, is_movable=False):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.is_collidable = is_collidable  # True para muros y bloques
        self.is_goal = is_goal  # True para la meta
        self.is_movable = is_movable  # True para bloques movibles


class Map:
    """
    Gestiona la carga y el dibujo del mapa del juego.
    """

    def __init__(self, game_settings, map_data_list):
        self.settings = game_settings
        self.map_data = map_data_list  # Ahora es directamente la lista de strings del mapa
        self.tile_size = self.settings.tile_size

        self.player_start_pos = None
        self.enemy_start_positions = []
        self.goal_pos = None

        self.all_sprites = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()  # Muros y bloques (todos colisionables inicialmente)
        self.movable_blocks = pygame.sprite.Group()  # Solo los bloques que el jugador puede empujar
        self.goal_tile = None  # Referencia al tile de la meta

        self._load_tile_images()
        self._build_map_sprites()

    def _load_tile_images(self):
        """Carga las imágenes necesarias para los diferentes tipos de tiles."""
        image_path = "imagenes"  # Asegúrate de que esta carpeta exista y contenga las imágenes
        self.images = {
            MURO: pygame.transform.scale(pygame.image.load(os.path.join(image_path, 'muro.png')).convert(),
                                         (self.tile_size, self.tile_size)),
            CAMINO: pygame.transform.scale(pygame.image.load(os.path.join(image_path, 'camino.png')).convert(),
                                           (self.tile_size, self.tile_size)),
            BLOQUE: pygame.transform.scale(pygame.image.load(os.path.join(image_path, 'bloque.png')).convert(),
                                           (self.tile_size, self.tile_size)),
            META: pygame.transform.scale(pygame.image.load(os.path.join(image_path, 'meta.png')).convert_alpha(),
                                         (self.tile_size, self.tile_size)),
            # El jugador y el enemigo se cargarán en sus propias clases
        }

    def _build_map_sprites(self):
        """Construye los objetos Tile y los agrega a los grupos de sprites."""
        for y, row_str in enumerate(self.map_data):
            for x, char in enumerate(row_str):
                pos_x = x * self.tile_size
                pos_y = y * self.tile_size

                # Por defecto, se crea un tile de camino debajo de los personajes y otros elementos
                tile_image = self.images[CAMINO]
                is_collidable = False
                is_goal = False
                is_movable = False

                # Determinar el tipo de tile y sus propiedades basadas en el carácter
                if char == MURO:
                    tile_image = self.images[MURO]
                    is_collidable = True
                elif char == BLOQUE:
                    tile_image = self.images[BLOQUE]
                    is_collidable = True
                    is_movable = True
                elif char == META:
                    tile_image = self.images[META]
                    is_goal = True
                    # Almacena la posición central de la meta
                    self.goal_pos = (pos_x + self.tile_size // 2, pos_y + self.tile_size // 2)
                elif char == JUGADOR:
                    # Almacena la posición central del jugador
                    self.player_start_pos = (pos_x + self.tile_size // 2, pos_y + self.tile_size // 2)
                elif char == ENEMIGO:
                    # Añadimos cada posición de enemigo a la lista
                    self.enemy_start_positions.append((pos_x + self.tile_size // 2, pos_y + self.tile_size // 2))

                # Crea el tile y agrégalo a los grupos de sprites
                tile = Tile(pos_x, pos_y, tile_image, is_collidable=is_collidable, is_goal=is_goal,
                            is_movable=is_movable)
                self.all_sprites.add(tile)

                # Agrega a los grupos específicos si es colisionable o movible
                if is_collidable:
                    self.walls.add(tile)
                if is_movable:
                    self.movable_blocks.add(tile)
                if is_goal:
                    self.goal_tile = tile

    def draw(self, screen):
        """Dibuja todos los tiles del mapa en la pantalla."""
        self.all_sprites.draw(screen)

    def get_collidable_rects(self):
        """Retorna una lista de rectángulos de todos los objetos con los que se puede colisionar (muros y bloques)."""
        return [tile.rect for tile in self.walls]