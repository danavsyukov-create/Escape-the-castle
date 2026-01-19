import arcade

class PlayerAnimation:
    def __init__(self):
        self.walk_sprites = []
        self.walk_sprites_left = []
        self.jump_sprites = []
        self.jump_sprites_left = []
        self.idle_sprite = None
        self.idle_sprite_left = None
        self.ladder_sprites = []
        self.ladder_sprites_left = []
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
            texture = arcade.load_texture(sprite_path)
            self.walk_sprites.append(texture)
            texture_left = self.create_flipped_texture(texture)
            self.walk_sprites_left.append(texture_left)

        if len(self.walk_sprites) < 8:
            while len(self.walk_sprites) < 8:
                self.walk_sprites.append(self.walk_sprites[-1])
                self.walk_sprites_left.append(self.walk_sprites_left[-1])

        for i in range(1, 5):
            sprite_path = f"images/player/jump_{i}.png"
            texture = arcade.load_texture(sprite_path)
            self.jump_sprites.append(texture)
            texture_left = self.create_flipped_texture(texture)
            self.jump_sprites_left.append(texture_left)

        if len(self.jump_sprites) < 4:
            while len(self.jump_sprites) < 4:
                self.jump_sprites.append(self.jump_sprites[-1])
                self.jump_sprites_left.append(self.jump_sprites_left[-1])

        self.idle_sprite = arcade.load_texture("images/player/idle.png")
        self.idle_sprite_left = self.create_flipped_texture(self.idle_sprite)
        self.ladder_sprites = self.walk_sprites.copy()
        self.ladder_sprites_left = self.walk_sprites_left.copy()

    def create_flipped_texture(self, texture):
        if texture is None:
            return None

        import PIL.Image
        from arcade import Texture

        try:
            image = PIL.Image.open(texture.file_path)
            flipped_image = image.transpose(PIL.Image.FLIP_LEFT_RIGHT)
            texture_name = f"flipped_{id(texture)}"
            flipped_texture = Texture(texture_name, flipped_image)
            return flipped_texture
        except Exception as e:
            return texture

    def update(self, dt, is_moving, is_jumping, is_facing_right, is_on_ground, on_ladder=False, is_moving_on_ladder=False):
        self.frame_timer += dt
        self.is_facing_right = is_facing_right
        self.on_ladder = on_ladder

        if on_ladder:
            self.current_state = "ladder"
        elif is_jumping or not is_on_ground:
            self.current_state = "jump"
        elif is_moving:
            self.current_state = "walk"
        else:
            self.current_state = "idle"

        should_animate = False
        if on_ladder and is_moving_on_ladder:
            should_animate = True
        elif not on_ladder and ((is_moving and self.current_state == "walk") or (is_jumping and self.current_state == "jump")):
            should_animate = True

        if self.frame_timer >= self.frame_delay and should_animate:
            sprites_count = self.get_sprites_count()
            if sprites_count > 0:
                self.current_frame = (self.current_frame + 1) % sprites_count
                self.frame_timer = 0

        if not should_animate:
            self.current_frame = 0

    def get_sprites_count(self):
        if self.current_state == "walk":
            return len(self.walk_sprites)
        elif self.current_state == "jump":
            return len(self.jump_sprites)
        elif self.current_state == "ladder":
            return len(self.ladder_sprites)
        else:
            return 1

    def get_current_sprite(self):
        if self.current_state == "walk":
            sprites = self.walk_sprites if self.is_facing_right else self.walk_sprites_left
        elif self.current_state == "jump":
            sprites = self.jump_sprites if self.is_facing_right else self.jump_sprites_left
        elif self.current_state == "ladder":
            sprites = self.ladder_sprites if self.is_facing_right else self.ladder_sprites_left
        else:
            sprites = [self.idle_sprite] if self.is_facing_right else [self.idle_sprite_left]

        frame_index = min(self.current_frame, len(sprites) - 1)
        return sprites[frame_index]