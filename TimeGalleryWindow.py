from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
                             QPushButton, QApplication, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import QPixmap, QColor





class TimeGalleryWindow(QWidget):
    def __init__(self, parent=None, PDH=None):
        super().__init__()
        self.parent = parent
        self.PDH = PDH

        self.setWindowTitle("时间长廊")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(800, 600)

        self.init_ui()
        self.load_mood_cards()

    def init_ui(self):
        self.main_container = QWidget(self)
        self.main_container.setObjectName("mainContainer")
        self.main_container.setStyleSheet("""
            #mainContainer {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                border: 1px solid #e0e0e0;
            }
        """)
        self.main_container.setGeometry(0, 0, 800, 600)

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

        title_icon = QLabel()
        title_icon.setPixmap(QPixmap('img/time_icon.png').scaled(36, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        title_icon.setStyleSheet("background: transparent;")

        title_text = QLabel("时间长廊")
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
        close_button.clicked.connect(self.close)

        title_layout.addWidget(title_icon)
        title_layout.addWidget(title_text)
        title_layout.addStretch()
        title_layout.addWidget(close_button)

        # 时间线区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
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

        self.timeline_container = QWidget()
        self.timeline_container.setStyleSheet("background: transparent;")
        self.timeline_layout = QVBoxLayout(self.timeline_container)
        self.timeline_layout.setContentsMargins(50, 30, 50, 30)
        self.timeline_layout.setSpacing(40)

        self.scroll_area.setWidget(self.timeline_container)

        main_layout.addWidget(title_bar)
        main_layout.addWidget(self.scroll_area)

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

    def load_mood_cards(self):
        """加载并显示所有情绪卡片"""
        cards = self.PDH.get_mood_cards("default")

        for i, card in enumerate(cards):
            date, weather, mood_summary,evaluate = card


            # 创建卡片
            card_widget = self.create_mood_card(date, weather, mood_summary,evaluate)
            self.timeline_layout.addWidget(card_widget)

            # 如果不是最后一张卡片，添加时间线连接线


    def create_mood_card(self, date, weather, mood_summary,evaluate):
        """创建单个情绪卡片"""



        starimage=self.point_to_star(evaluate)
        card = QWidget()
        card.setFixedHeight(180)
        card.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {self.back_color_change(evaluate)}, stop:1 #FFFFFF);
                border-radius: 10px; 
            }}
        """)

        shadow = QGraphicsDropShadowEffect(card)  # 将阴影效果直接绑定到卡片
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(3, 3)
        card.setGraphicsEffect(shadow)


        #悬停光效
        card.setAttribute(Qt.WA_Hover)
        def enterEvent(event):
            if event:
                glow_T_effect = QGraphicsDropShadowEffect(card)
                glow_T_effect.setBlurRadius(20)  # 光晕模糊半径（越大越柔和）
                glow_T_effect.setColor(QColor(39, 84, 138, 180))  # 发光颜色（RGBA）
                glow_T_effect.setOffset(0, 0)  # 偏移量设为0确保均匀发光
                card.setGraphicsEffect(glow_T_effect)
        def leaveEvent(event):
            if event:
                glow_F_effect = QGraphicsDropShadowEffect(card)
                glow_F_effect.setBlurRadius(0)  # 光晕模糊半径（越大越柔和）
                glow_F_effect.setColor(QColor(255, 200, 50, 180))  # 发光颜色（RGBA）
                glow_F_effect.setOffset(0, 0)  # 偏移量设为0确保均匀发光
                card.setGraphicsEffect(glow_F_effect)
        card.enterEvent = enterEvent
        card.leaveEvent = leaveEvent

        layout = QHBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # 左侧日期区域
        date_widget = QWidget()
        date_widget.setFixedWidth(100)
        date_widget.setStyleSheet(
            """background: transparent;"""
        )
        date_layout = QVBoxLayout(date_widget)
        date_layout.setContentsMargins(10,10,10,10)
        date_layout.setSpacing(5)

        day_label = QLabel(date[8:10]+'日')
        day_label.setStyleSheet("""
            QLabel {
                font-family: 'Microsoft YaHei';
                font-size: 36px;
                font-weight: bold;
                color: #333;
                qproperty-alignment: 'AlignCenter';
            }
        """)

        month_label = QLabel(date[5:7]+'月')
        month_label.setStyleSheet("""
            QLabel {
                font-family: 'Microsoft YaHei';
                font-size: 16px;
                color: #666;
                qproperty-alignment: 'AlignRight';
            }
        """)

        year_label = QLabel(date[0:4]+'年')
        year_label.setStyleSheet("""
            QLabel {
                font-family: 'Microsoft YaHei';
                font-size: 14px;
                color: #999;
                qproperty-alignment: 'AlignRight';
            }
        """)

        date_layout.addWidget(day_label)
        date_layout.addWidget(month_label)
        date_layout.addWidget(year_label)
        date_layout.addStretch()

        # 右侧内容区域
        content_widget = QWidget()
        content_widget.setStyleSheet("""background: transparent;""")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)


        # 天气信息
        weather_widget = QWidget()
        weather_layout = QHBoxLayout(weather_widget)
        weather_layout.setContentsMargins(0, 0, 0, 0)

        weather_icon = QLabel()
        weather_icon.setStyleSheet("background: transparent;")
        weather_icon.setPixmap(
            QPixmap(self.get_weather_icon(weather)).scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        weather_label = QLabel(weather if weather else "未知天气")
        weather_label.setStyleSheet("font-size: 14px; color: #555;"
                                    "font-family: 'Microsoft YaHei';"
                                    "background: transparent;"
                                    )

        weather_layout.addWidget(weather_icon)
        weather_layout.addWidget(weather_label)
        weather_layout.addStretch()

        # 情绪摘要
        mood_point_widget = QWidget()
        mood_point_widget.setStyleSheet("background: transparent;")
        mood_point_layout=QHBoxLayout(mood_point_widget)
        mood_point_layout.setContentsMargins(0, 0, 0, 0)
        mood_point_layout.setSpacing(10)
        mood_point_layout.setAlignment(Qt.AlignLeft)

        mood_1_point_label = QLabel()
        mood_1_point_label.setPixmap(QPixmap(starimage[0]).scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        mood_2_point_label = QLabel()
        mood_2_point_label.setPixmap(QPixmap(starimage[1]).scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        mood_3_point_label = QLabel()
        mood_3_point_label.setPixmap(QPixmap(starimage[2]).scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        mood_4_point_label = QLabel()
        mood_4_point_label.setPixmap(QPixmap(starimage[3]).scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        mood_5_point_label = QLabel()
        mood_5_point_label.setPixmap(QPixmap(starimage[4]).scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        mood_point_layout.addWidget(mood_1_point_label)
        mood_point_layout.addWidget(mood_2_point_label)
        mood_point_layout.addWidget(mood_3_point_label)
        mood_point_layout.addWidget(mood_4_point_label)
        mood_point_layout.addWidget(mood_5_point_label)

        mood_sum = QWidget()
        mood_sum_layout = QVBoxLayout(mood_sum)  # 添加布局
        mood_sum_layout.setContentsMargins(0, 0, 0, 0)

        mood_sum_label = QLabel(mood_summary if mood_summary else "无记录")
        mood_sum_label.setWordWrap(True)  # 允许文本换行
        mood_sum_label.setStyleSheet("""
            QLabel {
                background: transparent;
                border-radius: 10px;
                font-size: 14px; 
                color: #333;
                font-family: 'Microsoft YaHei';
                padding: 8px;
            }
        """)
        mood_sum_layout.addWidget(mood_sum_label)  # 将标签添加到布局

        # 确保情绪摘要区域有足够空间
        mood_sum.setMinimumHeight(60)




        content_layout.addWidget(weather_widget)
        content_layout.addWidget(mood_point_widget)
        content_layout.addWidget(mood_sum)
        content_layout.addStretch()

        layout.addWidget(date_widget)
        layout.addWidget(content_widget)

        return card

    def get_weather_icon(self, weather):
        """根据天气返回图标路径"""
        weather_icons = {
            "晴": "img/烈日.png",
            "阴": "img/多云.png",
            "少云": "img/多云.png",
            "晴间多云": "img/多云.png",
            "多云": "img/多云.png",
            "沙尘暴": "img/沙尘.png",
            "浮尘": "img/沙尘.png",
            "扬沙": "img/沙尘.png",
            "强沙尘暴": "img/沙尘.png",
            "雪": "img/大雪.png",
            "阵雪": "img/大雪.png",
            "小雪": "img/大雪.png",
            "中雪": "img/大雪.png",
            "大雪": "img/大雪.png",
            "暴雪": "img/大雪.png",
            "阵雨": "img/小雨.png",
            "细雨": "img/小雨.png",
            "小雨": "img/小雨.png",
            "中雨": "img/大雨.png",
            "大雨": "img/大雨.png",
            "暴雨": "img/大雨.png",
            "大暴雨": "img/大雨.png",
            "特大暴雨": "img/大雨.png",
            "雷阵雨": "img/雷电.png",
            "雷阵雨伴有冰雹": "img/雷电.png",
            "有风": "img/风.png",
            "平静微风": "img/风.png",
            "和风": "img/风.png",
            "清风": "img/风.png",
            "强风": "img/风.png",
            "劲风": "img/风.png",
            "疾风": "img/风.png",
            "大风": "img/风.png",
            "烈风": "img/风.png",
            "风暴": "img/风.png",
            "狂爆风": "img/风.png",
            "飓风": "img/风.png",
            "热带风": "img/风.png",
            "霾": "img/雾霾.png",
            "中度霾": "img/雾霾.png",
            "重度霾": "img/雾霾.png",
            "严重霾": "img/雾霾.png",
            "雾": "img/雾霾.png",
            "浓雾": "img/雾霾.png",
            "强浓雾": "img/雾霾.png",
            "轻雾": "img/雾霾.png",
            "大雾": "img/雾霾.png",
            "特强浓雾": "img/雾霾.png"
        }

        if weather in weather_icons:
            return weather_icons[weather]
        return "img/天气-未知.png"

    def adjust_position(self):
        if not self.parent:
            return

        pet_pos = self.parent.pos()
        pet_width = self.parent.width()
        screen_rect = QApplication.primaryScreen().availableGeometry()

        # 居中显示
        center_x = pet_pos.x() + pet_width / 2 - self.width() / 2
        center_y = pet_pos.y() + self.parent.height() / 2 - self.height() / 2

        # 确保窗口在屏幕内
        center_x = max(0, min(center_x, screen_rect.width() - self.width()))
        center_y = max(0, min(center_y, screen_rect.height() - self.height()))

        self.move(center_x, center_y)

    def show_gallery(self):
        self.adjust_position()
        self.show()

    def point_to_star(self, point):
        star_image=[]

        halfstar=point-int(point)
        for i in range(int(point)):
            star_image.append("img/full _star.png")
        if halfstar>=0.5:
            star_image.append("img/half_star.png")
        while len(star_image)<5:
            star_image.append("img/empty_star.png")
        return star_image[:5]

    def back_color_change(self, point):
        return {
            0: "#99CCFF",
            0.5: "#99CCFF",
            1: "#CCFFFF",
            1.5: "#CCFFFF",
            2: "#FFFFFF",
            2.5: "#FFFFFF",
            3: "#FFE5CC",
            3.5: "#FFE5CC",
            4: "#FFCC99",
            4.5: "#FFCC99",
            5: "#FFB266"
        }.get(point, "white")
