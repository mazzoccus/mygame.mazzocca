import arcade

# Window settings
WIDTH = 800
HEIGHT = 600
TITLE = "CYBERPUNK 1977"
BACKGROUND_IMAGE = "background.png"


class CyberpunkGame(arcade.Window):
    """Simple Arcade game with a title screen and an optional PNG background."""

    def __init__(self, width: int, height: int, title: str):
        super().__init__(width, height, title)

        #nasconde cursore
        self.set_mouse_visible(False)

        #cosa viene visualizzato
        self.current_screen = "menu"

        #sfondo
        self.background_sprite_list = None
        try:
            sprite = arcade.Sprite(BACKGROUND_IMAGE)
            sprite.center_x = width / 2
            sprite.center_y = height / 2
            sprite.width = width
            sprite.height = height

            self.background_sprite_list = arcade.SpriteList()
            self.background_sprite_list.append(sprite)
        except Exception:
            #se immagine non carica sfondo a griglia
            self.background_sprite_list = None

        # testo
        self.title_text = arcade.Text(
            TITLE,
            width / 2,
            height * 0.65,
            arcade.color.AQUA,
            font_size=54,
            anchor_x="center",
            anchor_y="center",
        )

        self.instruction_text = arcade.Text(
            "Premi un tasto per iniziare",
            width / 2,
            height * 0.35,
            arcade.color.WHITE,
            font_size=24,
            anchor_x="center",
            anchor_y="center",
        )

        self.game_text = arcade.Text(
            "Gioco avviato! Premi ESC per tornare",
            width / 2,
            height / 2,
            arcade.color.WHITE,
            font_size=32,
            anchor_x="center",
            anchor_y="center",
        )

    def on_draw(self):
        """Draw the current screen."""
        self.clear()

        # Draw background (image if available, otherwise the grid)
        if self.background_sprite_list:
            self.background_sprite_list.draw()
        else:
            self._draw_grid_background()

        # Draw the current screen
        if self.current_screen == "menu":
            self.title_text.draw()
            self.instruction_text.draw()
        else:
            self.game_text.draw()

    def _draw_grid_background(self):
        """Fallback background when the PNG cannot be loaded."""
        for x in range(0, WIDTH, 40):
            arcade.draw_line(x, 0, x, HEIGHT, arcade.color.RED_DEVIL, 1)
        for y in range(0, HEIGHT, 40):
            arcade.draw_line(0, y, WIDTH, y, arcade.color.RED_DEVIL, 1)

    def on_key_press(self, symbol: int, modifiers: int):
        """Handle key presses to switch between screens."""
        if self.current_screen == "menu":
            self.current_screen = "game"
        else:
            # Press ESC to return to the menu
            if symbol == arcade.key.ESCAPE:
                self.current_screen = "menu"


if __name__ == "__main__":
    game = CyberpunkGame(WIDTH, HEIGHT, TITLE)
    arcade.run()
