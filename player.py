import arcade
import os


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
        # Ходьба
        for i in range(1, 9):
            sprite_path = f"images/player/walk_{i}.png"
            if os.path.exists(sprite_path):
                texture = arcade.load_texture(sprite_path)
                self.walk_sprites.append(texture)
                # Создаем зеркальную версию через transform
                texture_left = self.create_flipped_texture(texture)
                self.walk_sprites_left.append(texture_left)

        if self.walk_sprites and len(self.walk_sprites) < 8:
            while len(self.walk_sprites) < 8:
                self.walk_sprites.append(self.walk_sprites[-1])
                self.walk_sprites_left.append(self.walk_sprites_left[-1])

        # Прыжок
        for i in range(1, 5):
            sprite_path = f"images/player/jump_{i}.png"
            if os.path.exists(sprite_path):
                texture = arcade.load_texture(sprite_path)
                self.jump_sprites.append(texture)
                # Создаем зеркальную версию
                texture_left = self.create_flipped_texture(texture)
                self.jump_sprites_left.append(texture_left)

        if self.jump_sprites and len(self.jump_sprites) < 4:
            while len(self.jump_sprites) < 4:
                self.jump_sprites.append(self.jump_sprites[-1])
                self.jump_sprites_left.append(self.jump_sprites_left[-1])

        # Загрузка спрайта для бездействия
        idle_path = "images/player/idle.png"
        if os.path.exists(idle_path):
            self.idle_sprite = arcade.load_texture(idle_path)
            self.idle_sprite_left = self.create_flipped_texture(self.idle_sprite)
        else:
            self.idle_sprite = self.walk_sprites[0] if self.walk_sprites else None
            if self.idle_sprite:
                self.idle_sprite_left = self.create_flipped_texture(self.idle_sprite)
            else:
                self.idle_sprite_left = None

        # Для лестницы используем те же спрайты
        self.ladder_sprites = self.walk_sprites.copy()
        self.ladder_sprites_left = self.walk_sprites_left.copy()

    def create_flipped_texture(self, texture):
        """Создает зеркальную версию текстуры"""
        # Если текстура None, возвращаем None
        if texture is None:
            return None

        # Загружаем изображение и создаем зеркальную версию
        try:
            # Получаем путь к файлу текстуры (если доступен)
            # Альтернативный подход: используем PIL для отражения
            import PIL.Image
            from arcade import Texture

            # Открываем изображение
            image = PIL.Image.open(texture.file_path)
            # Зеркально отражаем по горизонтали
            flipped_image = image.transpose(PIL.Image.FLIP_LEFT_RIGHT)
            # Создаем новую текстуру
            flipped_texture = Texture(f"{texture.name}_flipped", flipped_image)
            return flipped_texture
        except Exception as e:
            print(f"Не удалось создать зеркальную текстуру: {e}")
            # В случае ошибки возвращаем оригинальную текстуру
            return texture

    def update(self, dt, is_moving, is_jumping, is_facing_right, is_on_ground, on_ladder=False,
               is_moving_on_ladder=False):
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

        # Определяем нужен ли анимированный кадр
        should_animate = False
        if on_ladder and is_moving_on_ladder:
            should_animate = True
        elif not on_ladder and ((is_moving and self.current_state == "walk") or
                                (is_jumping and self.current_state == "jump")):
            should_animate = True

        # Обновление кадра анимации
        if self.frame_timer >= self.frame_delay and should_animate:
            sprites_count = self.get_sprites_count()
            if sprites_count > 0:
                self.current_frame = (self.current_frame + 1) % sprites_count
                self.frame_timer = 0

        if not should_animate:
            self.current_frame = 0

    def get_sprites_count(self):
        """Возвращает количество спрайтов для текущего состояния"""
        if self.current_state == "walk":
            return len(self.walk_sprites)
        elif self.current_state == "jump":
            return len(self.jump_sprites)
        elif self.current_state == "ladder":
            return len(self.ladder_sprites)
        else:  # idle
            return 1

    def get_current_sprite(self):
        try:
            # Выбираем правильный набор спрайтов в зависимости от направления
            if self.current_state == "walk":
                sprites = self.walk_sprites if self.is_facing_right else self.walk_sprites_left
            elif self.current_state == "jump":
                sprites = self.jump_sprites if self.is_facing_right else self.jump_sprites_left
            elif self.current_state == "ladder":
                sprites = self.ladder_sprites if self.is_facing_right else self.ladder_sprites_left
            else:  # idle
                if self.is_facing_right:
                    sprites = [self.idle_sprite]
                else:
                    sprites = [self.idle_sprite_left]

            # Проверяем, что спрайты существуют
            if not sprites or all(s is None for s in sprites):
                # Возвращаем первый доступный спрайт в качестве запасного варианта
                return self.walk_sprites[0] if self.walk_sprites else None

            # Получаем текущий кадр
            frame_index = min(self.current_frame, len(sprites) - 1)
            return sprites[frame_index]

        except (IndexError, TypeError) as e:
            print(f"Ошибка получения спрайта: {e}")
            return None
        