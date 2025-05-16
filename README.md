小忆 - AI桌面宠物伴侣

项目简介

小忆是一款集情感陪伴、学习辅助和娱乐功能于一体的智能桌面宠物应用。它结合了AI聊天、天气提醒、单词学习和休闲小游戏等功能，为用户提供温暖贴心的桌面陪伴体验。

主要功能

1. AI情感陪伴
• 基于DeepSeek API的智能对话系统

• 情感识别与回应功能

• 聊天记录保存与回顾


2. 天气服务
• 自动定位获取当地天气

• 天气图标动态显示

• 根据天气提供贴心建议


3. 学习辅助
• 英语单词打字练习游戏

• 支持CET4/CET6/考研词汇

• 实时正确率统计


4. 休闲游戏
• 猜拳小游戏

• 积分系统记录成绩


5. 情绪记录
• 每日心情卡片记录

• 可视化时间轴回顾

• 天气与心情关联分析


技术特点

• 基于PyQt5的跨平台GUI

• SQLite本地数据存储

• 多线程处理网络请求

• 响应式UI设计

• 可扩展的模块化架构


安装与运行

环境要求
• Python 3.7+

• PyQt5

• requests库

• sqlite3


运行步骤
1. 克隆仓库或下载源代码
2. 安装依赖：`pip install PyQt5 requests`
3. 运行主程序：`python DesktopPet.py`

使用说明

1. 右键点击宠物打开功能菜单
2. 选择"和小忆说说话"开始聊天
3. 使用"回忆卡片"查看历史心情记录
4. 通过"玩玩小游戏"选择休闲游戏
5. 天气图标实时显示当前天气状况

项目结构

```
小忆/
├── DesktopPet.py        # 主程序
├── PetDataHandler.py    # 数据处理
├── PetDatabase.py       # 数据库管理
├── PsychChatWindow.py   # 聊天窗口
├── TimeGalleryWindow.py # 回忆卡片
├── WeatherWindow.py     # 天气窗口
├── Pet_Game_1.py       # 猜拳游戏
├── WordTypingGame.py   # 单词游戏
├── global_value.py     # 全局变量
├── img/                # 资源图片
└── pet_data.db         # 数据库文件
```

未来计划

• 增加更多宠物外观选择

• 开发更多学习游戏

• 添加语音交互功能

• 优化AI对话体验

• 增加多语言支持


贡献指南

欢迎提交Issue和Pull Request，共同完善小忆的功能！

许可证

MIT License
