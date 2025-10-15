import sys
import random
import math
import time  # Importado para manejar el tiempo
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtCore import QTimer, Qt, QPoint
from PyQt5.QtGui import QPixmap, QImage

# --- Configuración ---
IMAGE_FILENAME = "a.png"  # Cambia aquí el nombre si tu imagen se llama distinto
MAX_FOLLOWERS = 200  # Tope de seguidores
SPAWN_DISTANCE = 30  # Distancia mínima para tocar el mouse
FPS = 60  # Usado para el timer
DELAY_RANGE = (1000, 5000)  # Rango de retraso inicial en ms
MIN_DISTANCE_FROM_MOUSE = 300  # Distancia mínima para posiciones "lejas"
DUPLICATION_COOLDOWN = 1000  # Cooldown para duplicaciones en ms
IMAGE_SIZE = (64, 64)  # Tamaño de la imagen

class Follower:
    def __init__(self, x=None, y=None):
        if x is None and y is None:
            self.x = random.uniform(0, app.screen_width - IMAGE_SIZE[0])
            self.y = random.uniform(0, app.screen_height - IMAGE_SIZE[1])
        else:
            self.x = x
            self.y = y
        self.speed = random.uniform(1.0, 3.0)
        self.start_time = app.current_time()  # Tiempo de creación en milisegundos
        self.delay = random.uniform(DELAY_RANGE[0], DELAY_RANGE[1])  # Retraso aleatorio

    def move_towards(self, mouse_x, mouse_y):
        current_time = app.current_time()
        if current_time - self.start_time > self.delay:
            dx = mouse_x - (self.x + IMAGE_SIZE[0] / 2)
            dy = mouse_y - (self.y + IMAGE_SIZE[1] / 2)
            dist = math.hypot(dx, dy)
            if dist > 0.5:
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed
            # Limitar dentro de la pantalla
            self.x = max(0, min(self.x, app.screen_width - IMAGE_SIZE[0]))
            self.y = max(0, min(self.y, app.screen_height - IMAGE_SIZE[1]))

    def touches_point(self, mouse_x, mouse_y):
        cx = self.x + IMAGE_SIZE[0] / 2
        cy = self.y + IMAGE_SIZE[1] / 2
        return math.hypot(cx - mouse_x, cy - mouse_y) <= SPAWN_DISTANCE

    def get_position(self):
        return int(self.x), int(self.y)

# Función para obtener una posición lejana del mouse
def get_distant_position(mouse_x, mouse_y, is_first_new=False):
    if is_first_new:
        corners = [
            (0, 0),
            (0, app.screen_height - IMAGE_SIZE[1]),
            (app.screen_width - IMAGE_SIZE[0], 0),
            (app.screen_width - IMAGE_SIZE[0], app.screen_height - IMAGE_SIZE[1])
        ]
        x, y = random.choice(corners)
        if math.hypot(x - mouse_x, y - mouse_y) < MIN_DISTANCE_FROM_MOUSE:
            return get_distant_position(mouse_x, mouse_y, is_first_new=True)
        return x, y
    else:
        while True:
            x = random.uniform(0, app.screen_width - IMAGE_SIZE[0])
            y = random.uniform(0, app.screen_height - IMAGE_SIZE[1])
            if math.hypot(x - mouse_x, y - mouse_y) > MIN_DISTANCE_FROM_MOUSE:
                return x, y

class App(QApplication):
    def __init__(self, sys_argv):
        super().__init__(sys_argv)
        self.main_win = TransparentWindow()
        self.screen_width = self.primaryScreen().size().width()
        self.screen_height = self.primaryScreen().size().height()
        self.followers = []  # Lista de seguidores
        self.initial_followers = 1
        self.last_duplication_time = 0
        for _ in range(self.initial_followers):
            self.followers.append(Follower())
        self.timer = QTimer()
        self.timer.timeout.connect(self.main_win.update)  # Corregido: Conectar a main_win.update
        self.timer.start(1000 / FPS)  # Actualizar a FPS frames por segundo

    def current_time(self):  # Corregido: Usar time.time() para obtener el tiempo en ms
        return int(time.time() * 1000)  # Retorna el tiempo actual en milisegundos

class TransparentWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("B1rus - Seguidores que duplican")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)  # Sin bordes, siempre arriba
        self.setAttribute(Qt.WA_TranslucentBackground)  # Fondo transparente
        self.setGeometry(0, 0, app.screen_width, app.screen_height)  # Full screen
        self.labels = []  # Lista de etiquetas para los followers

        try:
            # Cargar imagen
            self.image = QPixmap(IMAGE_FILENAME).scaled(*IMAGE_SIZE)
            for follower in app.followers:
                label = QLabel(self)
                label.setPixmap(self.image)
                label.setGeometry(follower.get_position()[0], follower.get_position()[1], IMAGE_SIZE[0], IMAGE_SIZE[1])
                label.setAttribute(Qt.WA_TransparentForMouseEvents)  # Ignorar clics
                label.show()
                self.labels.append(label)
        except Exception as e:
            print(f"Error al cargar la imagen: {e}")
            sys.exit(1)

    def update_followers(self):
        mouse_pos = self.cursor().pos()  # Posición del mouse (usar self.cursor() para precisión)
        mouse_x, mouse_y = mouse_pos.x(), mouse_pos.y()
        for i, follower in enumerate(app.followers):
            follower.move_towards(mouse_x, mouse_y)
            x, y = follower.get_position()
            self.labels[i].setGeometry(x, y, IMAGE_SIZE[0], IMAGE_SIZE[1])
            if follower.touches_point(mouse_x, mouse_y):
                current_time = app.current_time()
                if (len(app.followers) < MAX_FOLLOWERS and 
                    current_time - app.last_duplication_time > DUPLICATION_COOLDOWN):
                    is_first_new = (len(app.followers) == 1)
                    new_x, new_y = get_distant_position(mouse_x, mouse_y, is_first_new)
                    new_follower = Follower(x=new_x, y=new_y)
                    app.followers.append(new_follower)
                    label = QLabel(self)
                    label.setPixmap(self.image)
                    label.setGeometry(new_follower.get_position()[0], new_follower.get_position()[1], IMAGE_SIZE[0], IMAGE_SIZE[1])
                    label.setAttribute(Qt.WA_TransparentForMouseEvents)
                    label.show()
                    self.labels.append(label)
                    app.last_duplication_time = current_time

    def update(self):  # Método de actualización
        self.update_followers()
        self.repaint()  # Forzar repintado

if __name__ == '__main__':
    app = App(sys.argv)
    sys.exit(app.exec_())
