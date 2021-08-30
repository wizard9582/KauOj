# 서버 연결 예외처리 : 에러 메시지 출력
class JudgeServerException(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message

# 기타 발생할 수 있는 에러에 대해선 코드 실행 X
class TokenVerificationFailed(JudgeServerException):
    pass


class JudgeClientError(JudgeServerException):
    pass


class JudgeServiceError(JudgeServerException):
    pass


class CompileError(JudgeServerException):
    pass


class SPJCompileError(JudgeServerException):
    pass