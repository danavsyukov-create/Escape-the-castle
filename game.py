import arcade
from arcade.camera import Camera2D
from effects import EffectsManager
from player import PlayerAnimation
from config import config
import os
import time

SCREEN_W = 1280
SCREEN_H = 720
TITLE = "Escape the Castle"

GRAVITY = 4
MOVE_SPEED = 6
JUMP_SPEED = 20
LADDER_SPEED = 3

COYOTE_TIME = 0.08
JUMP_BUFFER = 0.12
MAX_JUMPS = 1

CAMERA_LERP = 0.12
WORLD_COLOR = arcade.color.SKY_BLUE

WORLD_WIDTH = 2000
WORLD_HEIGHT = 900
WORLD_LEFT = 0
WORLD_RIGHT = WORLD_WIDTH
WORLD_BOTTOM = 0
WORLD_TOP = WORLD_HEIGHT


class Level:
    def __init__(self):
        self.background_sprites = arcade.SpriteList()
        self.foreground_sprites = arcade.SpriteList()
        self.walls = arcade.SpriteList(use_spatial_hash=True)
        self.ladders = arcade.SpriteList()
        self.keys = arcade.SpriteList()
        self.doors = arcade.SpriteList()
        self.hazards = arcade.SpriteList()
        self.spawn_point = (0, 0)
        self.level_color = arcade.color.SKY_BLUE

    def load_background(self, filename, tile_scale=1.0):
        self.background_sprites.clear()
        if not os.path.exists(filename):
            return False

        texture = arcade.load_texture(filename)
        tile_width = texture.width * tile_scale
        tile_height = texture.height * tile_scale
        tiles_x = int(WORLD_WIDTH / tile_width) + 2
        tiles_y = int(WORLD_HEIGHT / tile_height) + 2

        for y in range(tiles_y):
            for x in range(tiles_x):
                pos_x = x * tile_width + tile_width / 2
                pos_y = y * tile_height + tile_height / 2
                bg_sprite = arcade.Sprite(texture, scale=tile_scale)
                bg_sprite.center_x = pos_x
                bg_sprite.center_y = pos_y
                self.background_sprites.append(bg_sprite)
        return True

    def setup(self):
        raise NotImplementedError("Subclasses must implement setup method")

    def draw(self):
        arcade.draw_lrbt_rectangle_filled(
            0, WORLD_WIDTH, 0, WORLD_HEIGHT, self.level_color
        )
        self.background_sprites.draw()
        self.walls.draw()
        self.ladders.draw()
        self.keys.draw()
        self.doors.draw()
        self.hazards.draw()

    def draw_foreground(self):
        self.foreground_sprites.draw()


class Level1(Level):
    def setup(self):
        self.spawn_point = (128, 256)
        self.level_color = (135, 206, 235)
        self.load_background('assets/Level_1.png', tile_scale=1.0)

        for x in range(0, 575, 64):
            wall = arcade.Sprite("images/wall.png", scale=0.1)
            wall.center_x = x
            wall.center_y = 400
            self.walls.append(wall)

        for x in range(0, WORLD_WIDTH, 64):
            floor_tile = arcade.Sprite("images/wall.png", scale=0.1)
            floor_tile.center_x = x
            floor_tile.center_y = 64
            self.walls.append(floor_tile)

        for y in range(65, 64 + 64 * 4, 64):
            ladder = arcade.Sprite("images/tiles/ladderMid.png", scale=0.5)
            ladder.center_x = 600
            ladder.center_y = y
            self.ladders.append(ladder)

        key = arcade.Sprite("images/key.png", scale=1)
        key.center_x = 250
        key.center_y = 200
        self.keys.append(key)

        door = arcade.Sprite("images/door.png", scale=0.25)
        door.center_x = 220
        door.center_y = 490
        self.doors.append(door)


