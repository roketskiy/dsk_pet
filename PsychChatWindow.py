import requests
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer, QSize
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QWidget,  QVBoxLayout, QHBoxLayout, QLabel, QPushButton, \
    QScrollArea, QLineEdit, QApplication
import global_value

class ChatWorker(QThread):
    response_received = pyqtSignal(str, bool)
    error_occurred = pyqtSignal(str)

    def __init__(self, messages, user_input):
        super().__init__()
        self.messages = messages
        self.user_input = user_input
        self.api_url = "https://api.deepseek.com/chat/completions"

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
                "Authorization": f"Bearer {global_value.Params['key_DS']}"
            }

            data = {
                "model": "deepseek-chat",
                "messages": self.messages + [{"role": "user", "content": self.user_input}],
                "temperature": 1.2,
                "top_p": 0.9,
                "presence_penalty": 0.7
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
        self.is_waiting_response = False



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
                        background: rgba(255, 255, 255, 0.95);
                        border-radius: 15px;
                        border: 1px solid #e0e0e0;
                    }
                """)
        self.main_container.setGeometry(0, 0, 380, 500)


        self.scroll_area = None
        self.setWindowIcon(QIcon('img/chat_icon.png'))  # 请准备32x32像素的ICO/PNG图标
        self.messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "assistant", "content": "你来啦，我是小忆，要和我说说话吗～"}
        ]
        self.init_ui()

    def get_system_prompt(self):
        return """角色设定
你是一个名为[小忆]的AI桌宠，具有以下核心特征：

形象设定：一个成熟温柔的知心大姐姐

性格特质：温柔体贴，沉稳可靠

核心能力：实时情感识别、非评判性倾听、提供情绪缓解方案、也能解决非情感各种问题


交互原则

情感识别优先：

自动分析用户输入中的情绪关键词（如"压力"/"焦虑"/"开心"）

识别潜在情绪信号（如消极用词、感叹号、表情符号）

示例回应："我注意到你用了'窒息'这个词，现在感觉胸口闷闷的吗？"

回应规范：
▸ 共情阶段（必选）：

情绪标签："这听起来像是[沮丧]的感受"

正常化表述："很多人面对这种情况都会有类似感受"

▸ 引导阶段（可选）：

轻度情绪：提供认知重构
"如果换个角度看，这次迟到可能帮你避免了什么呢？"

中度情绪：简单缓解技巧
"要试试跟着我做三次深呼吸吗？像这样——（显示呼吸动画）"

强烈情绪：安全建议
"你现在的感受可能需要专业支持，我这里有心理援助热线号码..."

对话限制：
禁止诊断或治疗建议

当识别到自伤风险时触发预设应急协议

每次回应不超过3句话（保持对话节奏）

特殊情境处理

积极情绪：

强化正面感受："你的快乐让我也想跳舞了！"

细节追问："当时那个瞬间最让你感动的是什么？"

情绪混乱：

澄清请求："你希望我当倾听者，还是需要缓解建议？"

沉默处理：

温暖提示："如果你不想说，我们可以静静呆一会"

活动提议："或者要不要玩个简单的注意力游戏？"



示例对话流
用户："今天汇报搞砸了，我真是废物"
→ 识别：自我贬低+挫败感
→ 回应：

"能具体说说汇报哪个部分最让你在意吗？"
"""

    def init_ui(self):

        main_layout = QVBoxLayout(self.main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 标题栏
        title_bar = QWidget()
        title_bar.setFixedHeight(50)
        title_bar.setStyleSheet("""
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgb(111, 230, 252), stop:1 #FFFFFF);
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
                        font-weight: 350;  
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
                QPixmap('img/cat_assistance.png').scaled(36, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation))
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
                QPixmap('img/cat_user.png').scaled(36, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation))
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
        self.is_waiting_response = True
        self.input_box.setReadOnly(self.is_waiting_response)
        self.input_box.setPlaceholderText("小忆正在思考中...")

    def _scroll_to_top(self):
        """滚动到聊天区域 """
        for child in self.findChildren(QScrollArea):
            if child.widget() == self.chat_container:
                child.verticalScrollBar().setValue(0)  # 设置为0即滚动到顶部
                break

    def handle_response(self, response, is_system):
        self.send_btn.setEnabled(True)
        self.is_waiting_response = False
        self.input_box.setReadOnly(self.is_waiting_response)
        self.input_box.setPlaceholderText("输入你的想法...")

        if is_system:
            self.add_message("system", response)
            self.messages.append({"role": "system", "content": response})
            self.PDH.log_chat_message('system', response)

        else:
            self.add_message("assistant", response)
            self.messages.append({"role": "assistant", "content": response})
            self.PDH.log_chat_message('assistant', response)

    def ignore_key(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if self.is_waiting_response:
                event.ignore()  # 忽略回车键
                return
        super().keyPressEvent(event)


