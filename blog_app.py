from flask import Flask, request, jsonify, render_template
import time
from db import MySQLDatabase
from redis_cache import RedisCache

app = Flask(__name__)

# 配置项（请根据实际情况修改）
MYSQL_CONFIG = {
    "host": "localhost",
    "user": "db_user",
    "password": "db_password",
    "database": "techblog_db",
    "port": 3306
}

REDIS_CONFIG = {
    "host": "localhost",
    "port": 6379,
    "password": "redis_password"
}

mysql_db = MySQLDatabase(**MYSQL_CONFIG)
redis_cache = RedisCache(**REDIS_CONFIG)

@app.route('/')
def index():
    """
    首页：展示最新的博客文章列表，优先从 Redis 缓存中获取数据
    """
    posts = redis_cache.get_cached_posts()
    if not posts:
        posts = mysql_db.get_posts(limit=10)
        redis_cache.cache_posts(posts)
    return render_template('index.html', posts=posts)

@app.route('/publish', methods=['POST'])
def publish():
    """
    发布博客文章，要求 JSON 格式数据包含：title, content, author
    系统自动记录当前 Unix 时间戳作为 created_at
    """
    data = request.get_json()
    required_fields = ["title", "content", "author"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"缺少字段: {field}"}), 400

    post_data = {
        "title": data.get("title"),
        "content": data.get("content"),
        "author": data.get("author"),
        "created_at": int(time.time())
    }
    try:
        mysql_db.insert_post(post_data)
        # 清空缓存，以便下次重新查询
        redis_cache.r.delete("latest_posts")
    except Exception as e:
        return jsonify({"error": f"MySQL 插入错误: {str(e)}"}), 500

    return jsonify({"status": "发布成功", "post": post_data}), 200

@app.route('/api/posts', methods=['GET'])
def api_get_posts():
    """
    提供 API 接口，返回最新博客文章列表（JSON 格式）
    """
    posts = redis_cache.get_cached_posts()
    if not posts:
        posts = mysql_db.get_posts(limit=10)
        redis_cache.cache_posts(posts)
    return jsonify({"posts": posts}), 200

if __name__ == '__main__':
    # 监听所有 IP，端口 5000，调试模式开启
    app.run(host='0.0.0.0', port=5000, debug=True)
