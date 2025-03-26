import redis
import json

class RedisCache:
    def __init__(self, host, port, password=None):
        self.r = redis.Redis(host=host, port=port, password=password, decode_responses=True)

    def cache_posts(self, posts):
        """
        将文章列表缓存到 Redis，key 固定为 "latest_posts"，缓存时间设置为 60 秒
        """
        key = "latest_posts"
        value = json.dumps(posts)
        self.r.set(key, value, ex=60)

    def get_cached_posts(self):
        key = "latest_posts"
        value = self.r.get(key)
        if value:
            return json.loads(value)
        return None
