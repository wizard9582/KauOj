import os
import sys
# sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append('/mnt/c/Users/skdbs/Desktop/OJ/Judger-newnew/bindings/Python')
import _judger # 저지 서버에서 사용할 Judger (Compiler) 본체 모듈 
import hashlib # 암호화 보안을 위한 모듈
import json
import shutil # 파일의 복사, 삭제 연산을 위한 모듈

"""
멀티 프로세싱을 위한 모듈. 
복잡하고 시간이 걸리는 작업을 프로세스를 이용, 병렬로 처리해 속도 개선
모듈 안의 Pool 객체는 함수 실행을 병렬 처리, 입력 데이터를 프로세스에 분산시키는 것을 지원.
https://docs.python.org/ko/3/library/multiprocessing.html
"""
from multiprocessing import Pool

# 시스템 모니터링, 프로세스 관리를 위한 모듈.
# https://npd-58.tistory.com/27
# https://psutil.readthedocs.io/en/latest/
import psutil

"""
TEST_CASE_DIR : 테스트 경로 지정
JUDGER_RUN_LOG_PATH : Judger 실행 로그 지정
RUN_GROUP_GID : 그룹 DB 기록 지정
RUN_USER_UID : 해당 사용자 ID 기록 지정
SPJ_EXE_DIR : 컴파일러 실행 결과 경로 지정
SPJ_GROUP_GID : 컴파일러가 처리한 그룹 ID 지정
"""
from config import TEST_CASE_DIR, JUDGER_RUN_LOG_PATH, RUN_GROUP_GID, RUN_USER_UID, SPJ_EXE_DIR, SPJ_USER_UID, SPJ_GROUP_GID, RUN_GROUP_GID
from exception import JudgeClientError
from utils import ProblemIOMode # 입력받은 문제의 처리 형식 지정 (표준 or 파일)
import sys
sys.path.append('/home/chris/OJ/JudgeServer-master/log') 

SPJ_WA = 1
SPJ_AC = 0
SPJ_ERROR = -1

# 다른 모듈에서 import되면 안될 함수는 underscore를 통해 준 private으로 지정. 
# underscore가 붙은 함수들은 테스팅을 위해 사용.

# 테스팅 확인
# 테스팅 결과를 토대로 실제 run수행을 위해 함수 지정 및 class 내 run과 구분을 위해 underscore 지정
def _run(instance, test_case_file_id):
    return instance._judge_one(test_case_file_id)


