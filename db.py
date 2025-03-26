import mysql.connector

class MySQLDatabase:
    def __init__(self, host, user, password, database, port=3306):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port

    def get_connection(self):
        return mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
            port=self.port
        )

    def insert_post(self, post_data):
        """
        插入博客文章，表结构：id (自增主键), title, content, author, created_at (时间戳)
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        query = ("INSERT INTO posts (title, content, author, created_at) "
                 "VALUES (%s, %s, %s, %s)")
        cursor.execute(query, (
            post_data.get("title"),
            post_data.get("content"),
            post_data.get("author"),
            post_data.get("created_at")
        ))
        conn.commit()
        cursor.close()
        conn.close()

    def get_posts(self, limit=10):
        """
        查询最新的博客文章列表
        """
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM posts ORDER BY created_at DESC LIMIT %s"
        cursor.execute(query, (limit,))
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
