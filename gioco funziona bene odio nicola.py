import arcade
import math
import time

WIDTH= 800
HEIGHT= 600
TITLE= "CYBERPUNK 2024"

class CyberpunkGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        self.set_mouse_visible(False)
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()
        for x in range(0, WIDTH, 40):
            arcade.draw_line(x, 0, x, HEIGHT, arcade.color.RED_DEVIL, 1)
        for y in range(0, HEIGHT, 40):
            arcade.draw_line(0, y, WIDTH, y, arcade.color.RED_DEVIL, 1)
            

if __name__ == "__main__":
    game = CyberpunkGame(WIDTH, HEIGHT, TITLE)
    arcade.run()