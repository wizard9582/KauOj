import hashlib # 암호화 보안을 위한 모듈
import json
import os
import shutil # 파일의 복사, 삭제 연산을 위한 모듈
import uuid # 난수가 아닌 고유 ID를 얻기 위한 모듈

import sys
sys.path.append('/home/chris/OJ/JudgeServer-master/log') 

"""
Django보다 더 가볍고 간단한 기능만을 사용하기 위해 Flask를 이용.
Flask 객체를 변수에 할당 후, 해당 변수를 통해 라우팅 경로를 설정,
해당 라우팅 경로로 요청이 올 때 실행할 함수를 작성해 백엔드 서버와 통신 준비를 마친다.
"""
# 통신에 필요한 Flask의 request, Response 모듈 import
from flask import Flask, request, Response

# 우리가 작성한 모듈
from compiler import Compiler

from config import (JUDGER_WORKSPACE_BASE, SPJ_SRC_DIR, SPJ_EXE_DIR, COMPILER_USER_UID, SPJ_USER_UID,
                    RUN_USER_UID, RUN_GROUP_GID, TEST_CASE_DIR)
from exception import TokenVerificationFailed, CompileError, SPJCompileError, JudgeClientError
from judge_client import JudgeClient
from utils import server_info, logger, token, ProblemIOMode
# from utils import server_info, token, ProblemIOMode


 # Flask 객체를 변수 app에 할당 후 디버그 모드 활성화
app = Flask(__name__)
DEBUG = os.environ.get("judger_debug") == "1"
app.debug = DEBUG

# 제출 환경 초기화
class InitSubmissionEnv(object):
    def __init__(self, judger_workspace, submission_id, init_test_case_dir=False):
        # 실행 디렉터리, 초기 테스트 케이스 디렉터리 경로 설정
        self.work_dir = os.path.join(judger_workspace, submission_id)
        self.init_test_case_dir = init_test_case_dir
        # 테스트 케이스 디렉터리를 잡지 못할 경우 다시 설정
        if init_test_case_dir:
            self.test_case_dir = os.path.join(self.work_dir, "submission_" + submission_id)
        else:
            self.test_case_dir = None
    
    # 런타임 실행 디렉터리 생성, 사용자의 컴파일 ID, 그룹 DB 기록 경로 지정
    def __enter__(self):
        try:
            os.makedirs(self.work_dir, exist_ok=True)
            if self.init_test_case_dir:
                os.makedirs(self.test_case_dir, exist_ok=True)
            os.chown(self.work_dir, COMPILER_USER_UID, RUN_GROUP_GID)
            os.chmod(self.work_dir, 0o711)
        except Exception as e:
            logger.exception(e)
            raise JudgeClientError("failed to create runtime dir")
        return self.work_dir, self.test_case_dir

    # 런타임 초기화 작업 종료
    def __exit__(self, exc_type, exc_val, exc_tb):
        if not DEBUG:
            try:
                shutil.rmtree(self.work_dir)
            except Exception as e:
                logger.exception(e)
                raise JudgeClientError("failed to clean runtime dir")

