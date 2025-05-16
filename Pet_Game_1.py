from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QMessageBox
import random


class RPGGame(QWidget):
    def __init__(self, PDH):
        super().__init__()

        self.PDH = PDH

        self.setWindowTitle("猜拳小游戏")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(500, 500)

        self.mainContainer = QWidget(self)
        self.mainContainer.setObjectName("mainContainer")
        self.mainContainer.setStyleSheet("""
                            #mainContainer {
                                background: transparent;
                                border: 1px;
                            }
                        """)
        self.score_this = 0

        self.player_choice = None  # 玩家选择
        self.computer_choice = None  # 电脑选择
        self.result = None  # 比赛结果

        self.rock_64_img = 'img/猜拳 石头剪刀布 石头 64.png'
        self.scissors_64_img = 'img/猜拳石头剪刀布剪刀64.png'
        self.paper_64_img = 'img/猜拳石头剪刀布 布64.png'
        self.rock_128_img = 'img/猜拳 石头剪刀布 石头128.png'
        self.scissors_128_img = 'img/猜拳石头剪刀布剪刀128.png'
        self.paper_128_img = 'img/猜拳石头剪刀布 布128.png'
        self.default_img = 'img/game_question.png'
        self.win_img = 'img/胜利.png'
        self.lose_img = 'img/负.png'
        self.pingju_img= 'img/平局.png'

        self.rock_pixmap = QPixmap(self.rock_128_img).scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.scissors_pixmap = QPixmap(self.scissors_128_img).scaled(128, 128, Qt.KeepAspectRatio,
                                                                     Qt.SmoothTransformation)
        self.paper_pixmap = QPixmap(self.paper_128_img).scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.win_pixmap = QPixmap(self.win_img).scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.lose_pixmap = QPixmap(self.lose_img).scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.pingju_pixmap = QPixmap(self.pingju_img).scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.init_UI()

    def init_UI(self):
        main_layout = QVBoxLayout(self.mainContainer)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        title_bar = QWidget()
        # 设置标题栏的固定高度为50
        title_bar.setFixedHeight(50)
        # 设置标题栏的样式表，包括背景色、圆角和内边距
        title_bar.setStyleSheet("""
                                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ADD8E6, stop:1 #FFFFFF);
                                    border-top-left-radius: 15px;
                                    border-top-right-radius: 15px;
                                    padding-left: 15px;
                                """)

        # 创建标题栏的布局，并设置其父容器为title_bar
        title_layout = QHBoxLayout(title_bar)
        # 设置标题栏布局的边距
        title_layout.setContentsMargins(0, 0, 10, 0)

        # 天气图标和基本信息
        title_icon = QLabel()
        title_icon.setPixmap(QPixmap('img/猜拳.png').scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        title_icon.setStyleSheet("""
                                            background: transparent;

                                        """)

        title_text = QLabel("猜拳游戏")
        title_text.setStyleSheet("""
                                    QLabel {
                                        background: transparent;
                                        color: black;
                                        font-size: 16px;
                                        font-weight: bold;
                                        padding-left: 10px;
                                        font-family: 'Microsoft YaHei';
                                    }
                                """)

        close_button = QPushButton("关闭")
        close_button.setStyleSheet("""
                    QPushButton {
                        background-color: white;
                        color: black;
                        border: none;
                        border-radius: 8px;
                        padding: 6px 12px;
                    }
                    QPushButton:hover {
                        background-color: rgba(192,192,192,0.5);
                    }
                """)
        close_button.clicked.connect(self.game_close)
        title_layout.addWidget(title_icon)
        title_layout.addWidget(title_text)
        title_layout.addStretch()
        title_layout.addWidget(close_button)

        main_layout.addWidget(title_bar)

        mid_body = QWidget()
        mid_body.setStyleSheet("""
                                    background: #ffffff;
                                    font-family: 'Microsoft YaHei';
                                    font-weight: bold;
                                """)
        mid_body.setFixedSize(400, 200)

        contract_layout = QHBoxLayout(mid_body)

        self.player_label = QLabel()
        self.player_label.setPixmap(
            QPixmap(self.default_img).scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        self.computer_label = QLabel()
        self.computer_label.setPixmap(
            QPixmap(self.default_img).scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        vs_label = QLabel()
        vs_label.setPixmap(QPixmap('img/vs.png').scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        vs_label.setAlignment(Qt.AlignCenter)

        contract_layout.addWidget(self.player_label)
        contract_layout.addWidget(vs_label)
        contract_layout.addWidget(self.computer_label)

        info_part = QWidget()
        info_layout = QHBoxLayout(info_part)
        info_part.setStyleSheet("""
                                QWidget {
                                background: white;
                                }

        """)

        me_label = QLabel('我')
        me_label.setStyleSheet("""
                                            QLabel {
                                                background: white;
                                                border-radius:3px;
                                                color: black;
                                                font-size: 16px;
                                                font-weight: bold;
                                                qproperty-alignment: 'AlignCenter';  /* 水平和垂直居中 */
                                                
                                                }


                                    """)

        self.score_label = QLabel()
        self.score_label.setText(f"积分:{self.score_this}")
        self.score_label.setStyleSheet("""
                                    QLabel {
                                        background: white;
                                        color: black;
                                        font-size: 16px;
                                        font-weight: bold;
                                        
                                        }

                            """)

        computer_label = QLabel()
        computer_label.setText("小忆")
        computer_label.setStyleSheet("""
                                                    QLabel {
                                                        background: white;
                                                        color: black;
                                                        font-size: 16px;
                                                        font-weight: bold;
                                                        
                                                        qproperty-alignment: 'AlignCenter';  /* 水平和垂直居中 */
                                                        }

                                            """)

        info_layout.addWidget(me_label)
        info_layout.addWidget(self.score_label)
        info_layout.addWidget(computer_label)

        main_layout.addWidget(mid_body)
        main_layout.addWidget(info_part)

        choice_part = QWidget()
        choice_part.setStyleSheet("""
                                    QWidget {
                                        background-color: white;
                                        border-bottom-left-radius: 15px;
                                        border-bottom-right-radius: 15px;}
                """)
        choice_layout = QHBoxLayout(choice_part)
        choice_layout.setContentsMargins(20, 20, 20, 20)
        choice_layout.setSpacing(10)

        a_btn = QPushButton()
        a_btn.setStyleSheet(
            """
            QPushButton {
                background-color: white;
                border: none;
                border-radius: 8px;}
            QPushButton:hover {
                        background-color: rgba(192,192,192,0.5);
                    }

            """
        )
        a_icon = QIcon(self.rock_64_img)
        a_btn.setIcon(a_icon)
        a_btn.setIconSize(QSize(64, 64))
        a_btn.clicked.connect(self.a_btn_clicked)

        b_btn = QPushButton()
        b_btn.setStyleSheet(
            """
            QPushButton {
                background-color: white;
                border: none;
                border-radius: 8px;}
            QPushButton:hover {
                        background-color: rgba(192,192,192,0.5);
                    }

            """
        )
        b_icon = QIcon(self.scissors_64_img)
        b_btn.setIcon(b_icon)
        b_btn.setIconSize(QSize(64, 64))
        b_btn.clicked.connect(self.b_btn_clicked)

        c_btn = QPushButton()
        c_btn.setStyleSheet(
            """
            QPushButton {
                background-color: white;
                border: none;
                border-radius: 8px;}
            QPushButton:hover {
                        background-color: rgba(192,192,192,0.5);
                    }

            """
        )
        c_icon = QIcon(self.paper_64_img)
        c_btn.setIcon(c_icon)
        c_btn.setIconSize(QSize(64, 64))
        c_btn.clicked.connect(self.c_btn_clicked)

        choice_layout.addWidget(a_btn)
        choice_layout.addWidget(b_btn)
        choice_layout.addWidget(c_btn)
        main_layout.addWidget(choice_part)

        self.drag_pos = None
        title_bar.mousePressEvent = self.title_mouse_press
        title_bar.mouseMoveEvent = self.title_mouse_move

    def title_mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos()

    def title_mouse_move(self, event):
        if self.drag_pos and event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.globalPos() - self.drag_pos)
            self.drag_pos = event.globalPos()

    def c_btn_clicked(self):
        self.player_choice = "paper"
        self.player_label.setPixmap(
            QPixmap(self.paper_128_img).scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.play_game()

    def b_btn_clicked(self):
        """剪刀按钮点击事件"""
        self.player_choice = "scissors"
        self.player_label.setPixmap(
            QPixmap(self.scissors_128_img).scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.play_game()

    def a_btn_clicked(self):
        """石头按钮点击事件"""
        self.player_choice = "rock"
        self.player_label.setPixmap(
            QPixmap(self.rock_128_img).scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.play_game()

    def contract_handler(self):
        pass

    def RPG_game_show(self):
        super().show()

    def play_game(self):
        """执行游戏逻辑"""
        # 禁用按钮防止重复点击
        for btn in self.findChildren(QPushButton):
            if btn.text() not in ["关闭"]:  # 保留关闭按钮可用
                btn.setEnabled(False)

        # 电脑随机选择
        choices = ["rock", "scissors", "paper"]
        self.computer_choice = random.choice(choices)

        # 显示电脑的选择（可以添加动画效果）
        self.animate_computer_choice()

    def animate_computer_choice(self):
        """动画显示电脑的选择过程"""
        choices = ["rock", "scissors", "paper"]
        self.animation_counter = 0
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_computer_animation)
        self.animation_timer.start(150)  # 每100毫秒更新一次

    def update_computer_animation(self):
        """更新电脑选择的动画"""
        choices = ["rock", "scissors", "paper"]
        if self.animation_counter < 10:  # 动画持续1秒（10次*100毫秒）
            # 随机显示一个选择作为动画效果
            temp_choice = random.choice(choices)
            if temp_choice == "rock":
                self.computer_label.setPixmap(
                    self.rock_pixmap)
            elif temp_choice == "scissors":
                self.computer_label.setPixmap(
                    self.scissors_pixmap)
            else:
                self.computer_label.setPixmap(
                    self.paper_pixmap)
            self.animation_counter += 1
        else:
            # 动画结束，显示电脑的真实选择
            self.animation_timer.stop()
            if self.computer_choice == "rock":
                self.computer_label.setPixmap(
                    self.rock_pixmap)
            elif self.computer_choice == "scissors":
                self.computer_label.setPixmap(
                    self.scissors_pixmap)
            else:
                self.computer_label.setPixmap(
                    self.paper_pixmap)

            # 判断胜负
            self.determine_winner()

            # 重新启用按钮
            for btn in self.findChildren(QPushButton):
                if btn.text() not in ["关闭"]:
                    btn.setEnabled(True)

    def determine_winner(self):
        """判断胜负并更新积分"""
        if self.player_choice == self.computer_choice:
            self.result = "平局"
            message = "平局！"
        elif (self.player_choice == "rock" and self.computer_choice == "scissors") or \
                (self.player_choice == "scissors" and self.computer_choice == "paper") or \
                (self.player_choice == "paper" and self.computer_choice == "rock"):
            self.result = "胜利"
            self.score_this += 1
            message = "你赢了！"
        else:
            self.result = "失败"
            self.score_this = max(0, self.score_this)  # 积分不低于0
            message = "你输了！"

        # 更新积分显示
        self.score_label.setText(f"积分: {self.score_this}")

        if message == "你输了！":
            self.computer_label.setPixmap(
                self.win_pixmap)
            self.player_label.setPixmap(
                self.lose_pixmap)
        elif message == "你赢了！":
            self.player_label.setPixmap(
                self.win_pixmap)
            self.computer_label.setPixmap(
                self.lose_pixmap)
        else:
            self.player_label.setPixmap(
                self.pingju_pixmap)
            self.computer_label.setPixmap(
                self.pingju_pixmap)

    def game_close(self):
        self.PDH.log_game_score(self.score_this)
        self.score_this = 0
        self.score_label.setText("积分: 0")
        self.close()


