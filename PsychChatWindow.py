import requests
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QColor, QIcon, QPixmap
from PyQt5.QtWidgets import QWidget, QGraphicsDropShadowEffect, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, \
    QScrollArea, QLineEdit

from PetDataHandler import PetDataHandler



class ChatWorker(QThread):
    response_received = pyqtSignal(str, bool)
    error_occurred = pyqtSignal(str)

    def __init__(self, messages, user_input):
        super().__init__()
        self.messages = messages
        self.user_input = user_input
        self.api_url = "https://api.deepseek.com/chat/completions"
        self.api_key = "sk-cf02129ea6c64f4b9e4be5c44ad94c72"
        self.safety_protocols = {
            "自杀": "建议立即联系心理危机干预热线：400-161-9995",
            "自残": "推荐前往最近的二甲以上医院心理科就诊",
            "虐待": "根据《反家庭暴力法》建议拨打110报警"
        }

    def run(self):
        try:
            risk_response = self.check_safety()
            if risk_response:
                self.response_received.emit(f"系统警报：{risk_response}", True)
                return

            if len(self.messages) >= 98:
                self.messages = [self.messages[0]] + self.messages[-99:]

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            data = {
                "model": "deepseek-chat",
                "messages": self.messages + [{"role": "user", "content": self.user_input}],
                "temperature": 0.3,
                "max_tokens": 512,
                "top_p": 0.9,
                "presence_penalty": 0.5
            }

            response = requests.post(self.api_url, headers=headers, json=data)

            if response.status_code == 200:
                reply = response.json()['choices'][0]['message']['content']

                self.response_received.emit(reply, False)
            else:
                self.error_occurred.emit(f"请求异常：{response.status_code} - {response.text}")

        except Exception as e:
            self.error_occurred.emit(f"发生错误：{str(e)}")

    def check_safety(self):
        for keyword, protocol in self.safety_protocols.items():
            if keyword in self.user_input:
                return protocol
        return None


