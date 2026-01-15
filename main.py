import arcade
from arcade.camera import Camera2D
from effects import EffectsManager
from player import PlayerAnimation
import os

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


class Level:
    def __init__(self):
        self.background_sprites = arcade.SpriteList()
        self.walls = arcade.SpriteList(use_spatial_hash=True)
        self.ladders = arcade.SpriteList()
        self.keys = arcade.SpriteList()
        self.doors = arcade.SpriteList()
        self.hazards = arcade.SpriteList()
        self.spawn_point = (0, 0)

    def setup(self):
        raise NotImplementedError("Subclasses must implement setup method")

    def draw(self):
        self.background_sprites.draw()
        self.walls.draw()
        self.ladders.draw()
        self.keys.draw()
        self.doors.draw()
        self.hazards.draw()


class Level1(Level):
    def setup(self):
        self.spawn_point = (128, 256)
        for x in range(0, 575, 64):
            wall = arcade.Sprite("images/wall.png", scale=0.1)
            wall.center_x = x
            wall.center_y = 400
            self.walls.append(wall)

        for x in range(0, 5000, 64):
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
        self.spawn_point = (100, 250)
        for x in range(0, 5000, 64):
            floor_tile = arcade.Sprite("images/wall.png", scale=0.1)
            floor_tile.center_x = x
            floor_tile.center_y = 200
            self.walls.append(floor_tile)

        door = arcade.Sprite("images/door.png", scale=0.25)
        door.center_x = 500
        door.center_y = 400
        self.doors.append(door)


class Platformer(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_W, SCREEN_H, TITLE, antialiasing=True)
        self.frame_delay = 0.15
        self.player_animation = PlayerAnimation()
        self.world_camera = Camera2D()
        self.gui_camera = Camera2D()
        self.background_texture = None
        self.player_list = arcade.SpriteList()
        self.engine = None
        self.left = self.right = self.up = self.down = self.jump_pressed = False
        self.jump_buffer_timer = 0.0
        self.time_since_ground = 999.0
        self.jumps_left = MAX_JUMPS
        self.was_jumping = False
        self.is_facing_right = True
        self.last_direction = 1
        self.effects = EffectsManager()
        self.player_animation = PlayerAnimation()
        self.current_level = None
        self.levels = []
        self.setup_levels()
        self.switch_to_level(0)
        self.setup()

    def setup_levels(self):
        self.levels = [Level1(), Level2()]
        for level in self.levels:
            level.setup()

    def switch_to_level(self, index):
        if 0 <= index < len(self.levels):
            self.current_level = self.levels[index]
            self.setup()

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

    def on_draw(self):
        self.clear(WORLD_COLOR)
        self.world_camera.use()
        self.current_level.draw()
        self.player_list.draw()
        self.effects.draw()
        self.gui_camera.use()

    def on_key_press(self, key, modifiers):
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

    def on_key_release(self, key, modifiers):
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

        self.player.change_x = move

        on_ladder = self.engine.is_on_ladder()

        if on_ladder:
            if self.up and not self.down:
                self.player.change_y = LADDER_SPEED
                is_moving_on_ladder = True
            elif self.down and not self.up:
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

        doors_collided = arcade.check_for_collision_with_list(self.player, self.current_level.doors)
        for door in doors_collided:
            if len(self.current_level.keys) == 0:
                new_level_index = (self.levels.index(self.current_level) + 1) % len(self.levels)
                self.switch_to_level(new_level_index)
                self.setup()
                break

        target = (self.player.center_x, self.player.center_y)
        cx, cy = self.world_camera.position
        smooth = (
            cx + (target[0] - cx) * CAMERA_LERP,
            cy + (target[1] - cy) * CAMERA_LERP
        )
        half_w = self.world_camera.viewport_width / 2
        half_h = self.world_camera.viewport_height / 2
        world_w = 2000
        world_h = 900
        cam_x = max(half_w, min(world_w - half_w, smooth[0]))
        cam_y = max(half_h, min(world_h - half_h, smooth[1]))
        self.world_camera.position = (cam_x, cam_y)
        self.gui_camera.position = (SCREEN_W / 2, SCREEN_H / 2)


def main():
    game = Platformer()
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()