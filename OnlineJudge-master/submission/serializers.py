from .models import Submission

# REST Framework의 Serializer를 우리의 APP에 사용하기 편리하도록 재구성한 함수 사용을 위해 import
from utils.api import serializers 
from utils.serializers import LanguageNameChoiceField

"""
제출한 답안(데이터)은 그 자체론 컴파일링 및 처리가 어려우므로,
JSON 형식으로 변환하는 Serializer를 이용해 FE-BE, BE-JudgeBE간 데이터의 통신을 지원,
아래의 Serializer들을 통해 BE-JudgeBE간 JSON 형식으로 통신.
"""

# 작성한 답안의 전송을 위한 Serializer
class CreateSubmissionSerializer(serializers.Serializer):
    problem_id = serializers.IntegerField()
    language = LanguageNameChoiceField()
    code = serializers.CharField(max_length=1024 * 1024)
    contest_id = serializers.IntegerField(required=False)
    captcha = serializers.CharField(required=False)

# 공유된 답안의 전송을 위한 Serializer
class ShareSubmissionSerializer(serializers.Serializer):
    id = serializers.CharField()
    shared = serializers.BooleanField()

# ACM rule_type에 사용되는 submission info 용 Serializer
class SubmissionSafeModelSerializer(serializers.ModelSerializer):
    problem = serializers.SlugRelatedField(read_only=True, slug_field="_id")

    class Meta:
        model = Submission
        exclude = ("info", "contest", "ip")

# 제출 리스트 정보 전송을 위한 Serializer
class SubmissionListSerializer(serializers.ModelSerializer):
    problem = serializers.SlugRelatedField(read_only=True, slug_field="_id")
    show_link = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = Submission
        exclude = ("info", "contest", "code", "ip")

    # 권한이 있는 사용자인지, 익명의 사용자인지 판단
    # 권한이 있는 사용자라면 link를 전송
    def get_show_link(self, obj):
        if self.user is None or not self.user.is_authenticated:
            return False
        return obj.check_user_permission(self.user)

        
class SubmissionModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Submission
        fields = "__all__"

