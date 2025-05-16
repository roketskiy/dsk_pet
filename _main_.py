import sys
import random
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QMovie, QPixmap
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel,QMenu, QAction)
from PetDataHandler import PetDataHandler
from Pet_Game_1 import RPGGame
from PsychChatWindow import PsychChatWindow
from TimeGalleryWindow import TimeGalleryWindow
from WeatherWindow import WeatherWindow
import global_value
from WordTypingGame import WordTypingGame


# ==================== 桌宠主程序 ====================
class DesktopPet(QWidget):
    def __init__(self):
        super().__init__()
        self.current_animation = None
        self.drag_start_pos = None
        self.click_threshold = 10
        self.init_ui()
        self.click_start_pos = None
        self.clk_start_time = None
        self.is_dragging = False
        self.weather_responses = {
            # 晴天系列
            "晴": [
                "阳光好温暖呀，要不要出去走走？",
                "看到太阳公公在笑，我的心情也变好了呢~",
                "记得涂防晒霜哦，我可不想你被晒伤",
                "这样的好天气，很适合晒被子呢！",
                "阳光下的你闪闪发光，就像钻石一样✨",
                "我收集了一袋阳光，送给你当礼物啦~",
                "蓝天白云在开派对，我们也加入吧！",
                "太阳能充电中...我的能量满格啦！"
            ],

            # 多云/阴天系列
            "多云": [
                "云朵像棉花糖一样，好想咬一口呀",
                "太阳在和我们玩捉迷藏呢",
                "这种天气最适合喝杯热可可了☕",
                "云层后面藏着很多小星星哦",
                "阴天也不能阻挡我们保持好心情~",
                "光线温柔得像妈妈的怀抱",
                "云朵在天空画画呢，你看像什么？"
            ],

            # 雨天系列
            "雨": [
                "听，雨滴在唱歌呢~嘀嗒嘀嗒",
                "我帮你数雨滴：1、2、3...哎呀数不过来了",
                "雨天和巧克力最配了，你说呢？",
                "彩虹正在云层后面准备惊喜哦",
                "雨伞战士出动！保护你不被淋湿",
                "雨水把世界洗得亮晶晶的✨",
                "我的防水模式已启动，陪你雨中漫步"
            ],

            # 暴雨系列
            "暴雨": [
                "雷公电母今天好激动啊！",
                "待在室内最安全啦，我保护你",
                "暴雨交响曲正在上演呢",
                "我启动了避雷针功能⚡",
                "雨水像珍珠帘子一样挂在天上",
                "这种天气最适合窝着看电影了"
            ],

            # 雪天系列
            "雪": [
                "雪花快递员来送冬季礼物啦❄️",
                "我们一起堆个雪人朋友吧！",
                "雪花落在鼻尖上凉凉的好有趣",
                "冬季魔法正在施展~",
                "雪地留下的小脚印是我们的秘密",
                "热乎乎的奶茶和雪景最配啦"
            ],

            # 大风系列
            "风": [
                "风姑娘今天心情很激动呢",
                "我的发型都被吹乱啦，噗哈哈",
                "听，风在讲远方的故事🌪️",
                "抱紧我，别被吹跑啦！",
                "树叶在跳风力发电舞呢"
            ],

            # 雾霾系列
            "霾": [
                "空气净化小卫士上线！",
                "记得戴好口罩保护自己哦",
                "等风来，就能看到蓝天啦",
                "我的防雾霾模式已启动",
                "我们一起期待好天气吧~"
            ],

            # 沙尘系列
            "沙尘": [
                "沙漠探险队准备出发！",
                "我的防沙护目镜借给你",
                "沙沙沙...像在演奏沙漠之歌",
                "闭上眼睛，想象我们在绿洲"
            ],

            # 默认通用发言
            "default": [
                "今天过得怎么样呀？",
                "有什么想和我分享的吗？",
                "我在这里陪着你呢~",
                "最近有什么开心的事吗？",
                "需要我为你放首轻音乐吗？",
                "记得多喝水哦~",
                "深呼吸，放松一下肩膀",
                "你笑起来一定很好看",
                "要不要一起数五下深呼吸？",
                "我刚刚发现了一个有趣的事情...",
                "猜猜我在想什么？",
                "给你表演个魔术：消失的烦恼~",
                "我偷偷存了好多阳光笑容，送给你",
                "你是我最重要的人类朋友❤️",
                "今天也要做最棒的自己！"
            ]
        }

        self.weather_mapping = {
            "晴": "晴", "少云": "晴", "晴间多云": "晴",
            "阴": "多云", "多云": "多云",
            "阵雨": "雨", "细雨": "雨", "小雨": "雨", "中雨": "雨",
            "大雨": "暴雨", "暴雨": "暴雨", "大暴雨": "暴雨", "特大暴雨": "暴雨",
            "雷阵雨": "暴雨", "雷阵雨伴有冰雹": "暴雨",
            "雪": "雪", "阵雪": "雪", "小雪": "雪", "中雪": "雪", "大雪": "雪", "暴雪": "雪",
            "有风": "风", "平静微风": "风", "和风": "风", "清风": "风", "强风": "风",
            "劲风": "风", "疾风": "风", "大风": "风", "烈风": "风", "风暴": "风",
            "狂爆风": "风", "飓风": "风", "热带风": "风",
            "霾": "霾", "中度霾": "霾", "重度霾": "霾", "严重霾": "霾",
            "雾": "霾", "浓雾": "霾", "强浓雾": "霾", "轻雾": "霾", "大雾": "霾", "特强浓雾": "霾",
            "沙尘暴": "沙尘", "浮尘": "沙尘", "扬沙": "沙尘", "强沙尘暴": "沙尘"
        }



        self.bubble_timer= QTimer(self)
        self.bubble_timer.timeout.connect(self.show_random_bubble)
        self.bubble_timer.start(60000)
        self.bubble_message=None
        self.bubble = QLabel(None)
        self.bubble.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.bubble.setStyleSheet("""
                QLabel {
                    background-color: white;
                    border: 2px solid #88aaff;
                    padding: 5px;
                    font-size: 12px;
                    font-family: 'Microsoft YaHei';
                    color: #333;
                    max-width: 200px;  /* 限制最大宽度 */
                }
            """)
        self.bubble.hide()
        self.bubble_duration = 3000  # 气泡显示3秒


        self.clk_timer = QTimer()
        self.clk_timer.setInterval(500)  # 设置定时器间隔为500毫秒
        self.clk_timer.setSingleShot(True)  # 设置为单次触发
        self.clk_timer.timeout.connect(self.on_timeout)

        #聊天窗口
        self.chat_window = None

        #天气窗口
        self.weather_window = WeatherWindow(self)
        self.weather_label = QLabel(self)
        self.weather_label.setPixmap(QPixmap("img/天气-未知.png"))
        self.weather_label.setFixedSize(40, 40)
        self.weather_label.move(0, 0)
        self.weather_label.setAttribute(Qt.WA_TranslucentBackground)
        self.weather_label.setStyleSheet("border: none;")




        self.action_timer = QTimer(self)
        self.action_timer.timeout.connect(self.random_action)
        self.action_timer.start(60000)

        self.click_timer = QTimer()
        self.click_timer.setSingleShot(True)
        #情绪概要
        self.time_gallery_window = None

        # RPG游戏
        self.RPG_game_window = None


        self.PDH= PetDataHandler()
        self.PDH.start_session()

        # 右键菜单
        self.menu = QMenu(self)
        self.menu.setWindowFlags(Qt.FramelessWindowHint | Qt.Popup)
        self.menu.setAttribute(Qt.WA_TranslucentBackground)
        self.menu.setContentsMargins(10,10,10,10)
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
        self.game_menu=QMenu(self)
        self.game_menu.setWindowFlags(Qt.FramelessWindowHint | Qt.Popup)
        self.game_menu.setAttribute(Qt.WA_TranslucentBackground)
        self.game_menu.setContentsMargins(10,10,10,10)
        self.game_menu.setStyleSheet("""
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
        self.RPG_Game=QAction('猜拳',self)
        self.RPG_Game.triggered.connect(self.show_RPG_Game)
        self.game_menu.addAction(self.RPG_Game)
        self.game_menu.addSeparator()
        self.word_game_action = QAction('单词打字', self)
        self.word_game_action.triggered.connect(self.show_word_game)
        self.game_menu.addAction(self.word_game_action)
        self.game_action.setMenu(self.game_menu)
        self.menu.addAction(self.game_action)
        self.menu.addSeparator()
        self.time_gallery_action = QAction("时间长廊", self)
        self.time_gallery_action.triggered.connect(self.show_time_gallery)
        self.menu.addAction(self.time_gallery_action)
        self.menu.addSeparator()
        self.exit_action = QAction("退出", self)
        self.exit_action.triggered.connect(self.close)
        self.menu.addAction(self.exit_action)
        self.menu.addSeparator()
        self.update_weather_icon()
        self.init_animation()



    def init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(1200, 800, 200, 200)



    def closeEvent(self, event):
        self.close_ani()
        if self.chat_window:
            self.chat_window.close()
        if self.weather_window:
            self.weather_window.close()
        if self.RPG_game_window:
            self.RPG_game_window.close()
        self.PDH.log_mood_card(global_value.CURRENT_WEATHER,'好',random.choice([1,2,3,4,5]), "default")
        self.PDH.end_session()
        event.accept()

    def init_animation(self):
        self.animation_label = QLabel(self)
        self.animation_label.move(10,10)
        self.animations = {
                        'box': 'img/character/box.gif',
                        'cry': 'img/character/cry.gif',
                        'excite': 'img/character/excite.gif',
                        'happy-1': 'img/character/happy-1.gif',
                        'idle': 'img/character/idle.gif',
                        'lay': 'img/character/lay.gif',
                        'sleep-1': 'img/character/sleep-1.gif',
                        'sleepy-1': 'img/character/sleepy-1.gif',
                        'surprise': 'img/character/surprise.gif'
                    }
        self.current_animation = None
        self.appear_animation()

    def appear_animation(self):
        self.play_animation(self.animations['box'])
        self.stand_action()

    def stand_action(self):
        self.play_animation(self.animations['idle'])

    def random_action(self):
        new_animation = random.choice(list(self.animations.values()))
        if new_animation != self.current_animation:
            self.play_animation(new_animation)
        self.stand_action()

    def play_animation(self, gif_path):
        movie = QMovie(gif_path)
        self.animation_label.setMovie(movie)
        movie.start()
        self.current_animation = gif_path

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.click_start_pos = event.pos()  # 记录点击起始位置
            self.is_dragging = False
            self.drag_start_pos = event.globalPos() - self.pos()
            self.clk_start_time = event.timestamp()
            
            self.click_timer.start()  # 开始计时器
        elif event.button() == Qt.RightButton:
            self.menu.exec_(self.mapToGlobal(event.pos()))

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.click_start_pos:
            # 计算移动距离
            move_distance = (event.pos() - self.click_start_pos).manhattanLength()
            if move_distance > self.click_threshold or self.is_dragging:
                # 超过阈值视为拖动
                self.clk_timer.stop()
                self.is_dragging = True
                self.move(event.globalPos() - self.drag_start_pos)
                self.play_animation(self.animations['excite'])


    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton :
            self.click_timer.stop()
            if not self.is_dragging:
                elapsed_time = event.timestamp() - self.clk_start_time
                if elapsed_time < 500:
                    pass
                else :
                    self.on_timeout()
        self.stand_action()


    def on_timeout(self):
        self.is_dragging = True
        self.play_animation('img/character/surprise.gif')

    def show_chat_window(self):
        if not self.chat_window:
            self.chat_window = PsychChatWindow(self,self.PDH)
        self.chat_window.show()

    def update_weather_icon(self):
        """更新天气图标"""

        self.weather_label.setPixmap(QPixmap(self.weather_window.get_current_weather_icon()))

    def show_weather_window(self):
        """显示天气详情窗口"""


        self.weather_window.weather_show()

    def show_RPG_Game(self):

        if self.RPG_game_window:
            self.RPG_game_window.close()  # 关闭旧窗口
        self.RPG_game_window = RPGGame(self.PDH)
        self.RPG_game_window.RPG_game_show()


    def show_random_bubble(self):
        if random.random() < 0.7:
            mes=self.speak_randomly()
            self.display_bubble(mes)

    def display_bubble(self, message):
        self.bubble.setText(message)
        self.bubble.adjustSize()

        # 计算气泡位置（在宠物右侧）
        pet_pos = self.pos()
        bubble_x = pet_pos.x()  + 45
        bubble_y = pet_pos.y()

        self.bubble.move(bubble_x, bubble_y)
        self.bubble.show()
        QTimer.singleShot(self.bubble_duration, self.bubble.hide)

    def speak_randomly(self):
        """随机发言"""
         # 假设宠物有获取天气的方法
        weather_type = self.weather_mapping.get(global_value.CURRENT_WEATHER, "default")

        responses = self.weather_responses.get(weather_type, []) + self.weather_responses["default"]
        message = random.choice(responses)
        return message

    def show_time_gallery(self):
        if not self.time_gallery_window:
            self.time_gallery_window = TimeGalleryWindow(self, self.PDH)
        self.time_gallery_window.show_gallery()
        print(self.PDH.get_today_conversations())

    def close_ani(self):
        pass

    def show_word_game(self):
        if hasattr(self, 'word_game_window'):
            self.word_game_window.close()
        self.word_game_window = WordTypingGame(self.PDH)
        self.word_game_window.show_game()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pet = DesktopPet()
    pet.show()
    sys.exit(app.exec_())