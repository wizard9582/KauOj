from django.db import models

from utils.constants import ContestStatus   # 대회 시작, 종료 Flag 사용을 위해 import
from utils.models import JSONField 
from problem.models import Problem # 문제 정보 사용을 위해 import
from contest.models import Contest # 대회 객체 사용을 위해 import 

from utils.shortcuts import rand_str

# 채점 상태 확인 Flag
class JudgeStatus:
    COMPILE_ERROR = -2
    WRONG_ANSWER = -1
    ACCEPTED = 0
    CPU_TIME_LIMIT_EXCEEDED = 1
    REAL_TIME_LIMIT_EXCEEDED = 2
    MEMORY_LIMIT_EXCEEDED = 3
    RUNTIME_ERROR = 4
    SYSTEM_ERROR = 5
    PENDING = 6
    JUDGING = 7
    PARTIALLY_ACCEPTED = 8


class Submission(models.Model):
    # DB 저장을 위한 구조 정의
    id = models.TextField(default=rand_str, primary_key=True, db_index=True)
    contest = models.ForeignKey(Contest, null=True, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_now_add=True)
    user_id = models.IntegerField(db_index=True)
    username = models.TextField()
    code = models.TextField()
    result = models.IntegerField(db_index=True, default=JudgeStatus.PENDING)
    # JudgeServer에서 반환 된 채점 세부 정보
    info = JSONField(default=dict)
    language = models.TextField()
    shared = models.BooleanField(default=False)
    # 제출 목록 표시를 보기 좋게하기 위해 제출 시간 및 메모리 값을 저장
    # {time_cost: "", memory_cost: "", err_info: "", score: 0}
    statistic_info = JSONField(default=dict)
    ip = models.TextField(null=True)

    # 사용자 권한 확인
    def check_user_permission(self, user, check_share=True):
        # Super 사용자 or 문제 제출자 본인 or 동일 사용자 or 모든 문제에 권한 있는 사용자
        if self.user_id == user.id or user.is_super_admin() or user.can_mgmt_all_problem() or self.problem.created_by_id == user.id:
            return True

        # 공유 유무
        if check_share: 
            if self.contest and self.contest.status != ContestStatus.CONTEST_ENDED:
                return False
            if self.problem.share_submission or self.shared:
                return True
        return False

    class Meta:
        db_table = "submission"
        ordering = ("-create_time",)

    def __str__(self):
        return self.id
