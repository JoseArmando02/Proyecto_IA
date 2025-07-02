# Settings.py

class Settings:
    """
    Clase de configuración global para el juego.

    Esta clase contiene todos los parámetros que definen el comportamiento visual y lógico
    del juego, como las dimensiones de pantalla, la velocidad y tamaño de los objetos, y
    la visualización de rutas o gráficos.
    """

    def __init__(self):
        # 📺 Dimensiones y color de la pantalla
        self.screen_width = 800  # Se ajustará dinámicamente en main.py
        self.screen_height = 600  # Se ajustará dinámicamente en main.py
        self.bg_color = (0, 0, 0)  # Fondo negro

        # 👤 Jugador (Ahora una IA)
        self.player_speed = 3
        self.player_size = (32, 32)

        # 👾 Enemigo (También una IA)
        self.enemy_speed = 3
        self.enemy_size = (32, 32)

        # 🧱 Tiles del mapa
        self.tile_size = 32  # Tamaño de cada tile en píxeles

        # 🧠 Configuración de la IA
        self.training_samples_player = 600  # Muestras para el entrenamiento de la IA del jugador
        self.training_samples_enemy = 300  # Muestras para el entrenamiento de la IA del enemigo

        # 🕒 Control de recálculo de rutas para ambas IAs
        self.player_recalculate_path_interval = 350  # ms para el jugador
        self.enemy_recalculate_path_interval = 200  # ms para el enemigo

        # 🗺️ Opciones de visualización (para depuración)
        self.show_path = False  # Mostrar el camino calculado por la IA
        self.show_graph = False  # Mostrar el grafo de nodos (no implementado visualmente)