# 백엔드 서버와 통신하게 될 저지 서버 본체
class JudgeServer:
    # 클래스 메소드 지정, 클래스 자체를 객체로 보고 인자로 전달.
    # 객체를 따로 선언할 필요 없이 함수를 바로 호출할 수 있도록 하기 위함.
    @classmethod
    def ping(cls):
        # 백엔드 서버와 통신 확인
        data = server_info()
        data["action"] = "pong"
        return data

    # 통신에 필요한 저지 함수 정의
    @classmethod
    def judge(cls, language_config, src, max_cpu_time, max_memory, test_case_id=None, test_case=None,
              spj_version=None, spj_config=None, spj_compile_config=None, spj_src=None, output=False,
              io_mode=None):
        if not io_mode:
            io_mode = {"io_mode": ProblemIOMode.standard}

        if not (test_case or test_case_id) or (test_case and test_case_id):
            raise JudgeClientError("invalid parameter")
        # init (초기화 작업)
        # 컴파일 설정, 실행 설정을 받아온다.
        compile_config = language_config.get("compile")
        run_config = language_config["run"]
        # 제출 id는 uuid 모듈을 통해 최대한 중복이 발생하지 않는 id로 지정
        submission_id = uuid.uuid4().hex

        # 스페셜 저지에 필요한 버전과 설정 지정.
        is_spj = spj_version and spj_config

        # 스페셜 저지의 컴파일 버전, 설정이 올바르게 되어있다면 실행 경로 지정.
        if is_spj:
            spj_exe_path = os.path.join(SPJ_EXE_DIR, spj_config["exe_name"].format(spj_version=spj_version))
            # spj src has not been compiled
            # 스페셜 저지 소스가 아직 컴파일되지 않았다면, 재 컴파일 시도.
            if not os.path.isfile(spj_exe_path):
                logger.warning("%s does not exists, spj src will be recompiled")
                cls.compile_spj(spj_version=spj_version, src=spj_src,
                                spj_compile_config=spj_compile_config)

        init_test_case_dir = bool(test_case)
        # 제출 환경 초기화에 필요한 객체들을 dir로 지정 후 경로 설정
        with InitSubmissionEnv(JUDGER_WORKSPACE_BASE, submission_id=str(submission_id), init_test_case_dir=init_test_case_dir) as dirs:
            submission_dir, test_case_dir = dirs
            test_case_dir = test_case_dir or os.path.join(TEST_CASE_DIR, test_case_id)

            # 컴파일 설정이 올바르게 되었다면 (컴파일이 필요)
            if compile_config:
                # 컴파일 소스 경로를 지정,
                src_path = os.path.join(submission_dir, compile_config["src_name"])

                # write source code into file
                # 파일에 소스 코드를 write,
                with open(src_path, "w", encoding="utf-8") as f:
                    f.write(src)
                os.chown(src_path, COMPILER_USER_UID, 0)
                os.chmod(src_path, 0o400)

                # compile source code, return exe file path
                # 해당 소스코드가 들어있는 파일을 컴파일 후 exe파일이 생성된 경로를 return.
                exe_path = Compiler().compile(compile_config=compile_config,
                                              src_path=src_path,
                                              output_dir=submission_dir)
                try:
                    # Java exe_path is SOME_PATH/Main, but the real path is SOME_PATH/Main.class
                    # We ignore it temporarily
                    # 컴파일링이 마쳐졌다면 실행하는 사용자 ID에 exe파일 경로의 권한 설정
                    os.chown(exe_path, RUN_USER_UID, 0)
                    os.chmod(exe_path, 0o500)
                except Exception:
                    pass
            # 컴파일 설정이 올바르게 되어있지 않았다면 (컴파일이 필요 X)
            else:
                # exe파일이 생성된 경로 지정 후 파일에 소스 코드 write.
                exe_path = os.path.join(submission_dir, run_config["exe_name"])
                with open(exe_path, "w", encoding="utf-8") as f:
                    f.write(src)

            # 테스트 케이스 경로가 존재한다면 (bool(test_case)의 return이 True)
            # 즉, 제출물의 저지를 위한 test_case의 경로가 제대로 지정이 되었다면
            if init_test_case_dir:
                # 테스트 케이스 정보를 json으로 지정,
                info = {"test_case_number": len(test_case), "spj": is_spj, "test_cases": {}}
                # write test case
                # 해당 제출물이 올바른지 확인을 위한 테스트 케이스 작성.
                for index, item in enumerate(test_case):
                    index += 1
                    item_info = {}
                    
                    # 테스트 케이스의 이름 및 데이터 형식, 정보 지정
                    input_name = str(index) + ".in"
                    item_info["input_name"] = input_name
                    input_data = item["input"].encode("utf-8")
                    item_info["input_size"] = len(input_data)

                    with open(os.path.join(test_case_dir, input_name), "wb") as f:
                        f.write(input_data)
                    
                    # ???
                    # 만일 스페셜 저지가 필요하지 않은 케이스라면,
                    # 출력 결과의 정보를 바로 지정, 출력물을 파일로 write.
                    if not is_spj:
                        output_name = str(index) + ".out"
                        item_info["output_name"] = output_name
                        output_data = item["output"].encode("utf-8")
                        item_info["output_md5"] = hashlib.md5(output_data).hexdigest()
                        item_info["output_size"] = len(output_data)
                        item_info["stripped_output_md5"] = hashlib.md5(output_data.rstrip()).hexdigest()

                        with open(os.path.join(test_case_dir, output_name), "wb") as f:
                            f.write(output_data)
                    # 작성된 테스트 케이스 목록 저장.      
                    info["test_cases"][index] = item_info

                # 작성된 테스트 케이스들은 테스트 케이스 경로에 파일로 저장
                with open(os.path.join(test_case_dir, "info"), "w") as f:
                    json.dump(info, f)

            # 테스트 케이스까지 작성이 완료되었다면 요청된 클라이언트의 저지 환경 설정 후
            judge_client = JudgeClient(run_config=language_config["run"],
                                       exe_path=exe_path,
                                       max_cpu_time=max_cpu_time,
                                       max_memory=max_memory,
                                       test_case_dir=test_case_dir,
                                       submission_dir=submission_dir,
                                       spj_version=spj_version,
                                       spj_config=spj_config,
                                       output=output,
                                       io_mode=io_mode)

            # Judger를 실행시킨 결과 저장, 그 결과를 return.
            run_result = judge_client.run()
            return run_result

    # 스페셜 저지 컴파일 설정 (?)
    @classmethod
    def compile_spj(cls, spj_version, src, spj_compile_config):
        # 스페셜 저지의 컴파일 설정 (소스 이름, 실행파일 이름) 지정 후 소스 파일 경로 지정.
        spj_compile_config["src_name"] = spj_compile_config["src_name"].format(spj_version=spj_version)
        spj_compile_config["exe_name"] = spj_compile_config["exe_name"].format(spj_version=spj_version)
        spj_src_path = os.path.join(SPJ_SRC_DIR, spj_compile_config["src_name"])

        # if spj source code not found, then write it into file
        # 스페셜 저지 소스 코드가 존재하지 않는다면, 파일로 작성한 후 컴파일 하는 사용자 ID에 경로 권한 설정
        if not os.path.exists(spj_src_path):
            with open(spj_src_path, "w", encoding="utf-8") as f:
                f.write(src)
            os.chown(spj_src_path, COMPILER_USER_UID, 0)
            os.chmod(spj_src_path, 0o400)

        try:
            # 경로 권한 설정 후 컴파일 수행, 기존 저지와 동일하지만 소스 경로에 스페셜 저지의 경로 지정.
            # 해당 소스코드가 들어있는 파일을 컴파일 후 exe파일이 생성된 경로를 return.
            exe_path = Compiler().compile(compile_config=spj_compile_config,
                                          src_path=spj_src_path,
                                          output_dir=SPJ_EXE_DIR)
            os.chown(exe_path, SPJ_USER_UID, 0)
            os.chmod(exe_path, 0o500)

        # turn common CompileError into SPJCompileError
        # 스페셜 저지에서 발생한 에러는 단순 컴파일 에러가 아닌 SPJ컴파일 에러임을 알림.
        except CompileError as e:
            raise SPJCompileError(e.message)
        # 저지가 성공적으로 마쳐졌다면 성공한 사실을 return.
        return "success"

