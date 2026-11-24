"""8주차 예시: 경험 자산으로 비즈니스용 AI 질문을 만들고, 첫 달 수익을 계산한다.

질문 만들기와 수익 계산을 한 파일에 둔 이유는 수강생이 파일 하나만 열고
실습 2~5단계를 따라가게 하기 위함이다.
"""

import math
from dataclasses import dataclass

IDEA_COUNT = 3
INTERVIEW_QUESTION_COUNT = 5
ROLE = "당신은 40·50대 직장인의 경험을 작은 서비스로 바꾸도록 돕는 창업 코치입니다."
# 수강생이 회사 자료를 넣거나 AI가 과장 문구를 쓰는 일을 막기 위한 공통 조건이다.
SAFETY_RULE = "보장하거나 확인할 수 없는 표현은 쓰지 말고, 퇴근 후 시간으로 할 수 있는 규모로 제안하세요."


@dataclass
class BusinessIdea:
    """실습 1·2단계에서 적는 재료. 7주차 한 줄 소개가 출발점이다."""

    one_liner: str
    assets: list[str]
    customer: str
    problem: str


@dataclass
class MonthlyPlan:
    """첫 달 수익 계산에 쓰는 값. 단위는 모두 원, 고객 수는 명이다."""

    price: int
    customers_per_month: int
    cost_per_customer: int
    fixed_cost: int


def build_prompts(idea: BusinessIdea) -> dict[str, str]:
    """실습에서 쓰는 질문 세 개를 만든다. 모든 질문에 같은 재료와 조건을 붙인다."""
    facts = "\n".join([
        f"- 나의 한 줄 소개: {idea.one_liner}",
        f"- 경험 자산: {', '.join(idea.assets)}",
        f"- 고객: {idea.customer}",
        f"- 고객의 문제: {idea.problem}",
    ])
    tasks = {
        "[1] 아이디어 발산": f"작은 서비스 아이디어 {IDEA_COUNT}개를 서비스 형태, 1회 가격 범위, 준비 기간과 함께 표로 주세요.",
        "[2] 고객 검증 질문": f"이 고객에게 물을 인터뷰 질문 {INTERVIEW_QUESTION_COUNT}개를 주세요. 유도 질문은 빼 주세요.",
        "[3] 소개 페이지 문구": "서비스 이름 후보 3개, 대상, 해결하는 문제, 제공 내용 3가지를 짧은 문구로 주세요.",
    }
    return {title: f"{ROLE}\n{facts}\n요청: {task}\n조건: {SAFETY_RULE}" for title, task in tasks.items()}


def estimate_month(plan: MonthlyPlan) -> dict[str, int]:
    """첫 달 매출, 비용, 수익, 손익분기 고객 수를 계산한다.

    1명당 남는 돈이 0 이하이면 고객을 늘려도 손해이므로 계산하지 않고 오류를 낸다.
    """
    if min(plan.price, plan.customers_per_month, plan.cost_per_customer, plan.fixed_cost) < 0:
        raise ValueError("가격, 고객 수, 비용에는 음수를 넣을 수 없습니다.")
    margin = plan.price - plan.cost_per_customer
    if margin <= 0:
        raise ValueError("가격이 고객 1명당 비용보다 높아야 합니다.")
    revenue = plan.price * plan.customers_per_month
    cost = plan.cost_per_customer * plan.customers_per_month + plan.fixed_cost
    return {
        "매출": revenue,
        "비용": cost,
        "수익": revenue - cost,
        "손익분기 고객 수": math.ceil(plan.fixed_cost / margin),
    }


# 수강생이 바꿔 쓰는 가상의 예시 값이다. 실제 시장 가격이 아니다.
SAMPLE_IDEA = BusinessIdea(
    one_liner="소규모 공장의 첫 품질 인증을 돕는 품질관리 22년 경력자",
    assets=["인증 서류 점검표", "현장 점검 순서", "심사 때 자주 받는 질문 목록"],
    customer="직원 30명 이하 소규모 공장 대표",
    problem="첫 품질 인증 심사에 무슨 서류가 필요한지 모른다",
)
SAMPLE_PLAN = MonthlyPlan(price=50_000, customers_per_month=6, cost_per_customer=5_000, fixed_cost=30_000)

if __name__ == "__main__":
    for title, prompt in build_prompts(SAMPLE_IDEA).items():
        print(f"{title}\n{prompt}\n")
    print("[첫 달 수익 계산]")
    for label, amount in estimate_month(SAMPLE_PLAN).items():
        unit = "명" if label == "손익분기 고객 수" else "원"
        print(f"- {label}: {amount:,}{unit}")
