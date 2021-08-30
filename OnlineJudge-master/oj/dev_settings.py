# coding=utf-8
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# DB 설정
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': '127.0.0.1',
        'PORT': 4568,
        'NAME': "onlinejudge",
        'USER': "onlinejudge",
        'PASSWORD': 'onlinejudge'
    }
}

# REDIS 설정
REDIS_CONF = {
    "host": "127.0.0.1",
    "port": "6379"
}


DEBUG = True

# 허용 호스트 설정 
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "192.168.0.1", "192.168.0.2", "dofh.iptime.org"]

DATA_DIR = f"{BASE_DIR}/data"