# flask 객체의 route()를 통해 어떤 URL이 이 애플리케이션 (즉, 함수들)을 실행시키는지 알 수 있도록 함.
# 즉, 백엔드 서버와 통신을 통해 백엔드 서버가 위 함수들을 실행하고 백엔드 서버 DB의 내용 변경을 위해 POST method로 연결.
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=["POST"])
# 연결을 위한 서버 객체 정의
def server(path):
    if path in ("judge", "ping", "compile_spj"):
        # 연결 전 헤더 정보를 받아와 토큰으로 기록
        _token = request.headers.get("X-Judge-Server-Token")
        try:
            # 토큰이 일치하지 않으면 에러, 임시로 주석처리해놓음. 
            if 1!=1: #if _token != token:
                raise TokenVerificationFailed("invalid token")
            # 데이터는 json형식으로 요청
            try:
                data = request.json
            except Exception:
                data = {}
            ret = {"err": None, "data": getattr(JudgeServer, path)(**data)}
        # 에러 핸들링
        except (CompileError, TokenVerificationFailed, SPJCompileError, JudgeClientError) as e:
            logger.exception(e)
            ret = {"err": e.__class__.__name__, "data": e.message}
        except Exception as e:
            logger.exception(e)
            ret = {"err": "JudgeClientError", "data": e.__class__.__name__ + " :" + str(e)}
    else:
        ret = {"err": "InvalidRequest", "data": "404"}
    return Response(json.dumps(ret), mimetype='application/json')


if DEBUG:
    logger.info("DEBUG=ON")

# gunicorn -w 4 -b 0.0.0.0:8080 server:app
# 윈도우 환경에선 fcntl 모듈 에러 발생.

if __name__ == "__main__":
    app.run(debug=DEBUG, use_reloader=False)