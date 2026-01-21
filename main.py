import sys
import os
import subprocess
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout,
                             QWidget, QLabel, QHBoxLayout, QDialog, QCheckBox,
                             QSlider, QMessageBox)
from PyQt6.QtGui import QIcon, QPalette, QColor, QPixmap
from PyQt6.QtCore import Qt, QUrl
from config import config  # Импортируем глобальную конфигурацию


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setFixedSize(400, 300)

        try:
            self.settings_background_image = QPixmap("images/settings.png")
            if self.settings_background_image.isNull():
                self.settings_background_image = QPixmap()
        except Exception as e:
            self.settings_background_image = QPixmap()

        # Главный layout
        main_layout = QVBoxLayout(self)

        # Создаем виджет для контента с прозрачным фоном
        content_widget = QWidget()
        content_widget.setStyleSheet("background: transparent;")

        content_layout = QVBoxLayout(content_widget)

        # Настройки
        self.music_checkbox = QCheckBox("Background Music", content_widget)
        content_layout.addWidget(self.music_checkbox)

        content_layout.addWidget(QLabel("Music Volume", content_widget))

        self.volume_slider = QSlider(Qt.Orientation.Horizontal, content_widget)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(int(config.music_volume * 100))
        content_layout.addWidget(self.volume_slider)

        content_layout.addWidget(QLabel("Sound Effects Volume", content_widget))

        self.effects_slider = QSlider(Qt.Orientation.Horizontal, content_widget)
        self.effects_slider.setRange(0, 100)
        self.effects_slider.setValue(int(config.sound_effects_volume * 100))
        content_layout.addWidget(self.effects_slider)

        self.sound_effects_checkbox = QCheckBox("Sound Effects", content_widget)
        content_layout.addWidget(self.sound_effects_checkbox)

        # Кнопки
        buttons_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK", content_widget)
        self.ok_button.clicked.connect(self.accept)

        self.cancel_button = QPushButton("Cancel", content_widget)
        self.cancel_button.clicked.connect(self.reject)

        buttons_layout.addWidget(self.ok_button)
        buttons_layout.addWidget(self.cancel_button)
        content_layout.addLayout(buttons_layout)

        # Добавляем отступы и растяжку
        content_layout.addStretch()
        content_widget.setLayout(content_layout)

        # Добавляем виджет с контентом в главный layout
        main_layout.addWidget(content_widget)

        # Устанавливаем начальные значения
        self.music_checkbox.setChecked(config.music_enabled)
        self.sound_effects_checkbox.setChecked(config.sound_effects_enabled)

        # Устанавливаем фон
        if not self.settings_background_image.isNull():
            self.setStyleSheet(f"""
                QDialog {{
                    background-image: url(images/settings.png);
                    background-position: center;
                    background-repeat: no-repeat;
                    background-origin: content;
                }}

                QCheckBox, QLabel, QSlider, QPushButton {{
                    background: transparent;
                }}
            """)
        else:
            self.setStyleSheet("""
                QDialog {
                    background-color: #2b2b2b;
                }

                QCheckBox, QLabel {
                    color: white;
                    background: transparent;
                }

                QPushButton {
                    background-color: #4a4a4a;
                    color: white;
                    border: 1px solid #5a5a5a;
                    border-radius: 5px;
                    padding: 8px;
                }

                QPushButton:hover {
                    background-color: #5a5a5a;
                }
            """)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Escape from the Castle")
        self.setGeometry(100, 100, 800, 600)

        try:
            self.background_image = QPixmap("assets/etc_background.png")
            self.dark_background_image = QPixmap("assets/etc_dark_background.jpg")
        except Exception as e:
            self.background_image = QPixmap()
            self.dark_background_image = QPixmap()

        self.background = QLabel(self)
        self.background.setPixmap(self.background_image.scaled(self.size(), Qt.AspectRatioMode.IgnoreAspectRatio,
                                                               Qt.TransformationMode.SmoothTransformation))
        self.background.setGeometry(0, 0, self.width(), self.height())

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        top_layout = QHBoxLayout()
        top_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        top_layout.setContentsMargins(10, 10, 10, 10)

        self.theme_button = QPushButton()
        self.theme_button.setFixedSize(80, 80)
        self.theme_button.clicked.connect(self.toggle_theme)
        top_layout.addWidget(self.theme_button)
        main_layout.addLayout(top_layout)

        self.title_label = QLabel("Escape The Castle")
        title_font = self.font()
        title_font.setPointSize(64)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("background: transparent;")

        title_container = QVBoxLayout()
        title_container.addStretch()
        title_container.addWidget(self.title_label)
        title_container.addStretch()
        main_layout.addLayout(title_container)

        self.play_button = QPushButton("Start it")
        self.play_button.setFixedSize(200, 100)
        self.play_button.setIcon(QIcon("images/start.jpg"))
        self.play_button.setIconSize(self.play_button.size())
        self.play_button.clicked.connect(self.start_game)

        self.settings_button = QPushButton("Settings")
        self.settings_button.setFixedSize(200, 100)
        self.settings_button.clicked.connect(self.open_settings)
        self.settings_button.setIcon(QIcon("images/settings.png"))
        self.settings_button.setIconSize(self.settings_button.size())

        self.exit_button = QPushButton("Leave it")
        self.exit_button.setFixedSize(200, 100)
        self.exit_button.clicked.connect(self.close)
        self.exit_button.setIcon(QIcon("images/exit.png"))
        self.exit_button.setIconSize(self.exit_button.size())

        buttons_container = QHBoxLayout()
        left_buttons_layout = QVBoxLayout()
        left_buttons_layout.setContentsMargins(50, 0, 0, 0)
        left_buttons_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        left_buttons_layout.addWidget(self.play_button)
        left_buttons_layout.addWidget(self.settings_button)
        left_buttons_layout.addWidget(self.exit_button)

        buttons_container.addLayout(left_buttons_layout)
        buttons_container.addStretch()
        main_layout.addLayout(buttons_container)
        main_layout.addStretch()

        self.apply_theme()

        self.music_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.music_player.setAudioOutput(self.audio_output)
        self.music_url = QUrl.fromLocalFile("music/background_music.mp3")
        self.music_player.setSource(self.music_url)
        self.audio_output.setVolume(config.music_volume)
        self.play_background_music()

    def start_game(self):
        """Запускает игру"""
        self.music_player.stop()
        self.hide()

        try:
            game_process = subprocess.Popen([sys.executable, "game.py"])
            game_process.wait()

            self.show()
            self.play_background_music()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось запустить игру:\n{str(e)}")
            self.show()
            self.play_background_music()

    def open_settings(self):
        settings_dialog = SettingsDialog(self)
        result = settings_dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            # Обновляем глобальные настройки
            config.update(
                music_enabled=settings_dialog.music_checkbox.isChecked(),
                sound_effects_enabled=settings_dialog.sound_effects_checkbox.isChecked(),
                music_volume=settings_dialog.volume_slider.value() / 100.0,
                sound_effects_volume=settings_dialog.effects_slider.value() / 100.0,
                dark_theme=config.dark_theme
            )

            # Обновляем музыку в главном меню
            self.audio_output.setVolume(config.music_volume)

            if config.music_enabled:
                self.play_background_music()
            else:
                self.music_player.stop()

            # Применяем тему
            self.apply_theme()

    def resizeEvent(self, event):
        self.background.setPixmap(self.background_image.scaled(self.size(), Qt.AspectRatioMode.IgnoreAspectRatio,
                                                               Qt.TransformationMode.SmoothTransformation))
        self.background.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)

    def toggle_theme(self):
        config.dark_theme = not config.dark_theme
        config.save()
        self.apply_theme()

    def apply_theme(self):
        try:
            if config.dark_theme:
                self.set_dark_theme()
                self.theme_button.setIcon(QIcon("images/moon.png"))
                self.theme_button.setIconSize(self.theme_button.size())
                if not self.dark_background_image.isNull():
                    self.background.setPixmap(
                        self.dark_background_image.scaled(self.size(), Qt.AspectRatioMode.IgnoreAspectRatio,
                                                          Qt.TransformationMode.SmoothTransformation))
                style = "color: white; font-size: 24px; font-weight: bold; background-color: #464646; border: 2px solid #5a5a5a; border-radius: 10px;"
                self.play_button.setStyleSheet(style)
                self.settings_button.setStyleSheet(style)
                self.exit_button.setStyleSheet(style)
                self.title_label.setStyleSheet("color: white; background: transparent;")
            else:
                self.set_light_theme()
                self.theme_button.setIcon(QIcon("images/sun.png"))
                self.theme_button.setIconSize(self.theme_button.size())
                if not self.background_image.isNull():
                    self.background.setPixmap(
                        self.background_image.scaled(self.size(), Qt.AspectRatioMode.IgnoreAspectRatio,
                                                     Qt.TransformationMode.SmoothTransformation))
                style = "color: black; font-size: 24px; font-weight: bold; background-color: #d3d3d3; border: 2px solid #a0a0a0; border-radius: 10px;"
                self.play_button.setStyleSheet(style)
                self.settings_button.setStyleSheet(style)
                self.exit_button.setStyleSheet(style)
                self.title_label.setStyleSheet("color: black; background: transparent;")
        except Exception as e:
            print(f"Error applying theme: {e}")

    def set_dark_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Button, QColor(70, 70, 70))
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        self.setPalette(palette)

    def set_light_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, Qt.GlobalColor.lightGray)
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.black)
        palette.setColor(QPalette.ColorRole.Base, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.AlternateBase, Qt.GlobalColor.lightGray)
        palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.black)
        palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.black)
        palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.black)
        palette.setColor(QPalette.ColorRole.Button, Qt.GlobalColor.lightGray)
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.black)
        self.setPalette(palette)

    def play_background_music(self):
        if config.music_enabled:
            self.music_player.play()


if __name__ == '__main__':
    os.environ['PYTHONIOENCODING'] = 'UTF-8'
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())