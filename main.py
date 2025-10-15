import sys
import random
import math
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap

# --- Configuración ---
IMAGE_FILENAME = "a.png"  # Cambia si tu imagen tiene otro nombre
MAX_FOLLOWERS = 200
SPAWN_DISTANCE = 30
FPS = 60
DELAY_RANGE = (1000, 5000)
MIN_DISTANCE_FROM_MOUSE = 300
DUPLICATION_COOLDOWN = 1000
IMAGE_SIZE = (64, 64)

class Follower:
    def __init__(self, app_instance, x=None, y=None):
        self.app = app_instance
        if x is None and y is None:
            self.x = random.uniform(0, self.app.screen_width - IMAGE_SIZE[0])
            self.y = random.uniform(0, self.app.screen_height - IMAGE_SIZE[1])
        else:
            self.x = x
            self.y = y
        self.speed = random.uniform(1.0, 3.0)
        self.start_time = self.app.current_time()
        self.delay = random.uniform(DELAY_RANGE[0], DELAY_RANGE[1])

    def move_towards(self, mouse_x, mouse_y):
        current_time = self.app.current_time()
        if current_time - self.start_time > self.delay:
            dx = mouse_x - (self.x + IMAGE_SIZE[0] / 2)
            dy = mouse_y - (self.y + IMAGE_SIZE[1] / 2)
            dist = math.hypot(dx, dy)
            if dist > 0.5:
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed
            self.x = max(0, min(self.x, self.app.screen_width - IMAGE_SIZE[0]))
            self.y = max(0, min(self.y, self.app.screen_height - IMAGE_SIZE[1]))

    def touches_point(self, mouse_x, mouse_y):
        cx = self.x + IMAGE_SIZE[0] / 2
        cy = self.y + IMAGE_SIZE[1] / 2
        return math.hypot(cx - mouse_x, cy - mouse_y) <= SPAWN_DISTANCE

    def get_position(self):
        return int(self.x), int(self.y)

def get_distant_position(app_instance, mouse_x, mouse_y, is_first_new=False):
    if is_first_new:
        corners = [
            (0, 0),
            (0, app_instance.screen_height - IMAGE_SIZE[1]),
            (app_instance.screen_width - IMAGE_SIZE[0], 0),
            (app_instance.screen_width - IMAGE_SIZE[0], app_instance.screen_height - IMAGE_SIZE[1])
        ]
        x, y = random.choice(corners)
        if math.hypot(x - mouse_x, y - mouse_y) < MIN_DISTANCE_FROM_MOUSE:
            return get_distant_position(app_instance, mouse_x, mouse_y, is_first_new=True)
        return x, y
    else:
        while True:
            x = random.uniform(0, app_instance.screen_width - IMAGE_SIZE[0])
            y = random.uniform(0, app_instance.screen_height - IMAGE_SIZE[1])
            if math.hypot(x - mouse_x, y - mouse_y) > MIN_DISTANCE_FROM_MOUSE:
                return x, y

class TransparentWindow(QMainWindow):
    def __init__(self, app_instance):
        super().__init__()
        self.app = app_instance
        self.setWindowTitle("B1rus - Seguidores que duplican")

        # --- Ocultar barra de tareas, sin bordes, siempre arriba ---
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(0, 0, self.app.screen_width, self.app.screen_height)
        self.labels = []

        try:
            self.image = QPixmap(IMAGE_FILENAME).scaled(*IMAGE_SIZE)
            for follower in self.app.followers:
                label = QLabel(self)
                label.setPixmap(self.image)
                label.setGeometry(follower.get_position()[0], follower.get_position()[1], IMAGE_SIZE[0], IMAGE_SIZE[1])
                label.setAttribute(Qt.WA_TransparentForMouseEvents)
                label.show()
                self.labels.append(label)
        except Exception as e:
            print(f"Error al cargar la imagen: {e}")
            sys.exit(1)

    def update_followers(self):
        mouse_pos = self.cursor().pos()
        mouse_x, mouse_y = mouse_pos.x(), mouse_pos.y()
        for i, follower in enumerate(self.app.followers):
            follower.move_towards(mouse_x, mouse_y)
            x, y = follower.get_position()
            self.labels[i].setGeometry(x, y, IMAGE_SIZE[0], IMAGE_SIZE[1])

            if follower.touches_point(mouse_x, mouse_y):
                current_time = self.app.current_time()
                if (len(self.app.followers) < MAX_FOLLOWERS and
                    current_time - self.app.last_duplication_time > DUPLICATION_COOLDOWN):
                    is_first_new = (len(self.app.followers) == 1)
                    new_x, new_y = get_distant_position(self.app, mouse_x, mouse_y, is_first_new)
                    new_follower = Follower(self.app, x=new_x, y=new_y)
                    self.app.followers.append(new_follower)
                    label = QLabel(self)
                    label.setPixmap(self.image)
                    label.setGeometry(new_follower.get_position()[0], new_follower.get_position()[1], IMAGE_SIZE[0], IMAGE_SIZE[1])
                    label.setAttribute(Qt.WA_TransparentForMouseEvents)
                    label.show()
                    self.labels.append(label)
                    self.app.last_duplication_time = current_time

    def update(self):
        self.update_followers()
        self.repaint()

class App(QApplication):
    def __init__(self, sys_argv):
        super().__init__(sys_argv)
        self.screen_width = self.primaryScreen().size().width()
        self.screen_height = self.primaryScreen().size().height()
        self.followers = []
        self.initial_followers = 1
        self.last_duplication_time = 0
        for _ in range(self.initial_followers):
            self.followers.append(Follower(self))
        self.main_win = TransparentWindow(self)
        self.main_win.show()
        self.timer = QTimer()
        self.timer.timeout.connect(self.main_win.update)
        self.timer.start(int(1000 / FPS))

    def current_time(self):
        return int(time.time() * 1000)

if __name__ == '__main__':
    app = App(sys.argv)
    sys.exit(app.exec_())
