import arcade
import math
import random
import time

WIDTH, HEIGHT = 800, 600
TITLE = "CyBERPUNK 1977"
BACKGROUND_IMAGE = "assets/background.png"
PLAYER_SPEED, BULLET_SPEED, ENEMY_SPEED, PLAYER_HEALTH = 5, 10, 2, 3


class CyberpunkGame(arcade.Window):
    def __init__(self, width: int, height: int, title: str):
        super().__init__(width, height, title)
        self.set_mouse_visible(False)
        self.current_screen = "menu"
        self.room_left, self.room_right, self.room_bottom, self.room_top = 50, WIDTH - 50, 50, HEIGHT - 50

        self.title_text = arcade.Text(TITLE, width / 2, height * 0.65, arcade.color.AQUA, 54, anchor_x="center", anchor_y="center")
        self.instruction_text = arcade.Text("Press ENTER to start", width / 2, height * 0.35, arcade.color.WHITE, 24, anchor_x="center", anchor_y="center")
        self.game_over_text = arcade.Text("Game Over! Press R to restart", width / 2, height / 2, arcade.color.RED, 32, anchor_x="center", anchor_y="center")
        self.win_text = arcade.Text("Missione Completata! Premi R per ricominciare", width / 2, height / 2, arcade.color.GREEN, 32, anchor_x="center", anchor_y="center")

        self.background = arcade.SpriteList()
        try:
            bg = arcade.Sprite(BACKGROUND_IMAGE)
            bg.center_x, bg.center_y, bg.width, bg.height = width / 2, height / 2, width, height
            self.background.append(bg)
        except Exception:
            pass

        self.rooms = [[
            {"x": 200, "y": 300, "type": "drone", "hp": 1},
            {"x": 600, "y": 400, "type": "drone", "hp": 1},
            {"x": 400, "y": 200, "type": "drone", "hp": 1},
            {"x": 100, "y": 500, "type": "drone", "hp": 1},
        ]]
        self.enemy_colors = {"drone": arcade.color.RED, "turret": arcade.color.ORANGE, "boss": arcade.color.PURPLE}
        self.reset_game()

    def _make_sprite(self, path: str, color: tuple[int, int, int], size: int = 20, scale: float = 0.05):
        try:
            return arcade.Sprite(path, scale=scale)
        except Exception:
            return arcade.SpriteSolidColor(size, size, color)

    def _shoot(self, origin_x: float, origin_y: float, target_x: float, target_y: float, speed: float, bag: list):
        dx, dy = target_x - origin_x, target_y - origin_y
        dist = math.hypot(dx, dy)
        if dist <= 0:
            return
        bag.append({"x": origin_x, "y": origin_y, "dx": dx / dist * speed, "dy": dy / dist * speed})

    def _move_bullets(self, bag: list):
        for b in bag[:]:
            b["x"] += b["dx"] * self.time_scale
            b["y"] += b["dy"] * self.time_scale
            if b["x"] < 0 or b["x"] > WIDTH or b["y"] < 0 or b["y"] > HEIGHT:
                bag.remove(b)

    def reset_game(self):
        self.current_room, self.player_health, self.player_speed, self.fire_rate = 0, PLAYER_HEALTH, PLAYER_SPEED, 0.05
        self.enemy_speed, self.bullet_speed, self.enemy_fire_rate = ENEMY_SPEED, BULLET_SPEED, 0.9
        self.keys_pressed, self.bullets, self.enemy_bullets, self.upgrades_collected = set(), [], [], []
        self.mouse_x, self.mouse_y, self.last_shot = WIDTH / 2, HEIGHT / 2, 0
        self.sandevistan_active, self.sandevistan_timer, self.sandevistan_cooldown, self.time_scale = False, 0, 0, 1.0
        self.player_sprite = self._make_sprite("assets/player.png", arcade.color.BLUE)
        self.enemy_sprites, self.upgrade_sprites, self.doors_open = arcade.SpriteList(), arcade.SpriteList(), False
        self.setup_room()

    def setup_room(self):
        if self.current_room >= len(self.rooms):
            self.current_screen = "win"
            return
        self.enemy_sprites = arcade.SpriteList()
        for e in self.rooms[self.current_room]:
            s = self._make_sprite(f"assets/enemy_{e['type']}.png", arcade.color.RED)
            s.center_x, s.center_y, s.type, s.hp = e["x"], e["y"], e["type"], e["hp"]
            s.next_shot_time = time.time() + random.uniform(0.1, 0.8)
            self.enemy_sprites.append(s)
        self.player_sprite.center_x, self.player_sprite.center_y = WIDTH / 2, HEIGHT / 2
        self.upgrade_sprites, self.enemy_bullets, self.doors_open = arcade.SpriteList(), [], False

    def on_update(self, dt: float):
        if self.current_screen != "game":
            return
        now = time.time()

        if self.sandevistan_active:
            self.time_scale, self.sandevistan_timer = 0.3, self.sandevistan_timer - dt
            if self.sandevistan_timer <= 0:
                self.sandevistan_active, self.sandevistan_cooldown, self.time_scale = False, 10, 1.0
        elif self.sandevistan_cooldown > 0:
            self.sandevistan_cooldown -= dt

        move = self.player_speed / self.time_scale if self.sandevistan_active else self.player_speed
        if arcade.key.W in self.keys_pressed:
            self.player_sprite.center_y += move
        if arcade.key.S in self.keys_pressed:
            self.player_sprite.center_y -= move
        if arcade.key.A in self.keys_pressed:
            self.player_sprite.center_x -= move
        if arcade.key.D in self.keys_pressed:
            self.player_sprite.center_x += move
        self.player_sprite.center_x = max(self.room_left, min(self.room_right, self.player_sprite.center_x))
        self.player_sprite.center_y = max(self.room_bottom, min(self.room_top, self.player_sprite.center_y))

        for s in self.enemy_sprites:
            dx, dy = self.player_sprite.center_x - s.center_x, self.player_sprite.center_y - s.center_y
            dist = math.hypot(dx, dy)
            if s.type in {"drone", "boss"} and dist > 0:
                speed = self.enemy_speed * self.time_scale * (0.5 if s.type == "boss" else 1.0)
                s.center_x += dx / dist * speed
                s.center_y += dy / dist * speed
            elif s.type == "cyborg":
                s.center_x += random.uniform(-1, 1) * self.enemy_speed * self.time_scale
                s.center_y += random.uniform(-1, 1) * self.enemy_speed * self.time_scale
            if s.type in {"turret", "boss"} and now >= s.next_shot_time:
                self._shoot(s.center_x, s.center_y, self.player_sprite.center_x, self.player_sprite.center_y, self.bullet_speed * (0.7 if s.type == "boss" else 0.5), self.enemy_bullets)
                s.next_shot_time = now + random.uniform(0.35, 0.7) if s.type == "boss" else now + random.uniform(self.enemy_fire_rate, self.enemy_fire_rate + 0.7)

        self._move_bullets(self.bullets)
        self._move_bullets(self.enemy_bullets)

        for b in self.bullets[:]:
            for s in self.enemy_sprites[:]:
                if abs(b["x"] - s.center_x) < 15 and abs(b["y"] - s.center_y) < 15:
                    s.hp -= 1
                    if s.hp <= 0:
                        self.enemy_sprites.remove(s)
                        up = self._make_sprite("assets/upgrade.png", arcade.color.GREEN, 10)
                        up.center_x, up.center_y = s.center_x, s.center_y
                        self.upgrade_sprites.append(up)
                    self.bullets.remove(b)
                    break

        for b in self.enemy_bullets[:]:
            if abs(b["x"] - self.player_sprite.center_x) < 13 and abs(b["y"] - self.player_sprite.center_y) < 13:
                self.player_health -= 1
                self.enemy_bullets.remove(b)
                if self.player_health <= 0:
                    self.current_screen = "game_over"

        hits = arcade.check_for_collision_with_list(self.player_sprite, self.enemy_sprites)
        if hits:
            for s in hits:
                self.enemy_sprites.remove(s)
            self.player_health -= len(hits)
            if self.player_health <= 0:
                self.current_screen = "game_over"

        for up in arcade.check_for_collision_with_list(self.player_sprite, self.upgrade_sprites):
            self.upgrade_sprites.remove(up)
            self.upgrades_collected.append("speed")
            self.player_speed += 1

        if not self.enemy_sprites and not self.doors_open:
            self.doors_open = True
            for _ in range(len(self.rooms[self.current_room])):
                up = self._make_sprite("assets/upgrade.png", arcade.color.GREEN, 10)
                up.center_x, up.center_y = random.uniform(self.room_left, self.room_right), random.uniform(self.room_bottom, self.room_top)
                self.upgrade_sprites.append(up)

        if self.doors_open and not self.enemy_sprites:
            self.current_screen = "win" if self.current_room >= len(self.rooms) - 1 else "game"
            if self.current_screen == "game":
                self.current_room += 1
                self.setup_room()

    def on_draw(self):
        self.clear()
        if self.background:
            self.background.draw()
        else:
            for x in range(0, WIDTH, 40):
                arcade.draw_line(x, 0, x, HEIGHT, arcade.color.RED_DEVIL, 1)
            for y in range(0, HEIGHT, 40):
                arcade.draw_line(0, y, WIDTH, y, arcade.color.RED_DEVIL, 1)

        if self.current_screen == "menu":
            self.title_text.draw()
            self.instruction_text.draw()
            return
        if self.current_screen == "game_over":
            self.game_over_text.draw()
            return
        if self.current_screen == "win":
            self.win_text.draw()
            return

        arcade.draw_lrbt_rectangle_outline(self.room_left, self.room_right, self.room_bottom, self.room_top, arcade.color.WHITE, 2)
        arcade.draw_circle_filled(self.player_sprite.center_x, self.player_sprite.center_y, 10, arcade.color.BLUE)
        for s in self.enemy_sprites:
            arcade.draw_circle_filled(s.center_x, s.center_y, 15 if s.type == "boss" else 10, self.enemy_colors.get(s.type, arcade.color.RED))
        for b in self.bullets:
            arcade.draw_circle_filled(b["x"], b["y"], 5, arcade.color.WHITE)
        for b in self.enemy_bullets:
            arcade.draw_circle_filled(b["x"], b["y"], 5, arcade.color.RED)
        for up in self.upgrade_sprites:
            arcade.draw_circle_filled(up.center_x, up.center_y, 5, arcade.color.GREEN)
        arcade.draw_text(f"Integrity: {self.player_health}", 10, HEIGHT - 30, arcade.color.WHITE, 18)
        arcade.draw_text(f"Room: {self.current_room + 1}", WIDTH - 110, HEIGHT - 30, arcade.color.WHITE, 18)
        arcade.draw_text(f"Upgrades: {len(self.upgrades_collected)}", 10, HEIGHT - 60, arcade.color.WHITE, 18)
        if self.sandevistan_cooldown > 0:
            arcade.draw_text(f"Sandevistan: {self.sandevistan_cooldown:.1f}s", 10, HEIGHT - 90, arcade.color.CYAN, 18)
        if self.sandevistan_active:
            arcade.draw_text("SANDEVISTAN ACTIVE", WIDTH / 2, HEIGHT / 2 + 50, arcade.color.CYAN, 24, anchor_x="center")

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        self.mouse_x, self.mouse_y = x, y

    def try_player_shoot(self, x: float, y: float):
        if self.current_screen != "game" or time.time() - self.last_shot <= self.fire_rate:
            return
        self._shoot(self.player_sprite.center_x, self.player_sprite.center_y, x, y, self.bullet_speed, self.bullets)
        self.last_shot = time.time()

    def on_key_press(self, symbol: int, modifiers: int):
        if self.current_screen == "menu" and symbol == arcade.key.ENTER:
            self.current_screen = "game"
            self.reset_game()
        elif self.current_screen in {"game_over", "win"} and symbol == arcade.key.R:
            self.current_screen = "menu"
        elif self.current_screen == "game":
            if symbol == arcade.key.ESCAPE:
                self.current_screen = "menu"
            elif symbol == arcade.key.LSHIFT and self.sandevistan_cooldown <= 0 and not self.sandevistan_active:
                self.sandevistan_active, self.sandevistan_timer = True, 3
            elif symbol == arcade.key.SPACE:
                self.try_player_shoot(self.mouse_x, self.mouse_y)
            else:
                self.keys_pressed.add(symbol)

    def on_key_release(self, symbol: int, modifiers: int):
        self.keys_pressed.discard(symbol)

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        self.try_player_shoot(x, y)


if __name__ == "__main__":
    CyberpunkGame(WIDTH, HEIGHT, TITLE)
    arcade.run()
