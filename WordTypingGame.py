import sqlite3

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QRadioButton)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap
import random


class WordTypingGame(QWidget):
    def __init__(self, PDH=None):
        super().__init__()
        self.PDH = PDH
        self.score = 0
        self.current_word = ""
        self.current_index = 0
        self.word_dict = {}
        self.word_source = "CET4"  # 默认使用CET4词汇表
        self.error_count = 0
        self.error_timer = None
        self.init_ui()
        self.load_words_from_db()

    def init_ui(self):
        self.setWindowTitle("单词打字游戏")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(600, 400)

        self.main_container = QWidget(self)
        self.main_container.setObjectName("mainContainer")
        self.main_container.setStyleSheet("""
            #mainContainer {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                border: 1px solid #e0e0e0;
            }
        """)
        self.main_container.setGeometry(0, 0, 600, 400)

        main_layout = QVBoxLayout(self.main_container)
        main_layout.setContentsMargins(0, 0, 0, 10)
        main_layout.setSpacing(15)

        # 标题栏
        title_bar = QWidget()
        title_bar.setFixedHeight(60)
        title_layout = QHBoxLayout(title_bar)
        title_bar.setStyleSheet(
            """
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ADD8E6, stop:1 #FFFFFF);
            border-top-left-radius: 15px;
            border-top-right-radius: 15px;
            padding-left: 15px;
            """)

        title_icon = QLabel()
        title_icon.setPixmap(QPixmap('img/keyboard.png').scaled(32, 32, Qt.KeepAspectRatio))
        title_icon.setStyleSheet("background: transparent;")

        title_text = QLabel("单词打字游戏")
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
                        font-family: 'Microsoft YaHei';
                    }
                    QPushButton:hover {
                        background-color: rgba(192,192,192,0.5);
                    }
                """)
        close_button.clicked.connect(self.close)

        title_layout.addWidget(title_icon)
        title_layout.addWidget(title_text)
        title_layout.addStretch()
        title_layout.addWidget(close_button)


        word_source_widget = QWidget()
        word_source_widget.setStyleSheet("background: transparent;")
        word_source_layout = QHBoxLayout(word_source_widget)
        word_source_layout.setContentsMargins(50, 0, 50, 0)

        self.cet_label = QLabel("词库：")
        self.cet_label.setStyleSheet("font-size: 15px; color: #333;font-family: 'Microsoft YaHei';")
        self.cet_label.setAlignment(Qt.AlignLeft)
        self.cet4_radio = QRadioButton("CET4")
        self.cet4_radio.setStyleSheet("font-size: 15px; color: #333;font-family: 'Microsoft YaHei';")
        self.cet4_radio.setChecked(True)
        self.cet4_radio.toggled.connect(self.on_word_source_changed)

        self.cet6_radio = QRadioButton("CET6")
        self.cet6_radio.setStyleSheet("font-size: 15px; color: #333;font-family: 'Microsoft YaHei';")
        self.cet6_radio.toggled.connect(self.on_word_source_changed)


        word_source_layout.addWidget(self.cet_label)
        word_source_layout.addWidget(self.cet4_radio)
        word_source_layout.addWidget(self.cet6_radio)
        word_source_layout.addStretch()

        # 游戏区域
        self.word_label = QLabel()
        self.word_label.setAlignment(Qt.AlignCenter)
        self.word_label.setStyleSheet("font-size: 80px; font-family: 'Arial';")

        self.meaning_label = QLabel()
        self.meaning_label.setAlignment(Qt.AlignCenter)
        self.meaning_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                color: #666;
                font-family: 'Microsoft YaHei';
            }
        """)

        self.count_widget = QWidget()
        self.count_widget.setStyleSheet("background: transparent;")

        count_layout= QHBoxLayout(self.count_widget)
        count_layout.setContentsMargins(50, 0, 50, 0)
        count_layout.setSpacing(15)

        self.score_label = QLabel(f"已输入单词: {self.score}")
        self.score_label.setAlignment(Qt.AlignCenter)
        self.score_label.setStyleSheet("font-size: 15px; color: #333;font-family: 'Microsoft YaHei';")

        self.error_label = QLabel(f"错误数: {self.error_count}")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setStyleSheet("font-size: 15px; color: #333;font-family: 'Microsoft YaHei';")

        count_layout.addWidget(self.score_label)
        count_layout.addStretch()
        count_layout.addWidget(self.error_label)

        main_layout.addWidget(title_bar)
        main_layout.addWidget(word_source_widget)
        main_layout.addStretch()
        main_layout.addWidget(self.word_label)
        main_layout.addWidget(self.meaning_label)
        main_layout.addStretch()
        main_layout.addWidget(self.count_widget)

        # 窗口拖动功能
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

    def load_words_from_db(self):
        """从数据库加载单词，根据选择的词库"""
        try:
            conn = sqlite3.connect('pet_data.db')
            cursor = conn.cursor()

            # 根据选择的词库决定查询哪个表
            table_name = self.word_source
            cursor.execute(f"SELECT word, translate FROM {table_name}")
            rows = cursor.fetchall()

            self.word_dict = {row[0]: row[1] for row in rows}
            self.word_list = list(self.word_dict.keys())
            random.shuffle(self.word_list)

            if self.word_list:
                self.next_word()
            else:
                print(f"警告：{self.word_source}表中没有单词数据")

        except sqlite3.Error as e:
            print(f"数据库错误: {str(e)}")
            # 可以在这里添加一些默认单词作为后备
            self.word_dict = {
                "error": "出错了喵",
            }
            self.word_list = list(self.word_dict.keys())
            random.shuffle(self.word_list)
            self.next_word()
        finally:
            if 'conn' in locals():
                conn.close()

    def next_word(self):
        """切换到下一个单词"""
        if not self.word_list:
            self.word_list = list(self.word_dict.keys())
            random.shuffle(self.word_list)

        self.current_word = self.word_list.pop()
        self.current_index = 0
        self.display_word()

        # 显示中文意思
        self.meaning_label.setText(self.word_dict[self.current_word])

    def display_word(self):
        """显示当前单词状态"""
        word_html = ""
        for i, char in enumerate(self.current_word):
            if i < self.current_index:
                # 已输入正确的字母 - 黑色
                word_html += f'<span style="color:rgb(101, 124, 106);">{char}</span>'
            else:
                # 待输入的字母 - 灰色
                word_html += f'<span style="color:#ccc;">{char}</span>'

        self.word_label.setText(word_html)

    def keyPressEvent(self, event):
        if not self.current_word:
            return

        key = event.text().lower()

        if key == self.current_word[self.current_index].lower():
            self.current_index += 1
            self.display_word()

            if self.current_index >= len(self.current_word):
                self.score += 1
                self.score_label.setText(f"得分: {self.score}")
                QTimer.singleShot(100, self.next_word)
        else:
            # 错误处理部分
            self.error_count += 1
            self.error_label.setText(f"错误: {self.error_count}")

            # 保存当前显示状态
            original_html = self.word_label.text()

            # 创建错误显示（当前字母变红）
            error_html = ""
            for i, char in enumerate(self.current_word):
                if i < self.current_index:
                    error_html += f'<span style="color:rgb(101, 124, 106);">{char}</span>'
                elif i == self.current_index:
                    error_html += f'<span style="color:rgb(187, 62, 0);">{char}</span>'
                else:
                    error_html += f'<span style="color:#ccc;">{char}</span>'

            self.word_label.setText(error_html)

            # 0.5秒后恢复原状
            if self.error_timer:
                self.error_timer.stop()
            self.error_timer = QTimer.singleShot(100, lambda: self.word_label.setText(original_html))

    def show_game(self):
        """显示游戏窗口"""
        self.show()
        self.activateWindow()
        self.setFocus()

    def on_word_source_changed(self):
        """当词库选择改变时重新加载单词"""
        if self.cet4_radio.isChecked():
            self.word_source = "CET4"
        else:
            self.word_source = "CET6"
        self.load_words_from_db()

    def closeEvent(self, event):
        """关闭时保存分数"""

        event.accept()