class Level2(Level):
    def setup(self):
        self.spawn_point = (100, 150)
        self.level_color = (70, 130, 180)
        self.load_background('assets/Level_2.1.png', tile_scale=0.8)

        for x in range(0, WORLD_WIDTH, 64):
            floor_tile = arcade.Sprite("images/floor_1.png", scale=0.6)
            floor_tile.center_x = x
            floor_tile.center_y = 100
            self.walls.append(floor_tile)

        platform_config = [(1000, 350, 3), (800, 350, 2), (1300, 700, 3)]
        for x, y, width in platform_config:
            for i in range(width):
                platform = arcade.Sprite("images/floor_2.png", scale=0.6)
                platform.center_x = x + (i * 64)
                platform.center_y = y
                self.walls.append(platform)

        for y in range(200, 270, 64):
            ladder = arcade.Sprite("images/tiles/ladderMid.png", scale=0.5)
            ladder.center_x = 700
            ladder.center_y = y
            self.ladders.append(ladder)

        for y in range(500, 600, 64):
            ladder = arcade.Sprite("images/tiles/ladderMid.png", scale=0.5)
            ladder.center_x = 1150
            ladder.center_y = y
            self.ladders.append(ladder)

        key = arcade.Sprite("images/key.png", scale=1)
        key.center_x = 1400
        key.center_y = 750
        self.keys.append(key)

        door = arcade.Sprite("images/door.png", scale=0.25)
        door.center_x = 1200
        door.center_y = 70
        self.doors.append(door)


class Level3(Level):
    def setup(self):
        self.spawn_point = (150, 300)
        self.level_color = (95, 158, 160)
        self.load_background('assets/Level_3.png', tile_scale=2)

        for x in range(0, WORLD_WIDTH, 64):
            floor_tile = arcade.Sprite("images/floor_3.png", scale=2)
            floor_tile.center_x = x
            floor_tile.center_y = 50
            self.walls.append(floor_tile)

        platforms = [
            (480, 490, 6, "images/floor_3.png"),
            (720, 745, 2, "images/floor_3.png"),
            (1000, 625, 6, "images/floor_3.png"),
            (1500, 624, 3, "images/floor_3.png")
        ]

        for x, y, width, sprite_path in platforms:
            for i in range(width):
                platform = arcade.Sprite(sprite_path, scale=1.5)
                platform.center_x = x + (i * 64)
                platform.center_y = y
                self.walls.append(platform)

        for y in range(280, 350, 64):
            ladder = arcade.Sprite("images/tiles/ladderMid.png", scale=0.5)
            ladder.center_x = 400
            ladder.center_y = y
            self.ladders.append(ladder)

        for y in range(640, 645, 1):
            ladder = arcade.Sprite("images/tiles/ladderMid.png", scale=0.5)
            ladder.center_x = 850
            ladder.center_y = y
            self.ladders.append(ladder)

        key1 = arcade.Sprite("images/key.png", scale=1)
        key1.center_x = 720
        key1.center_y = 800
        self.keys.append(key1)

        key2 = arcade.Sprite("images/key.png", scale=1)
        key2.center_x = 1920
        key2.center_y = 150
        self.keys.append(key2)

        door = arcade.Sprite("images/door.png", scale=0.25)
        door.center_x = 1825
        door.center_y = 550
        self.doors.append(door)


