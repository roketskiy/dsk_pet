import sys
import random
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QMovie, QPixmap
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel,QMenu, QAction,  QMessageBox)
from PetDataHandler import PetDataHandler
from PsychChatWindow import PsychChatWindow
from WeatherWindow import WeatherWindow


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

        self.weather_window = WeatherWindow(self)


        self.weather_label = QLabel(self)
        self.weather_label.setPixmap(QPixmap("img/天气-未知.png"))
        self.weather_label.setFixedSize(40, 40)
        self.weather_label.move(0, 0)
        self.weather_label.setAttribute(Qt.WA_TranslucentBackground)
        self.weather_label.setStyleSheet("border: none;")


        self.data_handler = PetDataHandler()
        self.session_id = self.data_handler.start_session()

        self.action_timer = QTimer(self)
        self.action_timer.timeout.connect(self.random_action)
        self.action_timer.start(10000)

        self.click_timer = QTimer()
        self.click_timer.setSingleShot(True)


        # 右键菜单
        self.menu = QMenu(self)
        self.menu.setWindowFlags(Qt.FramelessWindowHint | Qt.Popup)
        self.menu.setAttribute(Qt.WA_TranslucentBackground)
        self.menu.setStyleSheet("""
            QMenu {
                background-color: white;  /* 背景颜色为白色 */
                color:black;  /* 字体颜色为白色 */
                border-radius: 8px;  /* 圆角 */
                border: 1px solid black;  /* 边框 */
                padding: 0;
            }
            QMenu::item {
                background-color: transparent;
                border-radius: 5px;
                height: 30px;
                padding-left: 20px;  /* 左边距 */
                padding-right: 20px;  /* 右边距 */
                text-align: center;  /* 文本居中 */
                font-size: 14px;  /* 字体大小 */
                font-weight: 500;  /* 字体加粗 */
                font-family: "Microsoft YaHei";  /* 字体 */
            }
            QMenu::item:selected {
                background-color: rgb(173,216,230);  /* 选中项的背景色 */
                border-radius: 5px;  /* 选中项圆角 */
            }
            QMenu::item:disabled {
                color: #888;  /* 禁用项的字体颜色 */
                background-color: transparent;  /* 禁用项的背景色 */
            }
        """)
        self.menu.update()
        self.menu.addSeparator()
        self.chat_action = QAction("和小忆说说话", self)
        self.chat_action.triggered.connect(self.show_chat_window)
        self.menu.addAction(self.chat_action)
        self.menu.addSeparator()
        self.weather_action = QAction("查看天气", self)
        self.weather_action.triggered.connect(self.show_weather_window)
        self.menu.addAction(self.weather_action)
        self.menu.addSeparator()
        self.game_action = QAction("玩玩小游戏", self)

        self.menu.addAction(self.game_action)
        self.menu.addSeparator()
        self.exit_action = QAction("退出", self)
        self.exit_action.triggered.connect(self.close)
        self.menu.addAction(self.exit_action)
        self.menu.addSeparator()
        self.update_weather_icon()



    def init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(1200, 800, 180, 180)
        'self.update_weather_icon()'


    def closeEvent(self, event):
        if self.chat_window:
            self.chat_window.close()
        if self.weather_window:
            self.weather_window.close()
        self.data_handler.end_session()
        event.accept()

    def init_animation(self):
        self.animation_label = QLabel(self)
        self.animation_label.move(10,10)
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
            self.chat_window = PsychChatWindow(self)  # 传递self作为父窗口
        self.chat_window.show()

    def update_weather_icon(self):
        """更新天气图标"""

        self.weather_label.setPixmap(QPixmap(self.weather_window.get_current_weather_icon()))

    def show_weather_window(self):
        """显示天气详情窗口"""


        self.weather_window.weather_show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pet = DesktopPet()
    pet.show()
    sys.exit(app.exec_())