import requests
import json
import global_value
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QApplication)
from PyQt5.QtCore import Qt, QMargins, pyqtSignal, QThread, QRectF
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QLinearGradient, QFont
from PyQt5.QtChart import QChart, QChartView, QValueAxis, QAreaSeries, QCategoryAxis, QSplineSeries, QPieSeries, \
    QPieSlice


class EmotionAnalysisWindow(QWidget):
    def __init__(self, parent=None, PDH=None):
        super().__init__()
        self.parent = parent
        self.PDH = PDH
        self.setWindowTitle("情绪分析")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(1000, 1000)



        self.init_ui()
        self.load_history_data()  # 自动加载历史数据

    def init_ui(self):
        self.main_container = QWidget(self)
        self.main_container.setObjectName("mainContainer")
        self.main_container.setStyleSheet("""
            #mainContainer {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                border-bottom-left-radius: 15px;
                border-bottom-right-radius: 15px;
                
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
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgb(111, 230, 252), stop:1 #FFFFFF);
            border-top-left-radius: 15px;
            border-top-right-radius: 15px;
            padding-left: 15px;
        """)

        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(0, 0, 10, 0)

        title_icon = QLabel()
        title_icon.setPixmap(
            QPixmap('img/data.png').scaled(36, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        title_icon.setStyleSheet("background: transparent;")

        title_text = QLabel("情绪分析")
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

        # 分析按钮区域
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(15, 10, 15, 10)
        button_layout.setSpacing(15)

        self.analyze_btn = QPushButton("分析今日情绪")
        self.analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: rgb(204,204,255);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 14px;
                font-family: 'Microsoft YaHei';
                min-width: 120px;
                
            }
            QPushButton:hover {
                background-color:rgb(153,153,191);
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.analyze_btn.clicked.connect(self.analyze_today_emotion)



        button_layout.addWidget(self.analyze_btn)


        # 图表区域
        self.chart_widget =QWidget()
        self.chart_widget.setStyleSheet("""
            QWidget {
                background: transparent;
                };
        """)
        self.chart_widget.setFixedHeight(350)

        chart_widget_layout= QHBoxLayout(self.chart_widget)
        chart_widget_layout.setContentsMargins(0, 0, 0, 0)
        chart_widget_layout.setSpacing(0)

        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_view.setStyleSheet("background: transparent;")
        self.chart_view.setFixedWidth(600)




        self.chart_vview=QChartView()
        self.chart_vview.setRenderHint(QPainter.Antialiasing)
        self.chart_vview.setStyleSheet("background: transparent;")
        self.chart_view.setFixedWidth(400)


        chart_widget_layout.addWidget(self.chart_view)
        chart_widget_layout.addWidget(self.chart_vview)

        # 结果展示区域
        self.result_widget=QWidget()
        self.result_widget.setFixedHeight(200)
        self.result_widget.setStyleSheet("""
            QWidget {
            background: transparent;
            border-bottom-left-radius: 15px;
            border-bottom-right-radius: 15px;
            }
        """)
        result_layout = QVBoxLayout(self.result_widget)
        self.result_label = QLabel()
        self.result_label.setWordWrap(True)
        self.result_label.setStyleSheet("""
            QLabel {
                background: rgba(240, 240, 240, 0.8);
                border-radius: 10px;
                padding: 15px;
                margin: 15px;
                font-size: 14px;
                font-family: 'Microsoft YaHei';
            }
        """)
        self.result_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        result_layout.addWidget(self.result_label)

        # 将组件添加到主布局
        main_layout.addWidget(title_bar)
        main_layout.addWidget(button_widget)
        main_layout.addWidget(self.chart_widget)
        main_layout.addWidget(self.result_widget)

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

    def analyze_today_emotion(self):
        """分析今日情绪"""
        self.analyze_btn.setEnabled(False)

        self.result_label.setText("正在分析今日情绪，请稍候...")

        conversations = self.PDH.get_daily_conversations()
        if not conversations:
            self.result_label.setText("今天还没有对话记录哦，先和小忆聊聊天吧~")
            self.analyze_btn.setEnabled(True)

            return

        # 创建并启动工作线程
        self.worker = AnalysisWorker(self.PDH, conversations)
        self.worker.finished.connect(self.on_analysis_finished)
        self.worker.error.connect(self.on_analysis_error)
        self.worker.start()

    def load_history_data(self):
        """绘制左侧情绪线图和右侧饼图"""
        try:
            mood_data = self.PDH.get_mood_cards("default")
            if not mood_data:
                self.create_empty_chart()
                return
            mood_data.sort(key=lambda x: x[0])  # 按日期升序排序

            # 准备数据
            dates = []
            scores = []
            emotion_counts = {
                "积极(4-5分)": 0,
                "中性(3分)": 0,
                "消极(0-2分)": 0
            }


            for date, _, _, score in mood_data:
                dates.append(date)
                scores.append(float(score))

                if score >= 4:
                    emotion_counts["积极(4-5分)"] += 1
                elif score >= 3:
                    emotion_counts["中性(3分)"] += 1
                else:
                    emotion_counts["消极(0-2分)"] += 1

            # 创建左侧折线图
            line_chart = QChart()
            line_chart.setBackgroundBrush(QColor(0, 0, 0, 0))
            line_chart.setTitle("情绪变化趋势")
            line_chart.setTitleFont(QFont("Microsoft YaHei", 10))
            line_chart.legend().hide()

            # 创建折线系列
            line_series = QSplineSeries()
            line_series.setName("情绪评分")
            line_series.setColor(QColor(70, 134, 197))

            for i, score in enumerate(scores):
                line_series.append(i, score)

            # 创建区域系列（用于填充）
            area_series = QAreaSeries(line_series)
            area_series.setName("情绪评分")

            # 设置渐变填充
            gradient = QLinearGradient()
            gradient.setColorAt(0, QColor(70, 134, 197, 150))
            gradient.setColorAt(1, QColor(70, 134, 197, 50))
            area_series.setBrush(gradient)
            area_series.setPen(QPen(QColor(70, 134, 197, 0)))

            line_chart.addSeries(area_series)
            line_chart.addSeries(line_series)

            # 设置X轴（日期）
            axis_x = QCategoryAxis()
            axis_x.setLabelsFont(QFont("Microsoft YaHei", 8))
            axis_x.setTitleText("日期")

            # 只显示部分日期标签，避免重叠
            step = max(1, len(dates) // 5)
            for i in range(0, len(dates), step):
                axis_x.append(dates[i][5:10], i)

            axis_x.setRange(0, len(dates) - 1)
            line_chart.addAxis(axis_x, Qt.AlignBottom)
            line_series.attachAxis(axis_x)

            # 设置Y轴（分数）
            axis_y = QValueAxis()
            axis_y.setRange(0,6 )
            axis_y.setTickCount(6)
            axis_y.setLabelFormat("%.1f")
            axis_y.setTitleText("情绪评分")
            axis_y.setLabelsFont(QFont("Microsoft YaHei", 8))
            line_chart.addAxis(axis_y, Qt.AlignLeft)
            line_series.attachAxis(axis_y)

            # 创建右侧饼图
            pie_chart = QChart()
            pie_chart.setBackgroundBrush(QColor(0, 0, 0, 0))
            pie_chart.setTitle("情绪分布")
            pie_chart.setTitleFont(QFont("Microsoft YaHei", 10))

            pie_series = QPieSeries()

            # 添加饼图切片
            colors = {
                "积极(4-5分)": QColor(91, 189, 114),
                "中性(3分)": QColor(247, 186, 30),
                "消极(0-2分)": QColor(232, 80, 80)
            }

            for label, count in emotion_counts.items():
                if count > 0:
                    slice = QPieSlice(label, count)
                    slice.setColor(colors[label])
                    slice.setLabelFont(QFont("Microsoft YaHei", 8))
                    slice.setLabelVisible(True)
                    slice.setLabelPosition(QPieSlice.LabelOutside)
                    pie_series.append(slice)

            pie_chart.addSeries(pie_series)

            # 设置图表视图
            self.chart_view.setChart(line_chart)
            self.chart_vview.setChart(pie_chart)

        except Exception as e:
            print(f"绘制情绪图表失败: {str(e)}")
            self.create_empty_chart()

    def create_empty_chart(self):
        """创建空图表"""
        chart = QChart()
        chart.setBackgroundBrush(QColor(0, 0, 0, 0))
        chart.setTitle("暂无情绪数据")
        chart.setTitleBrush(QColor(70, 70, 70))
        self.chart_view.setChart(chart)

    def show_analysis(self):
        """显示分析窗口并调整位置"""
        self.adjust_position()
        self.show()
        self.load_history_data()  # 自动显示历史图表

    def adjust_position(self):
        """调整窗口位置"""
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

    def view_emotion_history(self):
        pass
    def on_analysis_finished(self, analysis_result):
        """分析成功回调"""
        try:
            result = json.loads(analysis_result)
            score = float(result.get("情感评分", 3))
            summary = result.get("关键摘要", "未获取到摘要")
            emotion = result.get("主要情绪", "中性")

            self.PDH.log_mood_card(
                weather=global_value.CURRENT_WEATHER,
                mood_summary=summary,
                evaluate=score,
                username="default"
            )

            self.result_label.setText(
                f"今日情绪分析结果:\n\n"
                f"情感评分: {score}/5\n"
                f"主要情绪: {emotion}\n"
                f"关键摘要: {summary}\n\n"
            )
            self.load_history_data()
        except (json.JSONDecodeError, ValueError) as e:
            self.result_label.setText(f"分析结果解析错误: {str(e)}\n原始结果:\n{analysis_result}")
        finally:
            self.analyze_btn.setEnabled(True)


    def on_analysis_error(self, error_msg):
        """分析失败回调"""
        self.result_label.setText(f"情绪分析失败: {error_msg}")
        self.analyze_btn.setEnabled(True)






class AnalysisWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, PDH, conversations):
        super().__init__()
        self.PDH = PDH
        self.conversations = conversations

    def run(self):
        try:
            analysis_result = self.analyze_with_deepseek("\n".join(self.conversations))
            self.finished.emit(analysis_result)
        except Exception as e:
            self.error.emit(str(e))

    def analyze_with_deepseek(self, texts):
        """使用DeepSeek API进行情感分析"""
        url = "https://api.deepseek.com/chat/completions"
        headers = {
            "Authorization": f"Bearer {global_value.Params['key_DS']}",
            "Content-Type": "application/json"
        }
        prompt = f"""
                请对以下对话进行情感分析和总结：
                {texts}
                要求：
                1. 情感评分：[在这里填写0-5分的评分，5分为最积极]
                2. 关键摘要：[在这里填写不超过50字的摘要,不要使用用户来称呼]
                3. 主要情绪：[在这里填写主要情绪，如快乐、愤怒、悲伤等]
                请按照json格式返回结果,前面不要带json标识。
                """
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2
        }
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        if "choices" in result:
            return result["choices"][0]["message"]["content"]
        else:
            return "分析失败：" + str(result)