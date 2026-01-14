import arcade
from arcade.camera import Camera2D
from effects import EffectsManager
from player import PlayerAnimation
import random
import os

SCREEN_W = 1280
SCREEN_H = 720
TITLE = "Escape the castle"

GRAVITY = 4
MOVE_SPEED = 6
JUMP_SPEED = 20
LADDER_SPEED = 3

COYOTE_TIME = 0.08
JUMP_BUFFER = 0.12
MAX_JUMPS = 1

CAMERA_LERP = 0.12
WORLD_COLOR = arcade.color.SKY_BLUE


class Platformer(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_W, SCREEN_H, TITLE, antialiasing=True)

        self.world_camera = Camera2D()
        self.gui_camera = Camera2D()

        self.background_texture = None
        self.background_sprites = arcade.SpriteList()

        self.player_list = arcade.SpriteList()
        self.walls = arcade.SpriteList(use_spatial_hash=True)
        self.ladders = arcade.SpriteList()
        self.key1 = arcade.SpriteList()
        self.hazards = arcade.SpriteList()
        self.door = arcade.SpriteList()

        self.player = None
        self.spawn_point = (128, 256)

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

    def setup(self):
        self.load_background()

        self.player_list.clear()
        self.player = arcade.Sprite("images/player/walk_1.png", scale=1)

        self.player.center_x, self.player.center_y = self.spawn_point
        self.player_list.append(self.player)

        for x in (-500, 220):
            c = arcade.Sprite("images/door.png", scale=0.25)
            c.center_x = x
            c.center_y = 490
            self.door.append(c)

        for z in range(0, 575, 64):
            tile = arcade.Sprite("images/wall.png", scale=0.1)
            tile.center_x = z
            tile.center_y = 400
            self.walls.append(tile)

        for x in range(0, 5000, 64):
            tile = arcade.Sprite("images/wall.png", scale=0.1)
            tile.center_x = x
            tile.center_y = 64
            self.walls.append(tile)

        for y in range(65, 64 + 64 * 4, 64):
            l = arcade.Sprite("images/tiles/ladderMid.png", scale=0.5)
            l.center_x = 600
            l.center_y = y
            self.ladders.append(l)

        for x in (-500, 1250):
            c = arcade.Sprite("images/key.png", scale=1)
            c.center_x = x
            c.center_y = 150
            self.key1.append(c)

        self.engine = arcade.PhysicsEnginePlatformer(
            player_sprite=self.player,
            gravity_constant=GRAVITY,
            walls=self.walls,
            ladders=self.ladders
        )

        self.jump_buffer_timer = 0
        self.time_since_ground = 999.0
        self.jumps_left = MAX_JUMPS

        self.was_jumping = False
        self.is_facing_right = True
        self.last_direction = 1

    def load_background(self):
        background_paths = [
            "assets/room.png"]

        for path in background_paths:
            if os.path.exists(path):
                try:
                    self.background_texture = arcade.load_texture(path)
                    self.create_tiled_background()
                    return
                except Exception as e:
                    print()

    def create_tiled_background(self):
        if not self.background_texture:
            return

        self.background_sprites.clear()

        world_width = 2000
        world_height = 900

        tex_width = self.background_texture.width
        tex_height = self.background_texture.height

        tiles_x = world_width // tex_width + 2
        tiles_y = world_height // tex_height + 2

        for x in range(tiles_x):
            for y in range(tiles_y):
                sprite = arcade.Sprite()
                sprite.texture = self.background_texture
                # Позиционируем тайлы
                sprite.center_x = x * tex_width + tex_width // 2
                sprite.center_y = y * tex_height + tex_height // 2
                self.background_sprites.append(sprite)


    def on_draw(self):
        self.clear()

        self.world_camera.use()

        if self.background_sprites:
            self.background_sprites.draw()
        elif self.background_texture:
            world_width = 2000
            world_height = 900
            tex_width = self.background_texture.width
            tex_height = self.background_texture.height

            for x in range(0, world_width + tex_width, tex_width):
                for y in range(0, world_height + tex_height, tex_height):
                    arcade.draw_texture_rectangle(
                        x + tex_width // 2,
                        y + tex_height // 2,
                        tex_width, tex_height,
                        self.background_texture
                    )

        self.walls.draw()
        self.ladders.draw()
        self.door.draw()
        self.key1.draw()
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

    def on_update(self, dt: float):
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
                self.time_since_ground += dt

            if self.jump_buffer_timer > 0:
                self.jump_buffer_timer -= dt

            want_jump = self.jump_pressed or (self.jump_buffer_timer > 0)

            if want_jump:
                can_coyote = (self.time_since_ground <= COYOTE_TIME)
                if grounded or can_coyote:
                    self.engine.jump(JUMP_SPEED)
                    self.jump_buffer_timer = 0
        else:
            self.was_jumping = False
            self.time_since_ground = 0

        self.engine.update()

        is_jumping = (self.player.change_y != 0 or not grounded) and not on_ladder
        self.player_animation.update(dt, is_moving_horizontally, is_jumping,
                                     self.is_facing_right, grounded, on_ladder, is_moving_on_ladder)

        current_sprite = self.player_animation.get_current_sprite()
        if current_sprite:
            self.player.texture = current_sprite

        self.effects.update(dt, self.player, grounded)

        for coin in arcade.check_for_collision_with_list(self.player, self.key1):
            coin.remove_from_sprite_lists()

        if arcade.check_for_collision_with_list(self.player, self.hazards):
            self.player.center_x, self.player.center_y = self.spawn_point
            self.player.change_x = self.player.change_y = 0
            self.time_since_ground = 999
            self.jumps_left = MAX_JUMPS

        target = (self.player.center_x, self.player.center_y)
        cx, cy = self.world_camera.position
        smooth = (cx + (target[0] - cx) * CAMERA_LERP,
                  cy + (target[1] - cy) * CAMERA_LERP)

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