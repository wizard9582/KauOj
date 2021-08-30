import json
import os

import requests # 요청 처리 모듈

from exception import JudgeServiceError
from utils import server_info, logger, token # 서버 정보 받는 모듈, 로그 추적 모듈, 환경변수 읽는 토큰
# from utils import server_info, token
from time import sleep

class JudgeService(object):
    # 서비스 초기화
    def __init__(self):
        # 서비스 URL과 백엔드 서버 URL을 읽어온 후 저장.
        # self.service_url = os.environ["SERVICE_URL"]
        self.service_url = "218.232.126.167:666"
        # self.backend_url = os.environ["BACKEND_URL"]
        self.backend_url = "http://dofh.iptime.org:8000/api/judge_server_heartbeat"

    def _request(self, data):
        try:
            # HTTP post method로 요청
            # json 모듈을 이용해 헤더 정보 요청
            # 백엔드 서버 URL에 토큰 정보와 json으로 이루어진 컨텐츠 요청
            resp = requests.post(self.backend_url, json=data,
                                 headers={"X-JUDGE-SERVER-TOKEN": token,
                                          "Content-Type": "application/json"}, timeout=5).text
        except Exception as e:
            # 예외처리 (timeout)
            logger.exception(e)
            raise JudgeServiceError("Heartbeat request failed")
        try:
            # 요청한 데이터 적재
            r = json.loads(resp)
            if r["error"]:
                raise JudgeServiceError(r["data"])
        except Exception as e:
            logger.exception("Heartbeat failed, response is {}".format(resp))
            raise JudgeServiceError("Invalid heartbeat response")

    # 주기적으로 서버와 연결이 이루어져있는지 확인
    def heartbeat(self):
        print("repeat!")
        data = server_info() # 서버 정보 (utils.py에서 정의)
        # server_info의 json 구조에 action과 service_url을 추가
        data["action"] = "heartbeat" 
        data["service_url"] = self.service_url
        # 해당되는 데이터를 요청
        self._request(data)
        print("got it?")


if __name__ == "__main__":
    try:
        # 연결 실행 후 연결상태 확인
        print("Try to connect")
        if not os.environ.get("DISABLE_HEARTBEAT"):
            service = JudgeService()
            service.heartbeat()
        exit(0)
    # 예외가 발생한 경우 예외 출력, 연결 종료
    except Exception as e:
        logger.exception(e)
        print("failed to send heartbeat")
        print(e)
        exit(1)