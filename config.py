import logging
from redis import StrictRedis


class Config(object):
    """项目的配置"""

    SECRET_KEY = "iECgbYWReMNxkRprrzMo5KAQYnb2UeZ3bwvReTSt+VSESW0OB8zbglT+6rEcDW9X"

    # 为数据库添加配置
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/news_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 在请求结束时候，如果指定此配置为 True ，那么 SQLAlchemy 会自动执行一次 db.session.commit()操作
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    # Redis的配置
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379
    DB = 0

    # Session保存配置
    SESSION_TYPE = "redis"
    # 开启session签名
    SESSION_USE_SIGNER = True
    # 指定 Session 保存的 redis
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=DB)
    # 设置需要过期
    SESSION_PERMANENT = False
    # 设置过期时间
    PERMANENT_SESSION_LIFETIME = 86400 * 2

    # 设置日志等级
    LOG_LEVEL = logging.DEBUG


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = logging.WARNING


class TestingConfig(Config):
    DEBUG = True
    TEST = True


config = {
    "Development": DevelopmentConfig,
    "Production": ProductionConfig,
    "Testing": TestingConfig
}