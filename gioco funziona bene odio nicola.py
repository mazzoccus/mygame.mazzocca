import arcade

# Window settings
WIDTH = 800
HEIGHT = 600
TITLE = "CyBERPUNK 1977"
BACKGROUND_IMAGE = "assets/background.png"

# Game constants
PLAYER_SPEED = 5
BULLET_SPEED = 10
ENEMY_SPEED = 2
PLAYER_HEALTH = 3

# Sprite assets - Scarica i PNG con questi nomi e mettili in assets/
SPRITE_PLAYER = "assets/player.png"
SPRITE_DRONE = "assets/drone.png"
SPRITE_CYBORG = "assets/cyborg.png"
SPRITE_TURRET = "assets/turret.png"
SPRITE_BOSS = "assets/boss.png"
SPRITE_UPGRADE = "assets/upgrade.png"
SPRITE_BULLET = "assets/bullet.png"  # opzionale, usato solo se vuoi sprite per proiettili


class CyberpunkGame(arcade.Window):
    """Cyberpunk roguelike MVP with procedural rooms, combat, and upgrades."""

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
            "Premi ENTER per iniziare",
            width / 2,
            height * 0.35,
            arcade.color.WHITE,
            font_size=24,
            anchor_x="center",
            anchor_y="center",
        )

        self.game_over_text = arcade.Text(
            "Sistema corrotto! Premi R per ricominciare",
            width / 2,
            height / 2,
            arcade.color.RED,
            font_size=32,
            anchor_x="center",
            anchor_y="center",
        )

        self.win_text = arcade.Text(
            "Vittoria! Premi R per ricominciare",
            width / 2,
            height / 2,
            arcade.color.GREEN,
            font_size=32,
            anchor_x="center",
            anchor_y="center",
        )

        # Game elements
        self.player_sprite = None
        self.enemy_sprites = arcade.SpriteList()
        self.upgrade_sprites = arcade.SpriteList()
        self.bullets = []  # list of {'x':, 'y':, 'dx':, 'dy':}
        self.enemy_bullets = []  # list of {'x':, 'y':, 'dx':, 'dy':}
        self.keys_pressed = set()

        self.current_room = 0
        self.player_health = PLAYER_HEALTH
        self.upgrades_collected = []

        # Game stats
        self.player_speed = PLAYER_SPEED
        self.bullet_speed = BULLET_SPEED
        self.enemy_speed = ENEMY_SPEED
        self.fire_rate = 0.5  # seconds between shots
        self.last_shot = 0

        # Sandevistan
        self.sandevistan_active = False
        self.sandevistan_timer = 0
        self.sandevistan_cooldown = 0
        self.time_scale = 1.0

        # Room boundaries
        self.room_left = 50
        self.room_right = WIDTH - 50
        self.room_top = HEIGHT - 50
        self.room_bottom = 50

        # Doors (for now, just check if cleared to move)
        self.doors_open = False

        # Room definitions: list of enemy configs
        self.rooms = [
            [{'x': 200, 'y': 300, 'type': 'drone', 'hp': 1}, {'x': 600, 'y': 400, 'type': 'drone', 'hp': 1}],  # Distretto 1: 2 droni
            [{'x': 100, 'y': 200, 'type': 'turret', 'hp': 1}, {'x': 300, 'y': 500, 'type': 'cyborg', 'hp': 1}, {'x': 500, 'y': 100, 'type': 'drone', 'hp': 1}],  # Distretto 2: torretta, cyborg, drone
            [{'x': 400, 'y': 300, 'type': 'boss', 'hp': 3}],  # Distretto 3: Boss IA
        ]

    def setup_room(self):
        """Setup the current room with enemies."""
        self.enemy_sprites = arcade.SpriteList()
        for enemy in self.rooms[self.current_room]:
            try:
                sprite = arcade.Sprite(f"assets/enemy_{enemy['type']}.png", scale=0.05)
            except:
                # Fallback to circle if PNG not found
                sprite = arcade.SpriteSolidColor(20, 20, arcade.color.RED)
            sprite.center_x = enemy['x']
            sprite.center_y = enemy['y']
            sprite.type = enemy['type']
            sprite.hp = enemy['hp']
            self.enemy_sprites.append(sprite)

        if self.player_sprite is None:
            try:
                self.player_sprite = arcade.Sprite("assets/player.png", scale=0.05)
            except:
                self.player_sprite = arcade.SpriteSolidColor(20, 20, arcade.color.BLUE)
        self.player_sprite.center_x = WIDTH / 2
        self.player_sprite.center_y = HEIGHT / 2

        self.upgrade_sprites = arcade.SpriteList()
        self.doors_open = False
        self.enemy_bullets = []

    def reset_game(self):
        """Reset the game to initial state."""
        self.current_room = 0
        self.player_health = PLAYER_HEALTH
        self.upgrades_collected = []
        self.sandevistan_active = False
        self.sandevistan_timer = 0
        self.sandevistan_cooldown = 0
        self.time_scale = 1.0
        self.player_speed = PLAYER_SPEED
        self.fire_rate = 0.5
        self.setup_room()

    def on_update(self, delta_time):
        """Update game logic."""
        if self.current_screen != "game":
            return

        # Sandevistan
        if self.sandevistan_active:
            self.time_scale = 0.3
            self.sandevistan_timer -= delta_time
            if self.sandevistan_timer <= 0:
                self.sandevistan_active = False
                self.sandevistan_cooldown = 10
                self.time_scale = 1.0
        else:
            self.time_scale = 1.0
            if self.sandevistan_cooldown > 0:
                self.sandevistan_cooldown -= delta_time

        # Player movement
        player_speed = self.player_speed if not self.sandevistan_active else self.player_speed / self.time_scale
        if arcade.key.W in self.keys_pressed:
            self.player_sprite.center_y += player_speed
        if arcade.key.S in self.keys_pressed:
            self.player_sprite.center_y -= player_speed
        if arcade.key.A in self.keys_pressed:
            self.player_sprite.center_x -= player_speed
        if arcade.key.D in self.keys_pressed:
            self.player_sprite.center_x += player_speed

        # Keep player in room bounds
        self.player_sprite.center_x = max(self.room_left, min(self.room_right, self.player_sprite.center_x))
        self.player_sprite.center_y = max(self.room_bottom, min(self.room_top, self.player_sprite.center_y))

        # Enemy AI
        for sprite in self.enemy_sprites:
            if sprite.type == 'drone':
                # Follow player
                dx = self.player_sprite.center_x - sprite.center_x
                dy = self.player_sprite.center_y - sprite.center_y
                dist = (dx**2 + dy**2)**0.5
                if dist > 0:
                    sprite.center_x += (dx / dist) * self.enemy_speed * self.time_scale
                    sprite.center_y += (dy / dist) * self.enemy_speed * self.time_scale
            elif sprite.type == 'cyborg':
                # Random movement
                sprite.center_x += (arcade.rand_in_range(-1, 1) * self.enemy_speed * self.time_scale)
                sprite.center_y += (arcade.rand_in_range(-1, 1) * self.enemy_speed * self.time_scale)
            elif sprite.type == 'turret':
                # Shoot periodically
                if arcade.rand_int(0, 100) < 2:  # 2% chance per frame
                    dx = self.player_sprite.center_x - sprite.center_x
                    dy = self.player_sprite.center_y - sprite.center_y
                    dist = (dx**2 + dy**2)**0.5
                    if dist > 0:
                        bullet = {
                            'x': sprite.center_x,
                            'y': sprite.center_y,
                            'dx': (dx / dist) * self.bullet_speed * 0.5,  # Slower enemy bullets
                            'dy': (dy / dist) * self.bullet_speed * 0.5
                        }
                        self.enemy_bullets.append(bullet)
            elif sprite.type == 'boss':
                # Boss AI: follow and shoot
                dx = self.player_sprite.center_x - sprite.center_x
                dy = self.player_sprite.center_y - sprite.center_y
                dist = (dx**2 + dy**2)**0.5
                if dist > 0:
                    sprite.center_x += (dx / dist) * self.enemy_speed * self.time_scale * 0.5  # Slower
                    sprite.center_y += (dy / dist) * self.enemy_speed * self.time_scale * 0.5
                if arcade.rand_int(0, 100) < 5:  # Shoot more
                    bullet = {
                        'x': sprite.center_x,
                        'y': sprite.center_y,
                        'dx': (dx / dist) * self.bullet_speed * 0.7,
                        'dy': (dy / dist) * self.bullet_speed * 0.7
                    }
                    self.enemy_bullets.append(bullet)

        # Move bullets
        for bullet in self.bullets[:]:
            bullet['x'] += bullet['dx'] * self.time_scale
            bullet['y'] += bullet['dy'] * self.time_scale
            if (bullet['x'] < 0 or bullet['x'] > WIDTH or
                bullet['y'] < 0 or bullet['y'] > HEIGHT):
                self.bullets.remove(bullet)

        # Move enemy bullets
        for bullet in self.enemy_bullets[:]:
            bullet['x'] += bullet['dx'] * self.time_scale
            bullet['y'] += bullet['dy'] * self.time_scale
            if (bullet['x'] < 0 or bullet['x'] > WIDTH or
                bullet['y'] < 0 or bullet['y'] > HEIGHT):
                self.enemy_bullets.remove(bullet)

        # Bullet-enemy collisions
        for bullet in self.bullets[:]:
            for sprite in self.enemy_sprites[:]:
                if abs(bullet['x'] - sprite.center_x) < 15 and abs(bullet['y'] - sprite.center_y) < 15:
                    sprite.hp -= 1
                    if sprite.hp <= 0:
                        self.enemy_sprites.remove(sprite)
                        # Spawn upgrade
                        try:
                            upgrade_sprite = arcade.Sprite("assets/upgrade.png", scale=0.05)
                        except:
                            upgrade_sprite = arcade.SpriteSolidColor(10, 10, arcade.color.GREEN)
                        upgrade_sprite.center_x = sprite.center_x
                        upgrade_sprite.center_y = sprite.center_y
                        self.upgrade_sprites.append(upgrade_sprite)
                    self.bullets.remove(bullet)
                    break

        # Enemy bullet-player collisions
        for bullet in self.enemy_bullets[:]:
            if abs(bullet['x'] - self.player_sprite.center_x) < 13 and abs(bullet['y'] - self.player_sprite.center_y) < 13:
                self.player_health -= 1
                self.enemy_bullets.remove(bullet)
                if self.player_health <= 0:
                    self.current_screen = "game_over"

        # Player-enemy collisions
        hit_sprites = arcade.check_for_collision_with_list(self.player_sprite, self.enemy_sprites)
        if hit_sprites:
            for sprite in hit_sprites:
                self.enemy_sprites.remove(sprite)
            self.player_health -= len(hit_sprites)
            if self.player_health <= 0:
                self.current_screen = "game_over"

        # Player-upgrade collisions
        hit_upgrades = arcade.check_for_collision_with_list(self.player_sprite, self.upgrade_sprites)
        for upgrade_sprite in hit_upgrades:
            self.upgrade_sprites.remove(upgrade_sprite)
            self.upgrades_collected.append("velocità")
            self.player_speed += 1

        # Check if room cleared
        if len(self.enemy_sprites) == 0 and not self.doors_open:
            self.doors_open = True
            # Spawn upgrades
            for _ in range(len(self.rooms[self.current_room])):
                try:
                    upgrade_sprite = arcade.Sprite("assets/upgrade.png", scale=0.05)
                except:
                    upgrade_sprite = arcade.SpriteSolidColor(10, 10, arcade.color.GREEN)
                upgrade_sprite.center_x = arcade.rand_in_range(self.room_left, self.room_right)
                upgrade_sprite.center_y = arcade.rand_in_range(self.room_bottom, self.room_top)
                self.upgrade_sprites.append(upgrade_sprite)

        # If doors open and player near door, next room (for now, auto after clear)
        if self.doors_open and len(self.enemy_sprites) == 0:
            if self.current_room < len(self.rooms) - 1:
                self.current_room += 1
                self.setup_room()
            else:
                self.current_screen = "win"

    def on_draw(self):
        """Draw the current screen."""
        self.clear()

        if self.background_sprite_list:
            self.background_sprite_list.draw()
        else:
            self._draw_grid_background()

        if self.current_screen == "menu":
            self.title_text.draw()
            self.instruction_text.draw()
        elif self.current_screen == "game":
            # Draw room boundaries
            arcade.draw_lrbt_rectangle_outline(self.room_left, self.room_right, self.room_bottom, self.room_top, arcade.color.WHITE, 2)
            # Draw player
            arcade.draw_circle_filled(self.player_x, self.player_y, 10, arcade.color.BLUE)
            # Draw enemies
            for enemy in self.enemies:
                color = arcade.color.RED
                size = 10
                if enemy['type'] == 'boss':
                    color = arcade.color.PURPLE
                    size = 15
                elif enemy['type'] == 'turret':
                    color = arcade.color.ORANGE
                arcade.draw_circle_filled(enemy['x'], enemy['y'], size, color)
            # Draw bullets
            for bullet in self.bullets:
                arcade.draw_circle_filled(bullet['x'], bullet['y'], 3, arcade.color.YELLOW)
            # Draw enemy bullets
            for bullet in self.enemy_bullets:
                arcade.draw_circle_filled(bullet['x'], bullet['y'], 3, arcade.color.RED)
            # Draw upgrades
            for ux, uy, _ in self.upgrades:
                arcade.draw_circle_filled(ux, uy, 5, arcade.color.GREEN)
            # UI
            arcade.draw_text(f"Integrità del sistema: {self.player_health}", 10, HEIGHT - 30, arcade.color.WHITE, 18)
            arcade.draw_text(f"Distretto: {self.current_room + 1}", WIDTH - 150, HEIGHT - 30, arcade.color.WHITE, 18)
            arcade.draw_text(f"Upgrade: {len(self.upgrades_collected)}", 10, HEIGHT - 60, arcade.color.WHITE, 18)
            if self.sandevistan_cooldown > 0:
                arcade.draw_text(f"Sandevistan: {self.sandevistan_cooldown:.1f}s", 10, HEIGHT - 90, arcade.color.CYAN, 18)
            if self.sandevistan_active:
                arcade.draw_text("SANDEVISTAN ATTIVO", WIDTH/2, HEIGHT/2 + 50, arcade.color.CYAN, 24, anchor_x="center")
        elif self.current_screen == "game_over":
            self.game_over_text.draw()
        elif self.current_screen == "win":
            self.win_text.draw()

    def _draw_grid_background(self):
        """Sfondo secondario se png non carica."""
        for x in range(0, WIDTH, 40):
            arcade.draw_line(x, 0, x, HEIGHT, arcade.color.RED_DEVIL, 1)
        for y in range(0, HEIGHT, 40):
            arcade.draw_line(0, y, WIDTH, y, arcade.color.RED_DEVIL, 1)

    def on_key_press(self, symbol: int, modifiers: int):
        """Handle key presses."""
        if self.current_screen == "menu":
            if symbol == arcade.key.ENTER:
                self.current_screen = "game"
                self.reset_game()
        elif self.current_screen in ["game_over", "win"]:
            if symbol == arcade.key.R:
                self.current_screen = "menu"
        elif self.current_screen == "game":
            if symbol == arcade.key.ESCAPE:
                self.current_screen = "menu"
            elif symbol == arcade.key.LSHIFT and self.sandevistan_cooldown <= 0 and not self.sandevistan_active:
                self.sandevistan_active = True
                self.sandevistan_timer = 3
            else:
                self.keys_pressed.add(symbol)

    def on_key_release(self, symbol: int, modifiers: int):
        """Handle key releases."""
        if symbol in self.keys_pressed:
            self.keys_pressed.remove(symbol)

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        """Handle mouse clicks for shooting."""
        if self.current_screen == "game" and arcade.get_time() - self.last_shot > self.fire_rate:
            dx = x - self.player_x
            dy = y - self.player_y
            dist = (dx**2 + dy**2)**0.5
            if dist > 0:
                bullet = {
                    'x': self.player_x,
                    'y': self.player_y,
                    'dx': (dx / dist) * self.bullet_speed,
                    'dy': (dy / dist) * self.bullet_speed
                }
                self.bullets.append(bullet)
                self.last_shot = arcade.get_time()


if __name__ == "__main__":
    game = CyberpunkGame(WIDTH, HEIGHT, TITLE)
    arcade.run()
