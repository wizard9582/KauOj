"""
백 엔드와 마찬가지로 자주 사용하는 기능 모듈 정의
"""
import os
import sys
# sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append('/mnt/c/Users/dezar/Desktop/OJ/Judger-newnew/bindings/Python') 
sys.path.append('/home/chris/OJ/JudgeServer-master/log') 
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import _judger
import hashlib # 암호화 보안을 위한 모듈
import logging # 에러 로그 추적 모듈
import socket # 소켓 통신을 위한 모듈

import psutil # 프로파일링 및 프로세스 자원 제한 및 관리를 위한 모듈

from config import SERVER_LOG_PATH # 서버 통신 로그
from exception import JudgeClientError # 클라이언트 에러 예외처리


logger = logging.getLogger(__name__) # 추적 로그 변수 지정
handler = logging.FileHandler(SERVER_LOG_PATH) # 서버 통신 로그 추적 핸들러 지정
# 출력될 로그 포맷 지정 및 로그 변수에 핸들러 추가
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s') 
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.WARNING)


def server_info():
    ver = _judger.VERSION
    # 통신하는 서버의 정보를 JSON형식으로 반환
    return {"hostname": socket.gethostname(),
            "cpu": psutil.cpu_percent(),
            "cpu_core": psutil.cpu_count(),
            "memory": psutil.virtual_memory().percent,
            "judger_version": ".".join([str((ver >> 16) & 0xff), str((ver >> 8) & 0xff), str(ver & 0xff)])}


def get_token():
    # token = os.environ.get("TOKEN") # 환경 변수를 읽기
    token = 'KAUOJ'
    if token:
        return token
    else:
        # 토큰이 없는 경우 에러 반환
        raise JudgeClientError("env 'TOKEN' not found")

# 입력받은 문제의 처리 형식 지정
class ProblemIOMode:
    standard = "Standard IO"
    file = "File IO"

# 토큰은 암호화를 거쳐서 get
token = hashlib.sha256(get_token().encode("utf-8")).hexdigest()