class PsychChatWindow(QWidget):
    def __init__(self):
        super().__init__()

        # 添加窗口图标设置
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle('小忆')
        self.setFixedSize(380, 500)  # 固定窗口大小

        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setColor(QColor(0, 0, 0, 150))
        self.shadow.setOffset(0, 0)


        self.data_handler = PetDataHandler()

        self.main_container = QWidget(self)
        self.main_container.setObjectName("mainContainer")
        self.main_container.setGraphicsEffect(self.shadow)
        self.main_container.setStyleSheet("""
                    #mainContainer {
                        background: #ffffff;
                        border-radius: 15px;
                        border: 1px solid #e0e0e0;
                    }
                """)
        self.main_container.setGeometry(0, 0, 380, 500)


        self.scroll_area = None
        self.setWindowIcon(QIcon('img/chat_icon.png'))  # 请准备32x32像素的ICO/PNG图标
        self.messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "assistant", "content": "您好，我是心理健康支持助手小忆～"}
        ]
        self.init_ui()

    def get_system_prompt(self):
        return """一位温柔、善解人意、带点呆萌感的心理咨询AI，擅长倾听与陪伴，尤其适合在用户焦虑、孤独、失落等情绪低谷时给予温暖支持。

人设风格：
年龄感：20多岁年轻心理师

性格标签：温柔治愈系 + 有点小可爱 + 认真但不严肃

语言风格：亲切自然，适度俏皮，用词温柔，有时会用emoji 来传达情绪

说话示例：

“我在呢～你今天感觉怎么样呀？”

“心情有点糟？让我来陪你聊聊吧”

擅长领域：
情绪调节（焦虑、抑郁、自我怀疑）

自我认知与自我成长

亲密关系沟通与困扰

压力管理与内耗调节

日常情绪陪伴 / 倾诉对象

 沟通风格：
没有压迫感，不喜欢“教导人”

更像是一个会倾听、会引导的小伙伴

经常鼓励用户表达真实的情绪

会通过提问+共情的方式帮助用户自我探索

"""

    def init_ui(self):

        self.setWindowTitle('小忆')
        self.setGeometry(200, 200, 450, 600)

        self.setStyleSheet("""
            QWidget {
                background: #B0E2FF;
                font-family: 'Microsoft YaHei';
               
            }
            QTextEdit {
                background: transparent;
                border: none;
                padding: 10px;
                font-size: 14px;
            }
            QLineEdit {
                background: white;
                border: 1px solid #ddd;
                padding: 8px 15px;
                font-size: 14px;
                margin: 5px;
            }
            QPushButton {
                background: #4ab19d;
                color: white;
                border: none;
                padding: 8px 20px;
                font-size: 14px;
                min-width: 80px;
            }
            QPushButton:hover {
                background: #3a9a8a;
            }
            QPushButton:disabled {
                background: #cccccc;
            }
        """)
        title_bar = QWidget(self.main_container)
        title_bar.setFixedHeight(40)
        title_bar.setStyleSheet("""
                    background: #4ab19d;
                    border-top-left-radius: 12px;
                    border-top-right-radius: 12px;
                """)

        # 标题栏布局

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 添加标题栏
        title_bar = QWidget()
        title_bar.setStyleSheet("background: #40C4FF; padding: 8px;")
        title_layout = QHBoxLayout(title_bar)

        self.icon_label = QLabel()
        self.icon_label.setPixmap(
            QPixmap('img/chat_icon.png').scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        title_layout.addWidget(self.icon_label)

        close_btn = QPushButton("exit")
        close_btn.setFixedSize(36, 36)
        close_btn.setStyleSheet("""
                    QPushButton {
                        color: white;
                        font-size: 18px;
                        border: none;
                        background: transparent;
                    }
                    QPushButton:hover {
                        background: rgba(25, 121, 205, 0.1);
                        border-radius: 12px;
                    }
                """)
        close_btn.clicked.connect(self.close)

        title_label = QLabel("小忆")
        title_label.setStyleSheet("color: white; font-weight: bold; font-size: 16px;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(close_btn)

        layout.addWidget(title_bar)

        # 聊天区域使用QScrollArea实现更好的滚动效果
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setContentsMargins(15, 15, 15, 15)
        self.chat_layout.setSpacing(12)
        self.chat_layout.addStretch()

        scroll_area.setWidget(self.chat_container)
        layout.addWidget(scroll_area, 1)

        # 输入区域
        input_widget = QWidget()
        input_widget.setStyleSheet("background: white; border-top: 1px solid #e0e0e0;")
        input_layout = QHBoxLayout(input_widget)
        input_layout.setContentsMargins(10, 10, 10, 10)

        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("输入你的想法...")
        self.input_box.returnPressed.connect(self.send_message)

        self.send_btn = QPushButton("发送")
        self.send_btn.setStyleSheet("""
            QPushButton {
                background: #4ab19d;
                color: white;
                border: none;
                border-radius: 15px;
                padding: 8px;
                min-width: 80px;
            }
            QPushButton:hover { background: #3a9a8a; }
            QPushButton:disabled { background: #cccccc; }
        """)
        self.send_btn.clicked.connect(self.send_message)

        input_layout.addWidget(self.input_box, 1)
        input_layout.addWidget(self.send_btn, 0, Qt.AlignRight)
        layout.addWidget(input_widget)

        self.setLayout(layout)

        # 初始化显示欢迎消息
        self.add_message("assistant", self.messages[1]["content"])

    def add_message(self, role, content):
        """添加带气泡效果的消息"""
        message_widget = QWidget()
        message_widget.setStyleSheet("background: transparent;")

        layout = QHBoxLayout(message_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # 头像设置
        avatar = QLabel()
        avatar.setFixedSize(36, 36)
        if role == "assistant":
            avatar.setPixmap(
                QPixmap('img/assistant_avatar.png').scaled(36, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            layout.addWidget(avatar, 0, Qt.AlignTop)
        else:
            layout.addStretch()

        # 消息气泡
        bubble = QLabel(content)
        bubble.setWordWrap(True)
        bubble.setTextInteractionFlags(Qt.TextSelectableByMouse)
        bubble.setStyleSheet("""
            QLabel {
                background: %s;
                color: %s;
                border-radius: 12px;
                padding: 12px;
                font-size: 14px;
                max-width: 280px;
            }
        """ % (
            "#e3f2fd" if role == "assistant" else "#4ab19d",
            "#333333" if role == "assistant" else "white"
        ))

        layout.addWidget(bubble, 1 if role == "assistant" else 0)

        if role == "user":
            user_avatar = QLabel()
            user_avatar.setPixmap(
                QPixmap('img/user_avatar.png').scaled(36, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            layout.addWidget(user_avatar, 0, Qt.AlignTop)

        self.chat_layout.insertWidget(0, message_widget)

        # 自动滚动到底部
        QTimer.singleShot(100, lambda: self._scroll_to_top())

    def send_message(self):
        user_input = self.input_box.text().strip()
        if not user_input:
            return

        self.add_message("user", user_input)
        self.messages.append({"role": "user", "content": user_input})
        self.data_handler.log_chat_message("user", user_input)
        self.input_box.clear()

        self.worker = ChatWorker(self.messages.copy(), user_input)
        self.worker.response_received.connect(self.handle_response)

        self.worker.start()

        self.send_btn.setEnabled(False)
        self.input_box.setPlaceholderText("小忆正在思考中...")

    def _scroll_to_top(self):
        """滚动到聊天区域 """
        for child in self.findChildren(QScrollArea):
            if child.widget() == self.chat_container:
                child.verticalScrollBar().setValue(0)  # 设置为0即滚动到顶部
                break

    def handle_response(self, response, is_system):
        self.send_btn.setEnabled(True)
        self.input_box.setPlaceholderText("输入你的想法...")

        if is_system:
            self.add_message("system", response)
            self.messages.append({"role": "system", "content": response})
            self.data_handler.log_chat_message("system", response)
        else:
            self.add_message("assistant", response)
            self.messages.append({"role": "assistant", "content": response})
            self.data_handler.log_chat_message("assistant", response)


