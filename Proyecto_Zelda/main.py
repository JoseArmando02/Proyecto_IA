# main.py

import pygame
import sys
from Settings import Settings
from Player import Player
from Enemy import Enemy
from Tile import Map
from Mapa import MAP_DATA
from AI_Trainer import train_ia
from Utils import show_text, d


class ZeldaLikeGame:
    def __init__(self):
        pygame.init()
        self.settings = Settings()

        map_width_tiles = len(MAP_DATA[0])
        map_height_tiles = len(MAP_DATA)
        calculated_screen_width = map_width_tiles * self.settings.tile_size
        calculated_screen_height = map_height_tiles * self.settings.tile_size

        self.screen = pygame.display.set_mode((calculated_screen_width, calculated_screen_height))
        pygame.display.set_caption("Proyecto IA Zelda")

        self.settings.screen_width = self.screen.get_width()
        self.settings.screen_height = self.screen.get_height()

        self.map = Map(self.settings, MAP_DATA)
        self.clock = pygame.time.Clock()
        self.game_active = False
        self.game_over = False
        self.game_won = False

        # Instanciar al jugador (sigue siendo uno solo)
        self.player = Player(self, self.map.player_start_pos, self.map.goal_pos)
        self.map.all_sprites.add(self.player)

        # --- CAMBIO: CREAR UN GRUPO PARA LOS ENEMIGOS ---
        self.enemies_group = pygame.sprite.Group()
        # --- FIN DEL CAMBIO ---

        self.running = True

    def run(self):
        # 1. Fase de Entrenamiento para el JUGADOR
        print("Iniciando el entrenamiento de la IA del JUGADOR. Por favor, espere...")
        player_ia_model, player_scaler = train_ia(
            self.settings.training_samples_player, self.map.get_collidable_rects(),
            self.settings.tile_size, self.settings.screen_width, self.settings.screen_height)
        if player_ia_model and player_scaler:
            self.player.set_model(player_ia_model, player_scaler)
        print("¡Entrenamiento de la IA del JUGADOR finalizado!")

        # 2. Fase de Entrenamiento para el ENEMIGO (SOLO UN MODELO GENÉRICO)
        # Entrenamos una única IA que será compartida por todos los enemigos.
        print("Iniciando el entrenamiento de la IA del ENEMIGO. Por favor, espere...")
        enemy_ia_model, enemy_scaler = train_ia(
            self.settings.training_samples_enemy, self.map.get_collidable_rects(),
            self.settings.tile_size, self.settings.screen_width, self.settings.screen_height)
        print("¡Entrenamiento de la IA del ENEMIGO finalizado!")

        # --- CAMBIO: CREAR Y CONFIGURAR MÚLTIPLES ENEMIGOS ---
        # Usamos un bucle para crear un enemigo por cada posición de inicio encontrada en el mapa.
        for start_pos in self.map.enemy_start_positions:
            enemy = Enemy(self, start_pos, self.player.position)  # El objetivo inicial es el jugador
            if enemy_ia_model and enemy_scaler:
                enemy.set_model(enemy_ia_model, enemy_scaler)  # Le asignamos el modelo de IA compartido

            self.enemies_group.add(enemy)  # Añadimos el enemigo al grupo de enemigos
            self.map.all_sprites.add(enemy)  # Y al grupo general para que se dibuje
        # --- FIN DEL CAMBIO ---

        print("Abriendo la ventana del juego...")
        self.game_active = True
        while self.running:
            self._check_events()
            if self.game_active and not self.game_over and not self.game_won:
                self._update_elements()
                self._check_game_state()
                self._update_screen()
                self.clock.tick(60)
            elif self.game_over:
                self._update_screen_game_over()
            elif self.game_won:
                self._update_screen_game_won()

    def _check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def _update_elements(self):
        static_obstacles = self.map.get_collidable_rects()

        # --- CAMBIO: EL JUGADOR DEBE EVITAR A TODOS LOS ENEMIGOS ---
        # Creamos una lista de zonas de peligro, una por cada enemigo.
        dynamic_obstacles = []
        for enemy in self.enemies_group:
            danger_zone = enemy.rect.inflate(self.settings.tile_size * 2, self.settings.tile_size * 2)
            dynamic_obstacles.append(danger_zone)

        # Actualizamos al jugador, que ahora conoce todos los peligros
        self.player.update(static_obstacles, dynamic_obstacles)
        # --- FIN DEL CAMBIO ---

        # --- CAMBIO: ACTUALIZAR TODO EL GRUPO DE ENEMIGOS ---
        # Pygame se encarga de llamar al método .update() de cada enemigo en el grupo.
        self.enemies_group.update(self.player.position, static_obstacles)
        # --- FIN DEL CAMBIO ---

    def _check_game_state(self):
        if d(self.player.position, self.map.goal_pos) < self.settings.tile_size / 2:
            self.game_won = True
            self.game_active = False
            print("¡JUGADOR HA GANADO!")

        # --- CAMBIO: COMPROBAR COLISIÓN CON CUALQUIER ENEMIGO DEL GRUPO ---
        # pygame.sprite.spritecollideany comprueba si un sprite (jugador) choca con alguno de un grupo.
        if pygame.sprite.spritecollideany(self.player, self.enemies_group):
            self.game_over = True
            self.game_active = False
            print("¡GAME OVER! Un enemigo te atrapó.")
        # --- FIN DEL CAMBIO ---

    def _update_screen(self):
        self.screen.fill(self.settings.bg_color)
        self.map.all_sprites.draw(self.screen)  # all_sprites ahora contiene al jugador y a todos los enemigos
        pygame.display.flip()

    def _update_screen_game_over(self):
        self.screen.fill((150, 0, 0))
        show_text(self.screen, "¡GAME OVER!", self.settings.screen_width // 2 - 100,
                  self.settings.screen_height // 2 - 30, font_size=48, color=(255, 255, 255))
        show_text(self.screen, "Un enemigo te atrapó.", self.settings.screen_width // 2 - 120,
                  self.settings.screen_height // 2 + 20, font_size=30, color=(255, 255, 255))
        pygame.display.flip()

    def _update_screen_game_won(self):
        self.screen.fill((0, 150, 0))
        show_text(self.screen, "¡GANASTE!", self.settings.screen_width // 2 - 70, self.settings.screen_height // 2 - 30,
                  font_size=48, color=(255, 255, 255))
        show_text(self.screen, "Llegaste a la meta.", self.settings.screen_width // 2 - 100,
                  self.settings.screen_height // 2 + 20, font_size=30, color=(255, 255, 255))
        pygame.display.flip()


if __name__ == '__main__':
    game = ZeldaLikeGame()
    game.run()
    pygame.quit()
    sys.exit()