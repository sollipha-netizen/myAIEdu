"""과정과 8주 커리큘럼 초기 데이터를 입력합니다. 여러 번 실행해도 중복되지 않습니다.

실행: cd backend 후 py -3 scripts/seed_curriculum.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.database import SessionLocal, init_db  # noqa: E402
from app.models.course import Course, Week  # noqa: E402

COURSE = dict(
    id=1,
    title="4050 AI 실전 입문",
    description="퇴근 후 30분, AI를 내 일의 도구로 바꾸는 40·50대 입문 과정",
    price=None,      # [확인 필요] 수강료. None이면 프론트에서 "추후 안내"로 표시
    capacity=20,     # [확인 필요] 정원
    is_open=True,
)

PRACTICE_RESUME = {
    "title": "AI로 이력서·자기소개서 다듬기",
    "steps": [
        "내 경력(업무, 성과, 자격증)을 날것 그대로 적고, 채용 담당자가 읽기 좋은 항목으로 정리해 달라고 요청합니다.",
        "지원 공고 문장을 넣고, 강조할 역량 3가지를 뽑아 내 경력과 연결한 뒤 직접 고칩니다.",
        "300자 분량 자기소개서 초안을 만들고, 사실과 다른 부분은 본인 표현으로 고쳐 최종본을 완성합니다.",
    ],
}


def week(no: int, title: str, goal: str, practice: dict | None = None) -> dict:
    return dict(
        week_no=no,
        title=title,
        goal=goal,
        practice_title=practice["title"] if practice else None,
        practice_steps=practice["steps"] if practice else None,
    )


WEEKS = [  # [확인 필요] 1~7주 학습 목표는 임시 문장입니다
    week(1, "AI 기초 개념과 생성형 AI 소개", "AI가 무엇인지 이해하고 생성형 AI 도구에 처음 접속해 봅니다."),
    week(2, "질문하는 법 (프롬프트 기초)", "원하는 답을 얻도록 질문을 구체적으로 쓰는 방법을 익힙니다."),
    week(3, "업무 문서 작성과 정리 (1)", "보고서나 안내문 초안을 AI와 함께 작성합니다."),
    week(4, "업무 문서 작성과 정리 (2)", "작성한 문서를 다듬고 목적에 맞게 요약합니다."),
    week(5, "데이터와 일정 관리 활용 (1)", "표 형태의 정보를 AI에게 정리하도록 요청합니다."),
    week(6, "데이터와 일정 관리 활용 (2)", "일정과 할 일을 AI와 함께 계획합니다."),
    week(7, "나만의 AI 활용 루틴 만들기", "매일 쓸 수 있는 나만의 AI 활용 방법을 정리합니다."),
    week(8, "마무리: 이력서·자기소개서 다듬기", "AI를 활용해 실제 지원용 문서를 완성합니다.", PRACTICE_RESUME),
]


def main() -> None:
    init_db()
    with SessionLocal() as db:
        if db.get(Course, COURSE["id"]) is not None:
            print("이미 입력된 과정입니다. 건너뜁니다.")
            return
        db.add(Course(**COURSE, weeks=[Week(**w) for w in WEEKS]))
        db.commit()
        print(f"과정 1개와 {len(WEEKS)}주차 커리큘럼을 입력했습니다.")


if __name__ == "__main__":
    main()
