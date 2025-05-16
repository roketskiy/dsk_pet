import datetime
import sqlite3
import uuid
from PetDatabase import PetDatabase


class PetDataHandler:
    def __init__(self):
        self.db = PetDatabase()
        self.current_session = None
        self.conn = self.db.conn

    def start_session(self, username="default"):
        """开始新会话"""
        try:
            cursor = self.db.conn.cursor()

            # 检查用户是否存在，不存在则创建
            cursor.execute("SELECT user_id FROM users WHERE username=?", (username,))
            user = cursor.fetchone()

            if not user:
                cursor.execute("INSERT INTO users (username) VALUES (?)", (username,))
                user_id = cursor.lastrowid
            else:
                user_id = user[0]

            # 创建新会话
            session_id = str(uuid.uuid4())
            cursor.execute(
                "INSERT INTO sessions (session_id, user_id) VALUES (?, ?)",
                (session_id, user_id)
            )

            self.db.conn.commit()
            self.current_session = session_id
            return session_id

        except sqlite3.Error as e:
            self.db.conn.rollback()
            raise Exception(f"无法开始会话: {str(e)}")

    def end_session(self):
        """结束当前会话"""
        if not self.current_session:
            return

        try:
            cursor = self.db.conn.cursor()
            cursor.execute(
                "UPDATE sessions SET end_time=datetime('now', 'localtime') WHERE session_id=?",
                (self.current_session,)
            )
            self.db.conn.commit()
            self.current_session = None

        except sqlite3.Error as e:
            self.db.conn.rollback()
            raise Exception(f"无法结束会话: {str(e)}")

    def log_chat_message(self, role, content):
        """记录聊天消息"""
        if not self.current_session:
            return

        try:
            cursor = self.db.conn.cursor()
            cursor.execute(
                """INSERT INTO chat_logs 
                (session_id, role, content) 
                VALUES (?, ?, ?)""",
                (self.current_session, role, content)
            )
            self.db.conn.commit()

        except sqlite3.Error as e:
            self.db.conn.rollback()
            raise Exception(f"无法记录聊天消息: {str(e)}")

    def log_game_score(self, points):
        """记录游戏得分"""
        if not self.current_session:
            return

        try:
            cursor = self.db.conn.cursor()

            # 获取用户所有会话的最新得分记录作为初始值
            cursor.execute(
                """SELECT gs.total_score 
                FROM game_scores gs 
                JOIN sessions s ON gs.session_id = s.session_id
                WHERE s.user_id = (
                    SELECT user_id FROM sessions WHERE session_id = ?
                )
                ORDER BY gs.score_id DESC LIMIT 1""",
                (self.current_session,)
            )
            last_total = cursor.fetchone()
            base_score = last_total[0] if last_total else 0

            # 记录单次得分并更新总得分
            cursor.execute(
                "INSERT INTO game_scores (session_id, points, total_score) VALUES (?, ?, ?)",
                (self.current_session, points, base_score + points)
            )

            self.db.conn.commit()

        except sqlite3.Error as e:
            self.db.conn.rollback()
            raise Exception(f"无法记录游戏得分: {str(e)}")

    def get_local_date(self):
        """获取本地日期"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT date('now', 'localtime')")
        return cursor.fetchone()[0]

    def log_weather_data(self, weather_data):
        """记录天气数据"""
        if not self.current_session:
            return

        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """INSERT INTO mood_cards 
                (session_id, weather, date) 
                VALUES (?, ?, datetime('now', 'localtime'))""",
                (self.current_session, weather_data)
            )
            self.conn.commit()
            return True

        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"无法记录天气数据: {str(e)}")

    def __del__(self):
        self.conn.close()

    def get_chat_history(self, session_id):
        """获取指定会话的聊天记录"""
        cursor = self.conn.cursor()
        cursor.execute(
            """SELECT role, content, timestamp 
            FROM chat_logs 
            WHERE session_id = ? 
            ORDER BY timestamp""",
            (session_id,)
        )
        return cursor.fetchall()

    def get_user_stats(self, username):
        """获取用户统计数据"""
        cursor = self.conn.cursor()

        # 总得分
        cursor.execute(
            """SELECT SUM(gs.total_score) 
            FROM game_scores gs 
            JOIN sessions s ON gs.session_id = s.session_id
            WHERE s.user_id = (
                SELECT user_id FROM users WHERE username = ?
            )""",
            (username,)
        )
        total_score = cursor.fetchone()[0] or 0

        # 会话次数
        cursor.execute(
            """SELECT COUNT(*) 
            FROM sessions 
            WHERE user_id = (
                SELECT user_id FROM users WHERE username = ?
            )""",
            (username,)
        )
        session_count = cursor.fetchone()[0]

        return {
            'username': username,
            'total_score': total_score,
            'session_count': session_count
        }

    def get_mood_cards(self, username):
        """获取用户的所有情绪卡片"""
        cursor = self.conn.cursor()
        cursor.execute(
            """SELECT mc.date, mc.weather, mc.mood_summary, mc.evaluate
            FROM mood_cards mc
            JOIN users u ON mc.user_id = u.user_id
            WHERE u.username = ?
            ORDER BY mc.date DESC""",
            (username,)
        )
        return cursor.fetchall()

    def log_mood_card(self, weather, mood_summary, evaluate, username="default"):
        """记录情绪卡片
        如果当天已有记录则更新，否则新建一条记录（仅基于日期判断）
        """
        try:
            current_date = datetime.datetime.now().strftime("%Y-%m-%d")
            cursor = self.db.conn.cursor()

            # 获取用户ID
            cursor.execute("SELECT user_id FROM users WHERE username=?", (username,))
            user = cursor.fetchone()
            if not user:
                raise Exception("用户不存在")
            user_id = user[0]

            # 检查当天是否已有记录（仅基于日期）
            cursor.execute(
                """SELECT card_id FROM mood_cards 
                WHERE date(date) = date(?)
                AND user_id = ?""",
                (current_date, user_id)
            )
            existing_record = cursor.fetchone()

            if existing_record:
                # 更新现有记录
                cursor.execute(
                    """UPDATE mood_cards 
                    SET weather = ?, mood_summary = ?, evaluate = ?
                    WHERE date(date) = date(?)
                    AND user_id = ?""",
                    (weather, mood_summary, evaluate, current_date, user_id)
                )
            else:
                # 插入新记录
                cursor.execute(
                    """INSERT INTO mood_cards 
                    (user_id, date, weather, mood_summary, evaluate) 
                    VALUES (?, ?, ?, ?, ?)""",
                    (user_id, current_date, weather, mood_summary, evaluate)
                )

            self.db.conn.commit()
        except sqlite3.Error as e:
            self.db.conn.rollback()
            raise Exception(f"无法记录情绪卡片: {str(e)}")

    def get_today_conversations(self, username=None):
        """获取当天所有对话记录

        参数:
            username: (可选) 指定要查询的用户名，如果为None则返回所有用户的当天对话

        返回:
            包含当天所有对话记录的列表，每个记录包含:
            - session_id: 会话ID
            - username: 用户名
            - start_time: 会话开始时间
            - messages: 该会话的所有消息列表(role, content, timestamp)
        """
        try:
            cursor = self.conn.cursor()
            today = datetime.datetime.now().strftime("%Y-%m-%d")

            # 使用明确的日期比较
            query = """
            SELECT s.session_id, u.username, s.start_time
            FROM sessions s
            JOIN users u ON s.user_id = u.user_id
            WHERE date(s.start_time) = date(?)
            AND date(?) = date('now', 'localtime')
            """

            # 如果指定了用户名，添加过滤条件
            params = [today, today]
            if username:
                query += " AND u.username = ?"
                params.append(username)

            query += " ORDER BY s.start_time DESC"

            cursor.execute(query, params)
            sessions = cursor.fetchall()

            result = []
            for session_id, username, start_time in sessions:
                # 获取每个会话的消息
                messages = self.get_chat_history(session_id)
                result.append({
                    'session_id': session_id,
                    'username': username,
                    'start_time': start_time,
                    'messages': messages
                })

            return result

        except sqlite3.Error as e:
            raise Exception(f"无法获取当天对话: {str(e)}")

    def get_cet4_words(self, limit=None):
        """从CET4表获取单词

        参数:
            limit: (可选) 限制返回的单词数量

        返回:
            包含(word, translate)元组的列表
        """
        try:
            cursor = self.conn.cursor()
            query = "SELECT word, translate FROM CET4"
            if limit:
                query += f" LIMIT {int(limit)}"
            cursor.execute(query)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"获取CET4单词失败: {str(e)}")
            return []

    def get_cet6_words(self, limit=None):
        """从CET6表获取单词

        参数:
            limit: (可选) 限制返回的单词数量

        返回:
            包含(word, translate)元组的列表
        """
        try:
            cursor = self.conn.cursor()
            query = "SELECT word, translate FROM CET6"
            if limit:
                query += f" LIMIT {int(limit)}"
            cursor.execute(query)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"获取CET6单词失败: {str(e)}")
            return []