class Level4(Level):
    def setup(self):
        self.spawn_point = (180, 350)
        self.level_color = (47, 79, 79)
        self.load_background('assets/Level_4.png', tile_scale=1.5)

        for x in range(0, WORLD_WIDTH, 64):
            floor_tile = arcade.Sprite("images/floor_4.png", scale=1)
            floor_tile.center_x = x
            floor_tile.center_y = 140
            self.walls.append(floor_tile)

        for x in range(0, WORLD_WIDTH, 64):
            floor_tile = arcade.Sprite("images/floor_4.png", scale=1)
            floor_tile.center_x = x
            floor_tile.center_y = 110
            self.walls.append(floor_tile)

        platforms = [
            (770, 350, 2, "images/floor_4.png"),
            (1060, 240, 1, "images/floor_4.png"),
            (600, 350, 1, "images/floor_4.png"),
            (320, 700, 3, "images/floor_4.png"),
            (150, 700, 1, "images/floor_4.png"),
            (600, 580, 1, "images/floor_4.png"),
            (800, 580, 2, "images/floor_4.png"),
            (921, 657, 3, "images/floor_4.png"),
            (1200, 657, 5, "images/floor_4.png"),
            (1500, 695, 10, "images/floor_4.png")
        ]

        for x, y, width, sprite_path in platforms:
            for i in range(width):
                platform = arcade.Sprite(sprite_path, scale=1)
                platform.center_x = x + (i * 64)
                platform.center_y = y
                self.walls.append(platform)

        ladder_positions = [(900, 350, 400), (540, 400, 700)]
        for x, y_start, y_end in ladder_positions:
            for y in range(y_start, y_end, 64):
                ladder = arcade.Sprite("images/tiles/ladderMid_2.png", scale=0.5)
                ladder.center_x = x
                ladder.center_y = y
                self.ladders.append(ladder)

        key_positions = [(1066, 200), (150, 750), (1980, 200)]
        for x, y in key_positions:
            key = arcade.Sprite("images/key.png", scale=1)
            key.center_x = x
            key.center_y = y
            self.keys.append(key)

        door = arcade.Sprite("images/door.png", scale=0.25)
        door.center_x = 1900
        door.center_y = 750
        self.doors.append(door)


