import arcade
import math
import time

WIDTH=800
HEIGHT=600
TITLE="CYBERPUNK 2024"

class CyberpunkGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        self.player_x = width // 2
        self.player_y = height // 2
        self.player_speed = 5

        self.obstacles = []
        for _ in range(10):
            x = arcade.random.randint(50, width - 50)
            y = arcade.random.randint(50, height - 50)
            self.obstacles.append((x, y))

    def on_draw(self):
        arcade.start_render()


    def on_key_press(self, key, modifiers):
        if key == arcade.key.W:
            self.player_y += self.player_speed
        elif key == arcade.key.S:
            self.player_y -= self.player_speed
        elif key == arcade.key.A:
            self.player_x -= self.player_speed
        elif key == arcade.key.D:
            self.player_x += self.player_speed

    def update(self, delta_time):
        self.player_x = max(15, min(WIDTH - 15, self.player_x))
        self.player_y = max(15, min(HEIGHT - 15, self.player_y)) 
        #Gestione personaggio e ostacoli e mappa