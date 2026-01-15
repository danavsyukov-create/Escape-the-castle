import arcade
import os
import random
import time

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.randint(2, 5)
        self.speed_x = random.uniform(-1.5, 1.5)
        self.speed_y = random.uniform(0.5, 2.0)
        self.lifetime = random.uniform(0.4, 0.8)
        self.max_lifetime = self.lifetime
        self.color = random.choice([(210, 180, 140, 255), (50, 50, 50, 255)])  # Четвертый элемент — альфа

    def update(self, dt):
        self.x += self.speed_x
        self.y += self.speed_y
        self.speed_y -= 0.1
        self.lifetime -= dt

    def draw(self):
        arcade.draw_circle_filled(self.x, self.y, self.size, self.color)


class EffectsManager:
    def __init__(self):
        self.particles = []
        self.trail_particles = []
        self.jump_sound = None
        self.walk_sound = None
        self.key_sound = None
        self.background_music = None
        self.screen_shake_timer = 0
        self.screen_shake_intensity = 0
        self.last_step_time = 0
        self.step_interval = 0.3
        self.should_play_walk_sound = False
        self.load_music()
        self.load_sounds()

    def load_music(self):
        """Загружаем фоновый музыкальный трек."""
        self.background_music = arcade.Sound(os.path.join("music", "music.mp3"))
        self.background_music.play(loop=True, volume=0.3)

    def load_sounds(self):
        """Загрузка звуков прыжка, ходьбы и подбора ключа."""
        self.jump_sound = arcade.Sound(os.path.join("music", "jump.mp3"))
        self.walk_sound = arcade.Sound(os.path.join("music", "walk.mp3"))
        self.key_sound = arcade.Sound(os.path.join("music", "key.mp3"))

    def play_key_sound(self):
        if self.key_sound:
            self.key_sound.play(volume=0.5)

    def set_walk_sound(self, should_play):
        self.should_play_walk_sound = should_play

    def update_walking_sound(self):
        if not self.should_play_walk_sound:
            return

        current_time = time.time()
        if self.walk_sound and current_time - self.last_step_time > self.step_interval:
            self.walk_sound.play(volume=0.1)
            self.last_step_time = current_time

    def create_jump_effect(self, x, y):
        for _ in range(10):
            particle = Particle(x, y - 25)
            self.particles.append(particle)

        for _ in range(6):
            particle = Particle(x, y - 25)
            particle.size = random.randint(1, 3)
            particle.speed_x = random.uniform(-0.3, 0.3)
            particle.speed_y = random.uniform(-0.2, 0.2)
            particle.lifetime = random.uniform(0.2, 0.4)
            particle.max_lifetime = particle.lifetime
            particle.color = random.choice([(128, 128, 128, 255), (0, 0, 0, 255)])  # Чёткий RGBA
            self.trail_particles.append(particle)

        self.screen_shake_timer = 0.08
        self.screen_shake_intensity = 2

        if self.jump_sound:
            self.jump_sound.play(volume=0.2)

    def create_land_effect(self, x, y):
        for _ in range(12):
            particle = Particle(x, y - 20)
            particle.speed_y = random.uniform(-1.0, 0.2)
            self.particles.append(particle)

        self.screen_shake_timer = 0.1
        self.screen_shake_intensity = 3

    def update(self, dt, player=None, grounded=False):
        self.update_walking_sound()

        for particle in self.particles[:]:
            particle.update(dt)
            if particle.lifetime <= 0:
                self.particles.remove(particle)

        for particle in self.trail_particles[:]:
            particle.update(dt)
            if particle.lifetime <= 0:
                self.trail_particles.remove(particle)

        if player and not grounded and abs(player.change_x) > 0:
            if random.random() < 0.2:
                particle = Particle(player.center_x, player.center_y - 25)
                particle.size = random.randint(1, 3)
                particle.speed_x = random.uniform(-0.3, 0.3)
                particle.speed_y = random.uniform(-0.2, 0.2)
                particle.lifetime = random.uniform(0.2, 0.4)
                particle.max_lifetime = particle.lifetime
                particle.color = random.choice([(128, 128, 128, 255), (0, 0, 0, 255)])  # Чёткий RGBA
                self.trail_particles.append(particle)

        if self.screen_shake_timer > 0:
            self.screen_shake_timer -= dt

    def draw(self):
        for particle in self.particles:
            particle.draw()
        for particle in self.trail_particles:
            particle.draw()

    def get_screen_shake(self):
        shake_x = 0
        shake_y = 0
        if self.screen_shake_timer > 0:
            max_shake = self.screen_shake_intensity * 0.7
            shake_x = random.uniform(-max_shake, max_shake)
            shake_y = random.uniform(-max_shake, max_shake)
        return shake_x, shake_y

    def stop(self):
        if self.background_music:
            self.background_music.stop()