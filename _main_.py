import sys
import random
from datetime import datetime
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel,QMenu, QAction,  QMessageBox)

from PetDataHandler import PetDataHandler
from PsychChatWindow import PsychChatWindow

# ==================== 桌宠主程序 ====================
class DesktopPet(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()
        self.init_animation()

        self.click_start_pos = None
        self.click_threshold = 5
        self.dragging = False

        self.chat_window = None
        self.game = None

        self.data_handler = PetDataHandler()
        self.session_id = self.data_handler.start_session()

        self.action_timer = QTimer(self)
        self.action_timer.timeout.connect(self.random_action)
        self.action_timer.start(10000)

        self.click_timer = QTimer()
        self.click_timer.setSingleShot(True)
        self.click_timer.timeout.connect(self.handle_successful_click)

        # 右键菜单
        self.menu = QMenu(self)
        self.chat_action = QAction("和小忆说说话", self)
        self.chat_action.triggered.connect(self.show_chat_window)
        self.menu.addAction(self.chat_action)
        self.menu.addSeparator()
        self.game_action = QAction("玩玩小游戏", self)
        self.game_action.triggered.connect(self.random_appear_game)
        self.menu.addAction(self.game_action)
        self.menu.addSeparator()
        self.exit_action = QAction("退出", self)
        self.exit_action.triggered.connect(self.close)
        self.menu.addAction(self.exit_action)

    def init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(1200, 800, 150, 150)

    def closeEvent(self, event):
        if self.chat_window:
            self.chat_window.close()
        self.data_handler.end_session()
        event.accept()

    def init_animation(self):
        self.animation_label = QLabel(self)
        self.animations = ["img/stand.gif", "img/walk.gif", "img/sleep.gif"]
        self.current_animation = None
        self.random_action()

    def stand_action(self):
        self.play_animation("img/stand.gif")

    def random_action(self):
        new_animation = random.choice(self.animations)
        if new_animation != self.current_animation:
            self.play_animation(new_animation)

    def play_animation(self, gif_path):
        movie = QMovie(gif_path)
        self.animation_label.setMovie(movie)
        movie.start()
        self.current_animation = gif_path

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.click_start_pos = event.pos()  # 记录点击起始位置
            self.dragging = False
            self.drag_start_pos = event.globalPos() - self.pos()
            self.play_animation("img/catch.gif")
        elif event.button() == Qt.RightButton:
            self.menu.exec_(self.mapToGlobal(event.pos()))

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.click_start_pos:
            # 计算移动距离
            move_distance = (event.pos() - self.click_start_pos).manhattanLength()

            if move_distance > self.click_threshold or self.dragging:
                # 超过阈值视为拖动
                self.dragging = True
                self.move(event.globalPos() - self.drag_start_pos)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.click_start_pos:
            move_distance = (event.pos() - self.click_start_pos).manhattanLength()

            if not self.dragging and move_distance <= self.click_threshold:
                pass  # 视为有效点击

            self.click_start_pos = None
            self.dragging = False
            self.stand_action()

    def show_chat_window(self):
        if not self.chat_window:
            self.chat_window = PsychChatWindow()
        pet_pos = self.pos()
        pet_width = self.width()
        chat_x = pet_pos.x() + pet_width + 10  # 右边留 10px 间距
        chat_y = pet_pos.y()
        self.chat_window.move(chat_x, chat_y)
        self.chat_window.show()






class PetGame_random_appear():
    def __init__(self, pet):
        self.pet = pet
        self.score = 0
        self.time_left = 30
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)

        # 分数显示标签
        self.score_label = QLabel(pet)
        self.score_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: bold;
                background: rgba(0,0,0,0.5);
                padding: 5px;
                border-radius: 10px;
            }
        """)
        self.score_label.move(10, 10)
        self.update_score()

        # 倒计时标签
        self.time_label = QLabel(pet)
        self.time_label.setStyleSheet(self.score_label.styleSheet())
        self.time_label.move(pet.width() - 100, 10)
        self.update_time()

    def update_score(self):
        self.score_label.setText(f"得分: {self.score}")
        self.score_label.adjustSize()

    def update_time(self):
        self.time_label.setText(f"剩余: {self.time_left}s")
        self.time_label.adjustSize()

    def update_timer(self):
        self.time_left -= 1
        self.update_time()
        if self.time_left <= 0:
            self.timer.stop()
            QMessageBox.information(self.pet, "游戏结束", f"最终得分: {self.score}")

    def start_game(self):
        self.score = 0
        self.time_left = 30
        self.update_score()
        self.update_time()
        self.timer.start(3000)  # 每秒更新
        self.move_pet_randomly()

    def move_pet_randomly(self):
        # 获取屏幕可用区域
        screen_rect = QApplication.primaryScreen().availableGeometry()

        # 随机位置（确保完全可见）
        new_x = random.randint(0, screen_rect.width() - self.pet.width())
        new_y = random.randint(0, screen_rect.height() - self.pet.height())

        self.pet.move(new_x, new_y)

        # 2秒后再次移动（如果游戏未结束）
        if self.time_left > 0:
            QTimer.singleShot(2000, self.move_pet_randomly)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    pet = DesktopPet()
    pet.show()
    sys.exit(app.exec_())