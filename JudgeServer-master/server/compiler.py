import os
import sys
#sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
#import _judger # 저지 서버에서 사용할 Judger (Compiler) 본체 모듈 
#sys.path.append('C:\\Users\\skdbs\\Desktop\\OJ\\Judger-newnew\\bindings\\Python')

sys.path.append('/mnt/c/Users/dezar/Desktop/OJ/Judger-newnew/bindings/Python') 
import _judger
import json


# 컴파일 로그, 컴파일을 수행하는 사용자의 ID, 그룹 DB에 저장할 컴파일 정보 
from config import COMPILER_LOG_PATH, COMPILER_USER_UID, COMPILER_GROUP_GID
# 컴파일 에러 예외
from exception import CompileError


class Compiler(object):
    def compile(self, compile_config, src_path, output_dir):
        # 컴파일 커맨드, exe 경로 및 컴파일 결과물 경로 지정S
        command = compile_config["compile_command"]
        exe_path = os.path.join(output_dir, compile_config["exe_name"])
        command = command.format(src_path=src_path, exe_dir=output_dir, exe_path=exe_path)
        compiler_out = os.path.join(output_dir, "compiler.out")
        _command = command.split(" ")

        # 결과물을 출력하는 경로로 디렉터리 변경
        os.chdir(output_dir)
        # 컴파일 환경 경로 통합
        env = compile_config.get("env", [])
        env.append("PATH=" + os.getenv("PATH"))
        # 컴파일 결과는 Judger를 이용해 받아온다.
        # Judger/bindings/Python/_judger/__init__.py 실행
        result = _judger.run(max_cpu_time=compile_config["max_cpu_time"],
                             max_real_time=compile_config["max_real_time"],
                             max_memory=compile_config["max_memory"],
                             max_stack=128 * 1024 * 1024,
                             max_output_size=20 * 1024 * 1024,
                             max_process_number=_judger.UNLIMITED,
                             exe_path=_command[0],
                             # /dev/null is best, but in some system, this will call ioctl system call
                             input_path=src_path,
                             output_path=compiler_out,
                             error_path=compiler_out,
                             args=_command[1::],
                             env=env,
                             log_path=COMPILER_LOG_PATH,
                             seccomp_rule_name=None,
                             uid=COMPILER_USER_UID,
                             gid=COMPILER_GROUP_GID)

        # 저지가 성공적으로 종료
        if result["result"] != _judger.RESULT_SUCCESS:
            # 컴파일 결과 출력 경로가 지정되어 있으면
            if os.path.exists(compiler_out):
                # 결과물을 읽고 에러가 있는지 확인
                with open(compiler_out, encoding="utf-8") as f:
                    error = f.read().strip()
                    os.remove(compiler_out)
                    # 에러가 있다면 컴파일 에러 반환
                    if error:
                        raise CompileError(error)
            # 출력 경로가 따로 지정되지 않아있다면 에러 출력
            raise CompileError("Compiler runtime error, info: %s" % json.dumps(result))
        else:
            os.remove(compiler_out)
            return exe_path
