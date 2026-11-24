"""7주차 예시: 경력 재료를 넣으면 퍼스널 브랜딩용 AI 질문(프롬프트)을 만들어 준다.

AI 서비스를 직접 호출하지 않는다. 수강생마다 쓰는 AI가 다르고 API 키 발급이
입문자에게 장벽이 되므로, 만든 질문을 대화창에 붙여 넣는 방식을 택했다.
"""

from dataclasses import dataclass

# 분량 기준을 한 곳에 둔다. 실습 가이드의 완료 기준과 같은 값이어야 한다.
ONE_LINER_MAX_CHARS = 40
ONE_LINER_COUNT = 3
SNS_MAX_CHARS = 150

# 모든 질문에 공통으로 붙는 역할과 검수 조건이다.
# AI가 없는 성과를 지어내는 일이 잦아서 "적은 사실만 쓰라"는 조건을 항상 넣는다.
ROLE = "당신은 40·50대 직장인의 경력 전환을 돕는 코치입니다."
HONESTY_RULE = "제가 적지 않은 성과나 숫자는 절대 넣지 말고, 과장 표현은 쓰지 마세요."


@dataclass
class CareerProfile:
    """1단계 경력 재료 정리표 한 장. 모든 값은 수강생이 직접 적은 사실이다."""

    career: str
    achievements: list[str]
    strength: str
    audience: str
    tone: str


def format_facts(profile: CareerProfile) -> str:
    """질문 본문에 들어갈 사실 목록을 만든다. 세 질문이 같은 재료를 쓰도록 한 곳에서 만든다."""
    achievements = ", ".join(profile.achievements) if profile.achievements else "없음"
    return "\n".join([
        f"- 경력: {profile.career}",
        f"- 성과: {achievements}",
        f"- 강점: {profile.strength}",
        f"- 돕고 싶은 사람: {profile.audience}",
    ])


def build_prompt(profile: CareerProfile, task: str) -> str:
    """역할, 사실, 요청, 조건 순서로 질문을 조립한다. 2주차에서 배운 4요소 순서다."""
    return "\n".join([
        ROLE,
        "아래 사실만 사용해 주세요.",
        format_facts(profile),
        f"요청: {task}",
        f"조건: 말투는 '{profile.tone}'. {HONESTY_RULE}",
    ])


def build_all_prompts(profile: CareerProfile) -> dict[str, str]:
    """실습 2·3단계에서 쓰는 질문 세 개를 순서대로 돌려준다. 키는 화면에 보일 제목이다."""
    tasks = {
        "[1] 한 줄 소개": f"한 줄 소개를 {ONE_LINER_COUNT}개 만들어 주세요. 각각 {ONE_LINER_MAX_CHARS}자 이내입니다.",
        "[2] 3줄 프로필": "강의 소개나 제안서에 쓸 3줄 프로필을 만들어 주세요.",
        "[3] SNS 소개글": f"블로그와 링크드인에 쓸 소개글을 {SNS_MAX_CHARS}자 이내로 만들어 주세요.",
    }
    return {title: build_prompt(profile, task) for title, task in tasks.items()}


# 수강생이 자기 내용으로 바꿔 쓰는 예시 값이다. 실존 인물이 아닌 가상의 경력이다.
SAMPLE_PROFILE = CareerProfile(
    career="제조 현장 품질관리 22년",
    achievements=["불량률 3.2%에서 0.8%로 개선", "품질 인증 심사 5회 통과"],
    strength="불량 원인을 빨리 찾는다",
    audience="품질 인증을 처음 준비하는 소규모 공장",
    tone="믿음직하고 차분하게",
)

if __name__ == "__main__":
    for title, prompt in build_all_prompts(SAMPLE_PROFILE).items():
        print(f"{title}\n{prompt}\n")