class JudgeClient(object):
    # 컴파일링 할 Judger 초기화
    def __init__(self, run_config, exe_path, max_cpu_time, max_memory, test_case_dir,
                 submission_dir, spj_version, spj_config, io_mode, output=False):
        # 각종 경로 및 환경변수 지정
        self._run_config = run_config
        self._exe_path = exe_path
        self._max_cpu_time = max_cpu_time
        self._max_memory = max_memory
        self._max_real_time = self._max_cpu_time * 3
        self._test_case_dir = test_case_dir
        self._submission_dir = submission_dir

        # 현재 프로세스 풀은 실행되고 있는 CPU의 논리 프로세서 수. 개수는 물리적 코어 x2.
        # 즉, 물리적 코어의 수 x2 만큼의 프로세스를 생성.
        self._pool = Pool(processes=psutil.cpu_count())
        self._test_case_info = self._load_test_case_info()

        # 컴파일러 버전, 설정, 출력물, 처리형식 지정
        self._spj_version = spj_version
        self._spj_config = spj_config
        self._output = output
        self._io_mode = io_mode

        # 컴파일러 버전과 설정이 올바르게 되어있으면 
        if self._spj_version and self._spj_config:
            # 컴파일러 실행 경로는 exe파일 경로로 지정
            self._spj_exe = os.path.join(SPJ_EXE_DIR,
                                         self._spj_config["exe_name"].format(spj_version=self._spj_version))
            # 설정이 올바르지 않으면 에러 반환.
            if not os.path.exists(self._spj_exe):
                raise JudgeClientError("spj exe not found")

    # 테스트 정보 로드
    def _load_test_case_info(self):
        try:
            with open(os.path.join(self._test_case_dir, "info")) as f:
                return json.load(f)
        # 테스트 파일이 없는 경우
        except IOError:
            raise JudgeClientError("Test case not found")
        # 테스트 설정이 잘못된 경우
        except ValueError:
            raise JudgeClientError("Bad test case config")

    # 테스팅 파일 정보 로드 (여기까지)
    def _get_test_case_file_info(self, test_case_file_id):
        return self._test_case_info["test_cases"][test_case_file_id]


    # 사용자 출력 파일과 테스트 출력 파일을 비교
    def _compare_output(self, test_case_file_id, user_output_file):
        with open(user_output_file, "rb") as f:
            content = f.read()
        # 출력물을 암호화
        output_md5 = hashlib.md5(content.rstrip()).hexdigest()
        result = output_md5 == self._get_test_case_file_info(test_case_file_id)["stripped_output_md5"]
        return output_md5, result

    # 스페셜 저지 (답안이 여러개 나올 수 있는 경우)의 컴파일 환경 설정
    def _spj(self, in_file_path, user_out_file_path):
        # 컴파일러가 맡을 제출파일, 결과 파일의 경로 권한 지정
        os.chown(self._submission_dir, SPJ_USER_UID, 0)
        os.chown(user_out_file_path, SPJ_USER_UID, 0)
        os.chmod(user_out_file_path, 0o740)
        command = self._spj_config["command"].format(exe_path=self._spj_exe,
                                                     in_file_path=in_file_path,
                                                     user_out_file_path=user_out_file_path).split(" ")
        seccomp_rule_name = self._spj_config["seccomp_rule"]
        # 권한 설정을 마쳤다면 Judger를 실행시킨 결과를 저장
        result = _judger.run(max_cpu_time=self._max_cpu_time * 3,
                             max_real_time=self._max_cpu_time * 9,
                             max_memory=self._max_memory * 3,
                             max_stack=128 * 1024 * 1024,
                             max_output_size=1024 * 1024 * 1024,
                             max_process_number=_judger.UNLIMITED,
                             exe_path=command[0],
                             input_path=in_file_path,
                             output_path="/tmp/spj.out",
                             error_path="/tmp/spj.out",
                             args=command[1::],
                             env=["PATH=" + os.environ.get("PATH", "")],
                             log_path=JUDGER_RUN_LOG_PATH,
                             seccomp_rule_name=seccomp_rule_name,
                             uid=SPJ_USER_UID,
                             gid=SPJ_GROUP_GID)

        # 컴파일이 일단 제대로 수행되면 (RESULT_SUCCESS || RESULT_RUNTIME_ERROR || SPJ_WA, SPJ_ERROR) 코드 종료
        if result["result"] == _judger.RESULT_SUCCESS or \
                (result["result"] == _judger.RESULT_RUNTIME_ERROR and
                 result["exit_code"] in [SPJ_WA, SPJ_ERROR] and result["signal"] == 0):
            return result["exit_code"]
        # 컴파일이 제대로 수행되지 않았다면 에러 반환
        else:
            return SPJ_ERROR

    # 한 문제를 Judge
    def _judge_one(self, test_case_file_id):
        # 입력으로 넣을 파일 경로와 파일 정보 지정
        test_case_info = self._get_test_case_file_info(test_case_file_id)
        in_file = os.path.join(self._test_case_dir, test_case_info["input_name"])

        # 현재 컴파일 프로그램이 컴파일 수행이 아니라 파일을 기다리고 있는 상태이면
        if self._io_mode["io_mode"] == ProblemIOMode.file:
            # 제출 경로를 결과 출력 경로로 지정, 시스템 실행 환경을 해당 경로로 변경
            user_output_dir = os.path.join(self._submission_dir, str(test_case_file_id))
            os.mkdir(user_output_dir)
            os.chown(user_output_dir, RUN_USER_UID, RUN_GROUP_GID)
            os.chmod(user_output_dir, 0o711)
            os.chdir(user_output_dir)
            # todo check permission (권한 확인 필요?)
            # 사용자 출력 파일은 지정한 경로에 저장
            # 입력파일 또한 복사 후 지정한 경로에 저장
            # 저장한 파일 명들을 통신을 위해 JSON 형식으로 지정
            user_output_file = os.path.join(user_output_dir, self._io_mode["output"])
            real_user_output_file = os.path.join(user_output_dir, "stdio.txt")
            shutil.copyfile(in_file, os.path.join(user_output_dir, self._io_mode["input"]))
            kwargs = {"input_path": in_file, "output_path": real_user_output_file, "error_path": real_user_output_file}
        # 파일이 이미 올려져있는 상태라면, 사용자 출력 파일을 해당 경로에 저장
        # 마찬가지로 통신을 위해 JSON형식으로 지정
        else:
            real_user_output_file = user_output_file = os.path.join(self._submission_dir, test_case_file_id + ".out")
            kwargs = {"input_path": in_file, "output_path": real_user_output_file, "error_path": real_user_output_file}
        # 명령 형식, 환경변수 경로 지정
        command = self._run_config["command"].format(exe_path=self._exe_path, exe_dir=os.path.dirname(self._exe_path),
                                                     max_memory=int(self._max_memory / 1024)).split(" ")
        env = ["PATH=" + os.environ.get("PATH", "")] + self._run_config.get("env", [])

        seccomp_rule = self._run_config["seccomp_rule"]

        # seccomp_rule이 닥셔너리 자료형이라면 io 모드로 전환
        if isinstance(seccomp_rule, dict):
            seccomp_rule = seccomp_rule[self._io_mode["io_mode"]]

        # 경로 설정, 명령형식, 모드전환 등의 작업을  마쳤으면 Judger를 실행시킨 결과를 저장
        run_result = _judger.run(max_cpu_time=self._max_cpu_time,
                                 max_real_time=self._max_real_time,
                                 max_memory=self._max_memory,
                                 max_stack=128 * 1024 * 1024,
                                 max_output_size=max(test_case_info.get("output_size", 0) * 2, 1024 * 1024 * 16),
                                 max_process_number=_judger.UNLIMITED,
                                 exe_path=command[0],
                                 args=command[1::],
                                 env=env,
                                 log_path=JUDGER_RUN_LOG_PATH,
                                 seccomp_rule_name=seccomp_rule,
                                 uid=RUN_USER_UID,
                                 gid=RUN_GROUP_GID,
                                 memory_limit_check_only=self._run_config.get("memory_limit_check_only", 0),
                                 **kwargs)
        run_result["test_case"] = test_case_file_id

        # if progress exited normally, then we should check output result
        # 진행이 정상적으로 종료되었으면 출력 결과를 확인
        run_result["output_md5"] = None
        run_result["output"] = None
        # 컴파일이 결과가 제대로 생성되었는지 확인
        if run_result["result"] == _judger.RESULT_SUCCESS:
            # 만약 현재 지정된 경로에 사용자 출력 파일이 없으면 에러.
            if not os.path.exists(user_output_file):
                run_result["result"] = _judger.RESULT_WRONG_ANSWER
            # 지정된 경로에 출력 파일이 정상적으로 있다면
            else:
                # spj 정보를 받아와서
                if self._test_case_info.get("spj"):
                    # spj 버전이나 설정이 다르다면 에러 반환,
                    if not self._spj_config or not self._spj_version:
                        raise JudgeClientError("spj_config or spj_version not set")
                    # 올바르게 되어있다면 해당 파일로 컴파일 수행.
                    spj_result = self._spj(in_file_path=in_file, user_out_file_path=user_output_file)

                    # spj 컴파일 결과가 올바르지 않으면 오답
                    if spj_result == SPJ_WA:
                        run_result["result"] = _judger.RESULT_WRONG_ANSWER
                    # spj 컴파일 결과가 SPJ 에러라면 자체 에러.(시스템 에러 or SPJ 컴파일러 에러)
                    elif spj_result == SPJ_ERROR:
                        run_result["result"] = _judger.RESULT_SYSTEM_ERROR
                        run_result["error"] = _judger.ERROR_SPJ_ERROR
                # spj 정보를 받아오지 않는다면 결과물을 비교, 플래그로 판단 (?)
                # 정보를 받아오지 않는다면 출력된 결과물 파일을 비교, 플래그 변수를 통해 저지 결과를 판단
                else:
                    run_result["output_md5"], is_ac = self._compare_output(test_case_file_id, user_output_file)
                    # -1 == Wrong Answer
                    if not is_ac:
                        run_result["result"] = _judger.RESULT_WRONG_ANSWER
        # 컴파일 결과가 제대로 생성되었고 결과 출력물이 있다면 파일을 open.
        if self._output:
            try:
                with open(user_output_file, "rb") as f:
                    run_result["output"] = f.read().decode("utf-8", errors="backslashreplace")
            except Exception:
                pass

        return run_result

    # pool.apply_async : https://docs.python.org/ko/3/library/multiprocessing.html
    # 테스트가 아닌 실제로 실행시킬 run 함수
    # 실행은 multiprocessing - Pool 이용
    def run(self):
        tmp_result = []
        result = []
        # 테스트 케이스 갯수만큼 작업 실행
        for test_case_file_id, _ in self._test_case_info["test_cases"].items():
            # 비동기 식으로 run, 지정한 pool에서 실행된 프로세스의 결과를 얻는다
            tmp_result.append(self._pool.apply_async(_run, (self, test_case_file_id)))
        self._pool.close()
        self._pool.join()

        for item in tmp_result:
            # exception will be raised, when get() is called
            # get()이 호출되면 예외가 발생할 수 있음. 다음 링크 참고.
            # # http://stackoverflow.com/questions/22094852/how-to-catch-exceptions-in-workers-in-multiprocessing
            result.append(item.get())
        return result

    def __getstate__(self):
        # http://stackoverflow.com/questions/25382455/python-notimplementederror-pool-objects-cannot-be-passed-between-processes
        self_dict = self.__dict__.copy()
        del self_dict["_pool"]
        return self_dict
