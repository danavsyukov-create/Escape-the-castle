import arcade
import os


class PlayerAnimation:
    def __init__(self):
        self.walk_sprites = []
        self.jump_sprites = []
        self.idle_sprite = None
        self.ladder_sprites = []
        self.load_sprites()
        self.current_state = "idle"
        self.current_frame = 0
        self.frame_timer = 0
        self.frame_delay = 0.15
        self.is_facing_right = True
        self.on_ladder = False

    def load_sprites(self):
            for i in range(1, 9):
                sprite_path = f"images/player/walk_{i}.png"
                if os.path.exists(sprite_path):
                    texture = arcade.load_texture(sprite_path)
                    self.walk_sprites.append(texture)

            if self.walk_sprites and len(self.walk_sprites) < 8:
                while len(self.walk_sprites) < 8:
                    self.walk_sprites.append(self.walk_sprites[-1])

            for i in range(1, 5):
                sprite_path = f"images/player/jump_{i}.png"
                if os.path.exists(sprite_path):
                    texture = arcade.load_texture(sprite_path)
                    self.jump_sprites.append(texture)

            if self.jump_sprites and len(self.jump_sprites) < 4:
                while len(self.jump_sprites) < 4:
                    self.jump_sprites.append(self.jump_sprites[-1])

            idle_path = "images/player/idle.png"
            if os.path.exists(idle_path):
                self.idle_sprite = arcade.load_texture(idle_path)
            else:
                self.idle_sprite = self.walk_sprites[0] if self.walk_sprites else None

            self.ladder_sprites = self.walk_sprites.copy()

    

    def update(self, dt, is_moving, is_jumping, is_facing_right, is_on_ground, on_ladder=False,
               is_moving_on_ladder=False):
        self.frame_timer += dt
        self.is_facing_right = is_facing_right
        self.on_ladder = on_ladder

        if on_ladder:
            self.current_state = "ladder"
            current_sprites = self.ladder_sprites
        elif is_jumping or not is_on_ground:
            self.current_state = "jump"
            current_sprites = self.jump_sprites
        elif is_moving:
            self.current_state = "walk"
            current_sprites = self.walk_sprites
        else:
            self.current_state = "idle"
            current_sprites = [self.idle_sprite] if self.idle_sprite else self.walk_sprites

        if not current_sprites or all(s is None for s in current_sprites):
            current_sprites = self.walk_sprites if self.walk_sprites else []

        current_sprites = [s for s in current_sprites if s is not None]

        if not current_sprites:
            return

        should_animate = False
        if on_ladder and is_moving_on_ladder:
            should_animate = True 
        elif not on_ladder and ((is_moving and self.current_state == "walk") or
                                (is_jumping and self.current_state == "jump")):
            should_animate = True

        if self.frame_timer >= self.frame_delay and len(current_sprites) > 1 and should_animate:
            self.current_frame = (self.current_frame + 1) % len(current_sprites)
            self.frame_timer = 0

        if not should_animate:
            self.current_frame = 0

    def get_current_sprite(self):
        if self.current_state == "walk" and self.walk_sprites:
            sprites = self.walk_sprites
        elif self.current_state == "jump" and self.jump_sprites:
            sprites = self.jump_sprites
        elif self.current_state == "ladder" and self.ladder_sprites:
            sprites = self.ladder_sprites
        elif self.current_state == "idle" and self.idle_sprite:
            sprites = [self.idle_sprite]
        else:
            sprites = self.walk_sprites if self.walk_sprites else []

        sprites = [s for s in sprites if s is not None]

        if not sprites:
            return None

        current_sprite = sprites[min(self.current_frame, len(sprites) - 1)]

        