class Platformer(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_W, SCREEN_H, TITLE, antialiasing=True)

        self.show_level_message = False
        self.level_message_timer = 0
        self.level_message_duration = 2.0
        self.game_start_time = time.time()
        self.game_completed = False
        self.total_game_time = 0

        self.end_background_sprites = arcade.SpriteList()
        self.instruction_panel_sprites = arcade.SpriteList()

        self.frame_delay = 0.15
        self.player_animation = PlayerAnimation()
        self.world_camera = Camera2D()
        self.gui_camera = Camera2D()
        self.player_list = arcade.SpriteList()
        self.engine = None
        self.effects = EffectsManager()
        self.left = self.right = self.up = self.down = self.jump_pressed = False
        self.jump_buffer_timer = 0.0
        self.time_since_ground = 999.0
        self.jumps_left = MAX_JUMPS
        self.was_jumping = False
        self.is_facing_right = True
        self.last_direction = 1
        self.player_animation = PlayerAnimation()
        self.current_level = None
        self.levels = []

        self.setup_levels()
        self.switch_to_level(0)
        self.setup()

        self.load_end_background()
        self.create_instruction_panel()

    def load_end_background(self):
        self.end_background_sprites.clear()
        try:
            if os.path.exists("assets/end.png"):
                texture = arcade.load_texture("assets/end.png")
                sprite = arcade.Sprite(texture, scale=1.0)

                tex_width = texture.width
                tex_height = texture.height

                scale_x = SCREEN_W / tex_width
                scale_y = SCREEN_H / tex_height

                scale = max(scale_x, scale_y)
                sprite.scale = scale

                sprite.center_x = SCREEN_W // 2
                sprite.center_y = SCREEN_H // 2

                self.end_background_sprites.append(sprite)
        except:
            self.create_default_end_background()

    def create_default_end_background(self):
        sprite = arcade.Sprite()
        sprite.color = (20, 40, 80)
        sprite.width = SCREEN_W
        sprite.height = SCREEN_H
        sprite.center_x = SCREEN_W // 2
        sprite.center_y = SCREEN_H // 2
        self.end_background_sprites.append(sprite)

    def create_instruction_panel(self):
        self.instruction_panel_sprites.clear()

        panel_sprite = arcade.Sprite()
        panel_sprite.color = (40, 40, 40, 200)
        panel_sprite.width = 500
        panel_sprite.height = 80
        panel_sprite.center_x = SCREEN_W // 2
        panel_sprite.center_y = 120
        self.instruction_panel_sprites.append(panel_sprite)

    def setup_levels(self):
        self.levels = [Level1(), Level2(), Level3(), Level4()]
        for level in self.levels:
            level.setup()

    def switch_to_level(self, index):
        if 0 <= index < len(self.levels):
            self.current_level = self.levels[index]
            self.setup()
            self.show_level_message = True
            self.level_message_timer = self.level_message_duration

    def setup(self):
        self.player_list.clear()
        self.player = arcade.Sprite("images/player/walk_1.png", scale=1)
        self.player.center_x, self.player.center_y = self.current_level.spawn_point
        self.player_list.append(self.player)
        self.engine = arcade.PhysicsEnginePlatformer(
            player_sprite=self.player,
            gravity_constant=GRAVITY,
            walls=self.current_level.walls,
            ladders=self.current_level.ladders
        )
        self.player.change_x = 0
        self.player.change_y = 0
        self.left = False
        self.right = False
        self.up = False
        self.down = False
        self.jump_pressed = False
        self.jump_buffer_timer = 0.0

    def draw_results_screen(self):
        arcade.set_background_color(arcade.color.BLACK)

        self.end_background_sprites.draw()

        minutes = self.total_game_time // 60
        seconds = self.total_game_time % 60

        arcade.draw_text(
            f"Время: {minutes:02d}:{seconds:02d}",
            SCREEN_W // 2, SCREEN_H // 2 + 50,
            arcade.color.GOLD, 48,
            font_name="Arial",
            anchor_x="center",
            bold=True
        )

        arcade.draw_text(
            "Поздравляем!",
            SCREEN_W // 2, SCREEN_H // 2 - 30,
            arcade.color.WHITE, 36,
            font_name="Arial",
            anchor_x="center",
            bold=True
        )

        arcade.draw_text(
            "Создатели игры:",
            SCREEN_W // 2, SCREEN_H // 2 - 90,
            arcade.color.LIGHT_YELLOW, 28,
            font_name="Arial",
            anchor_x="center"
        )

        arcade.draw_text(
            "Авсюков Даниил",
            SCREEN_W // 2, SCREEN_H // 2 - 140,
            arcade.color.LIGHT_BLUE, 32,
            font_name="Arial",
            anchor_x="center",
            bold=True
        )

        arcade.draw_text(
            "Третьяков Матвей",
            SCREEN_W // 2, SCREEN_H // 2 - 190,
            arcade.color.LIGHT_BLUE, 32,
            font_name="Arial",
            anchor_x="center",
            bold=True
        )

        self.instruction_panel_sprites.draw()

        arcade.draw_text(
            "Нажмите ESC для выхода",
            SCREEN_W // 2, 140,
            arcade.color.LIGHT_GRAY, 24,
            font_name="Arial",
            anchor_x="center",
            bold=True
        )

        arcade.draw_text(
            "Или R для начала новой игры",
            SCREEN_W // 2, 100,
            arcade.color.LIGHT_GRAY, 24,
            font_name="Arial",
            anchor_x="center",
            bold=True
        )

    def on_draw(self):
        self.clear()

        if self.game_completed:
            self.draw_results_screen()
            return

        self.world_camera.use()
        self.current_level.draw()
        self.player_list.draw()
        self.effects.draw()
        self.current_level.draw_foreground()
        self.gui_camera.use()
        self.draw_gui()
        if self.show_level_message:
            self.draw_level_message()

    def draw_gui(self):
        if not self.game_completed:
            current_time = time.time()
            total_time = int(current_time - self.game_start_time)
            minutes = total_time // 60
            seconds = total_time % 60

            arcade.draw_text(
                f"Время: {minutes:02d}:{seconds:02d}",
                SCREEN_W // 2, SCREEN_H - 40,
                arcade.color.WHITE, 24,
                font_name="Arial",
                anchor_x="center"
            )

    def draw_level_message(self):
        level_num = self.levels.index(self.current_level) + 1
        arcade.draw_text(
            f"Уровень {level_num}",
            SCREEN_W // 2, SCREEN_H // 2 + 10,
            arcade.color.WHITE, 48,
            font_name="Arial",
            anchor_x="center",
            anchor_y="center",
            bold=True
        )
        arcade.draw_text(
            f"Соберите все ключи и найдите дверь",
            SCREEN_W // 2, SCREEN_H // 2 - 30,
            arcade.color.LIGHT_GRAY, 20,
            font_name="Arial",
            anchor_x="center",
            anchor_y="center"
        )

    def on_key_press(self, key, modifiers):
        if self.game_completed:
            if key == arcade.key.ESCAPE:
                arcade.exit()
            elif key == arcade.key.R:
                self.game_completed = False
                self.game_start_time = time.time()
                self.switch_to_level(0)
            return

        if key in (arcade.key.LEFT, arcade.key.A):
            self.left = True
            self.is_facing_right = False
            self.last_direction = -1
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.right = True
            self.is_facing_right = True
            self.last_direction = 1
        elif key in (arcade.key.UP, arcade.key.W):
            self.up = True
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.down = True
        elif key == arcade.key.SPACE:
            self.jump_pressed = True
            self.jump_buffer_timer = JUMP_BUFFER
        elif key == arcade.key.R:
            self.switch_to_level(self.levels.index(self.current_level))
        elif key == arcade.key.N:
            next_level = (self.levels.index(self.current_level) + 1) % len(self.levels)
            self.switch_to_level(next_level)
        elif key == arcade.key.P:
            prev_level = (self.levels.index(self.current_level) - 1) % len(self.levels)
            self.switch_to_level(prev_level)
        elif key == arcade.key.ESCAPE:
            arcade.exit()

    def on_key_release(self, key, modifiers):
        if self.game_completed:
            return

        if key in (arcade.key.LEFT, arcade.key.A):
            self.left = False
            if not self.right:
                self.is_facing_right = (self.last_direction == 1)
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.right = False
            if not self.left:
                self.is_facing_right = (self.last_direction == 1)
        elif key in (arcade.key.UP, arcade.key.W):
            self.up = False
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.down = False
        elif key == arcade.key.SPACE:
            self.jump_pressed = False
            if self.player.change_y > 0:
                self.player.change_y *= 0.45

    def on_update(self, delta_time):
        if self.game_completed:
            return

        if self.show_level_message:
            self.level_message_timer -= delta_time
            if self.level_message_timer <= 0:
                self.show_level_message = False

        move = 0
        is_moving_horizontally = False
        is_moving_on_ladder = False

        if self.left and not self.right:
            move = -MOVE_SPEED
            is_moving_horizontally = True
            self.is_facing_right = False
            self.last_direction = -1
        elif self.right and not self.left:
            move = MOVE_SPEED
            is_moving_horizontally = True
            self.is_facing_right = True
            self.last_direction = 1
        elif not is_moving_horizontally:
            self.is_facing_right = (self.last_direction == 1)

        player_width = self.player.width
        next_x = self.player.center_x + move

        if next_x - player_width / 2 < WORLD_LEFT:
            move = 0
            self.player.center_x = WORLD_LEFT + player_width / 2
        elif next_x + player_width / 2 > WORLD_RIGHT:
            move = 0
            self.player.center_x = WORLD_RIGHT - player_width / 2

        self.player.change_x = move
        on_ladder = self.engine.is_on_ladder()

        if on_ladder:
            if self.up and not self.down:
                player_height = self.player.height
                next_y = self.player.center_y + LADDER_SPEED
                if next_y + player_height / 2 > WORLD_TOP:
                    self.player.change_y = 0
                    self.player.center_y = WORLD_TOP - player_height / 2
                else:
                    self.player.change_y = LADDER_SPEED
                is_moving_on_ladder = True
            elif self.down and not self.up:
                player_height = self.player.height
                next_y = self.player.center_y - LADDER_SPEED
                if next_y - player_height / 2 < WORLD_BOTTOM:
                    self.player.change_y = 0
                    self.player.center_y = WORLD_BOTTOM + player_height / 2
                else:
                    self.player.change_y = -LADDER_SPEED
                is_moving_on_ladder = True
            else:
                self.player.change_y = 0

        grounded = self.engine.can_jump(y_distance=6)
        is_walking = (is_moving_horizontally and grounded and not on_ladder and not self.was_jumping)
        self.effects.set_walk_sound(is_walking)

        if not on_ladder:
            if not self.was_jumping and self.player.change_y > 0:
                self.effects.create_jump_effect(self.player.center_x, self.player.center_y)
                self.was_jumping = True
            elif self.was_jumping and grounded:
                self.effects.create_land_effect(self.player.center_x, self.player.center_y)
                self.was_jumping = False

            if grounded:
                self.time_since_ground = 0
                self.jumps_left = MAX_JUMPS
            else:
                self.time_since_ground += delta_time

            if self.jump_buffer_timer > 0:
                self.jump_buffer_timer -= delta_time

            want_jump = self.jump_pressed or (self.jump_buffer_timer > 0)
            if want_jump:
                can_coyote = (self.time_since_ground <= COYOTE_TIME)
                if grounded or can_coyote:
                    self.engine.jump(JUMP_SPEED)
                    self.jump_buffer_timer = 0
        else:
            self.was_jumping = True
            self.time_since_ground = 0

        self.engine.update()

        player_height = self.player.height
        if self.player.center_y - player_height / 2 < WORLD_BOTTOM:
            self.player.center_y = WORLD_BOTTOM + player_height / 2
            self.player.change_y = 0
            if self.player.center_y < WORLD_BOTTOM + 100:
                self.player.center_x, self.player.center_y = self.current_level.spawn_point

        if self.player.center_y + player_height / 2 > WORLD_TOP:
            self.player.center_y = WORLD_TOP - player_height / 2
            self.player.change_y = 0

        is_jumping = (self.player.change_y > 0 and not on_ladder)

        self.player_animation.update(
            delta_time,
            is_moving_horizontally,
            is_jumping,
            self.is_facing_right,
            grounded,
            on_ladder,
            is_moving_on_ladder
        )

        current_sprite = self.player_animation.get_current_sprite()
        if current_sprite:
            self.player.texture = current_sprite
            self.player.scale_x = 1 if self.is_facing_right else -1

        self.effects.update(delta_time, self.player, grounded)

        keys_collected = arcade.check_for_collision_with_list(self.player, self.current_level.keys)
        for key in keys_collected:
            key.remove_from_sprite_lists()
            self.effects.play_key_sound()

        doors_collided = arcade.check_for_collision_with_list(self.player, self.current_level.doors)
        for door in doors_collided:
            if len(self.current_level.keys) == 0:
                current_index = self.levels.index(self.current_level)
                if current_index + 1 < len(self.levels):
                    self.switch_to_level(current_index + 1)
                else:
                    self.game_completed = True
                    self.total_game_time = int(time.time() - self.game_start_time)
                break

        target = (self.player.center_x, self.player.center_y)
        cx, cy = self.world_camera.position
        smooth = (
            cx + (target[0] - cx) * CAMERA_LERP,
            cy + (target[1] - cy) * CAMERA_LERP
        )
        half_w = self.world_camera.viewport_width / 2
        half_h = self.world_camera.viewport_height / 2
        cam_x = max(half_w, min(WORLD_WIDTH - half_w, smooth[0]))
        cam_y = max(half_h, min(WORLD_HEIGHT - half_h, smooth[1]))
        self.world_camera.position = (cam_x, cam_y)
        self.gui_camera.position = (SCREEN_W / 2, SCREEN_H / 2)


def main():
    game = Platformer()
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()