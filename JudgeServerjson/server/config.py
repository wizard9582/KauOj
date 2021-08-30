"""
MIT Open Source License - HUST OJ (https://github.com/hustoj) 참고
중국 화중과학기술대학교의 전 ACM 팀원들이 개발한 오픈 소스 프로젝트
"""

import os # read, write 등의 OS 관련 기능을 사용하기 위한 모듈
import pwd # 암호화 된 DB에 접근하기 위한 모듈
import grp # 그룹 DB에 접근하기 위한 모듈
import sys
sys.path.append('/home/chris/OJ/JudgeServer-master/log') 

JUDGER_WORKSPACE_BASE = "/judger/run" # Judger의 Workspace 지정
LOG_BASE = "/log" # Judger의 활동 로그 기록소 지정

COMPILER_LOG_PATH = os.path.join(LOG_BASE, "compile.log") # 컴파일 로그 지정
JUDGER_RUN_LOG_PATH = os.path.join(LOG_BASE, "judger.log") # Judger 실행 로그 지정
SERVER_LOG_PATH = os.path.join(LOG_BASE, "judge_server.log") # 서버 통신 로그 지정

RUN_USER_UID = pwd.getpwnam("code").pw_uid 
RUN_GROUP_GID = grp.getgrnam("code").gr_gid
COMPILER_USER_UID = pwd.getpwnam("compiler").pw_uid 
COMPILER_GROUP_GID = grp.getgrnam("compiler").gr_gid 
SPJ_USER_UID = pwd.getpwnam("spj").pw_uid 
SPJ_GROUP_GID = grp.getgrnam("spj").gr_gid 

TEST_CASE_DIR = "/test_case"
SPJ_SRC_DIR = "/judger/spj"
SPJ_EXE_DIR = "/judger/spj"
