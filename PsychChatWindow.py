import requests
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer, QSize
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QWidget,  QVBoxLayout, QHBoxLayout, QLabel, QPushButton, \
    QScrollArea, QLineEdit, QApplication

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
    def __init__(self,parent_pet=None,PDH=None):
        super().__init__()
        self.send_btn = None
        self.input_box = None
        self.drag_pos = None
        self.worker = None
        self.chat_container = None
        self.chat_layout = None



        self.parent_pet = parent_pet

        self.PDH= PDH

        # 添加窗口图标设置
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet(
            """background-color: transparent;"""
        )
        self.setWindowTitle('小忆')
        self.setFixedSize(380, 500)  # 固定窗口大小

        self.main_container = QWidget(self)
        self.main_container.setObjectName("mainContainer")
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

        main_layout = QVBoxLayout(self.main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 标题栏
        title_bar = QWidget()
        title_bar.setFixedHeight(50)
        title_bar.setStyleSheet("""
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ADD8E6, stop:1 #FFFFFF);
                    border-top-left-radius: 15px;
                    border-top-right-radius: 15px;
                    padding-left: 15px;
                """)

        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(0, 0, 10, 0)

        # 标题图标和文字
        title_icon = QLabel()
        title_icon.setPixmap(QPixmap('img/chat_icon.png').scaled(30, 30, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        title_icon.setStyleSheet("""
                            background: transparent;
                        
                        """)


        title_text = QLabel("小忆")
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

        # 关闭按钮
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
        close_button.clicked.connect(self.close)


        title_layout.addWidget(title_icon)
        title_layout.addWidget(title_text)
        title_layout.addStretch()
        title_layout.addWidget(close_button)

        main_layout.addWidget(title_bar)

        # 聊天区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
                    QScrollArea {
                        border: none;
                        background: #f5f5f5;
                    }
                    QScrollBar:vertical {
                        width: 8px;
                        background: #f5f5f5;
                    }
                    QScrollBar::handle:vertical {
                        background: #d0d0d0;
                        border-radius: 4px;
                    }
                """)

        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setContentsMargins(15, 15, 15, 15)
        self.chat_layout.setSpacing(12)
        self.chat_layout.addStretch()

        self.scroll_area.setWidget(self.chat_container)
        main_layout.addWidget(self.scroll_area, 1)

        # 输入区域
        input_widget = QWidget()
        input_widget.setStyleSheet("""
                    background: white;
                    border-top: 1px solid #e0e0e0;
                    border-bottom-left-radius: 15px;
                    border-bottom-right-radius: 15px;
                """)

        input_layout = QHBoxLayout(input_widget)
        input_layout.setContentsMargins(15, 15, 15, 15)

        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("输入你的想法...")
        self.input_box.setStyleSheet("""
                    QLineEdit {
                        background: white;
                        border: 1px solid #e0e0e0;
                        border-radius: 18px;
                        padding: 8px 15px;
                        font-size: 14px;
                        font-family: 'Microsoft YaHei';
                    }
                """)
        self.input_box.returnPressed.connect(self.send_message)

        self.send_btn = QPushButton()
        self.send_btn.setIcon(QIcon('img/send_icon.png'))
        self.send_btn.setIconSize(QSize(32, 32))
        self.send_btn.setFixedSize(40, 40)
        self.send_btn.setStyleSheet("""
                    QPushButton {
                        background: white;
                        border: none;
                        border-radius: 20px;
                    }
                    QPushButton:hover {
                        background: rgba(224,224,224, 0.3);
                    }
                    QPushButton:disabled {
                        background: rgba(32,32,32, 0.4);
                    }
                """)
        self.send_btn.clicked.connect(self.send_message)

        input_layout.addWidget(self.input_box, 1)
        input_layout.addWidget(self.send_btn, 0, Qt.AlignRight)
        main_layout.addWidget(input_widget)

        # 窗口拖动功能
        self.drag_pos = None
        title_bar.mousePressEvent = self.title_mouse_press
        title_bar.mouseMoveEvent = self.title_mouse_move

        # 初始化显示欢迎消息
        self.add_message("assistant", self.messages[1]["content"])

    def title_mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos()

    def title_mouse_move(self, event):
        if self.drag_pos and event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.globalPos() - self.drag_pos)
            self.drag_pos = event.globalPos()

    def show(self):
        super().show()
        self.adjust_position()

    def adjust_position(self):
        if not self.parent_pet:
            return

        # 获取桌宠位置和屏幕信息
        pet_pos = self.parent_pet.pos()
        pet_width = self.parent_pet.width()
        screen_rect = QApplication.primaryScreen().availableGeometry()

        # 尝试放在右侧
        right_x = pet_pos.x() + pet_width + 10
        if right_x + self.width() <= screen_rect.right():
            self.move(right_x, pet_pos.y())
        # 右侧空间不足则放在左侧
        else:
            left_x = pet_pos.x() - self.width() - 10
            self.move(left_x, pet_pos.y())

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
                font-family: 'Microsoft YaHei';
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

        # 自动滚动到顶部
        QTimer.singleShot(100, lambda: self._scroll_to_top())

    def send_message(self):
        user_input = self.input_box.text().strip()
        if not user_input:
            return

        self.add_message("user", user_input)
        self.messages.append({"role": "user", "content": user_input})
        self.PDH.log_chat_message('user', user_input)

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
            self.PDH.long_log_chat_message('system', response)

        else:
            self.add_message("assistant", response)
            self.messages.append({"role": "assistant", "content": response})
            self.PDH.log_chat_message('assistant', response)



