from PyQt5.QtWidgets import ( QVBoxLayout, QLabel, QHBoxLayout, QWidget, QApplication, QPushButton)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
import requests
import global_value


class WeatherWindow(QWidget):
    def __init__(self,parent=None  ):
        super().__init__()
        self.parent = parent
        self.setWindowTitle("天气详情")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(500, 250)

        self.main_container = QWidget(self)
        self.main_container.setObjectName("mainContainer")
        self.main_container.setStyleSheet("""
                            #mainContainer {
                                background: rgba(255, 255, 255, 0.95);
                                border-radius: 15px;
                                border: 1px solid #e0e0e0;
                            }
                        """)
        self.main_container.setGeometry(0, 0, 500, 250)


        self.report_time_label = None
        self.humidity_label = None
        self.wind_label = None
        self.weather_info = None
        self.temp_label = None

        self.get_IP()
        self.init_ui()



    def init_ui(self):
        # 创建主布局，并设置其父容器为self.main_container
        main_layout = QVBoxLayout(self.main_container)
        # 设置布局的边距为0
        main_layout.setContentsMargins(0, 0, 0, 0)
        # 设置布局的间距为0
        main_layout.setSpacing(0)

        # 创建标题栏的QWidget对象
        title_bar = QWidget()
        # 设置标题栏的固定高度为50
        title_bar.setFixedHeight(50)
        # 设置标题栏的样式表，包括背景色、圆角和内边距
        title_bar.setStyleSheet("""
                            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgb(111, 230, 252), stop:1 #FFFFFF);
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
        title_icon.setPixmap(QPixmap('img/天气.png').scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        title_icon.setStyleSheet("""
                                    background: transparent;

                                """)


        title_text = QLabel("天气详情")
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
        close_button.clicked.connect(self.weather_close)
        title_layout.addWidget(title_icon)
        title_layout.addWidget(title_text)
        title_layout.addStretch()
        title_layout.addWidget(close_button)


        mid_body = QWidget()
        mid_body.setStyleSheet("""
                            background: #ffffff;
                            border-bottom-left-radius: 15px;
                            border-bottom-right-radius: 15px;
                            font-family: 'Microsoft YaHei';
                            font-weight: 350;  
                        """)
        mid_body.setContentsMargins(10,10,10,10)
        layout= QVBoxLayout(mid_body)
        layout.setContentsMargins(10, 10, 10, 10)


        # 详细天气信息
        self.weather_wealabel=QLabel()
        self.weather_info = QLabel()
        self.temp_label = QLabel()
        self.wind_label = QLabel()
        self.humidity_label = QLabel()
        self.report_time_label = QLabel()

        layout.addWidget(self.weather_wealabel)
        layout.addWidget(self.temp_label)
        layout.addWidget(self.wind_label)
        layout.addWidget(self.humidity_label)
        layout.addWidget(self.weather_info)
        layout.addWidget(self.report_time_label)
        layout.setSpacing(10)


        main_layout.addWidget(title_bar)
        main_layout.addWidget(mid_body)

        self.update_weather()

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


    def adjust_position(self):
        if not self.parent:
            return
        # 获取桌宠位置和屏幕信息
        pet_pos = self.parent.pos()
        pet_width = self.parent.width()
        screen_rect = QApplication.primaryScreen().availableGeometry()

        # 尝试放在右侧
        right_x = pet_pos.x() + pet_width + 10
        if right_x + self.width() <= screen_rect.right():
            self.move(right_x, pet_pos.y())
        # 右侧空间不足则放在左侧
        else:
            left_x = pet_pos.x() - self.width() - 20
            self.move(left_x, pet_pos.y())
    def update_weather(self):
        url = "https://restapi.amap.com/v3/weather/weatherInfo"
        try:
            response = requests.get(url, params={"city": global_value.Params["city"], "key": global_value.Params["key_GD"]})
            weather_data = response.json()

            if weather_data["status"] == "1":
                weather_info = weather_data["lives"][0]
                self.current_weather = weather_info["weather"]

                # 更新天气图标
                global_value.CURRENT_WEATHER= self.current_weather
                # 更新天气信息
                self.weather_wealabel.setText(f"天气: {weather_info['weather']}")
                self.weather_info.setText(f"{weather_info['province']} {weather_info['city']}")
                self.temp_label.setText(f"温度: {weather_info['temperature']}°C")
                self.wind_label.setText(f"风力: {weather_info['windpower']}级 {weather_info['winddirection']}")
                self.humidity_label.setText(f"湿度: {weather_info['humidity']}%")
                self.report_time_label.setText(f"更新时间: {weather_info['reporttime']}")

                return self.current_weather
            else:
                self.show_default_weather()
                return None
        except Exception as e:
            print(f"获取天气信息失败: {e}")
            self.show_default_weather()
            return None

    def get_weather_icon_path(self, weather_condition):
        """根据天气情况返回对应的图标路径"""
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

        return weather_icons.get(weather_condition, "img/天气-未知.png")

    def show_default_weather(self):
        """显示默认天气信息（当API请求失败时）"""
        self.temp_label.setText("温度: --°C")
        self.wind_label.setText("风力: --")
        self.humidity_label.setText("湿度: --%")
        self.report_time_label.setText("更新时间: --")

    def get_current_weather_icon(self):
        """返回当前天气对应的图标路径"""
        return self.get_weather_icon_path(self.current_weather if hasattr(self, 'current_weather') else None)

    def weather_show(self):
        self.adjust_position()

        super().show()
    def weather_close(self):
        self.hide()

    def get_IP(self):
        pass
        url = 'https://apis.map.qq.com/ws/location/v1/ip'
        try:
            response = requests.get(url, params={'key': global_value.Params["key_QQ"]})
            ip_data = response.json()

            if ip_data['message'] == "Success":
                global_value.Params['city'] = ip_data['result']['ad_info']['adcode']
                print(global_value.Params['city'])
                return None
            else:
                print(f"API返回错误: {ip_data.get('info', '未知错误')}")
                print(response.json())
                return None

        except requests.exceptions.RequestException as e:
            print(f"获取IP失败: {e}")
            return None