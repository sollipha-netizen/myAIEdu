"""8주차 예시 코드의 수익 계산 규칙과 질문 구성을 확인한다."""

import pytest

from business_canvas import (
    SAFETY_RULE,
    SAMPLE_IDEA,
    SAMPLE_PLAN,
    MonthlyPlan,
    build_prompts,
    estimate_month,
)


def test_sample_plan_numbers_match_the_practice_guide():
    result = estimate_month(SAMPLE_PLAN)
    assert result == {"매출": 300_000, "비용": 60_000, "수익": 240_000, "손익분기 고객 수": 1}


def test_break_even_rounds_up_to_a_whole_customer():
    # 고객은 0.5명을 받을 수 없으므로 올림해야 손해가 나지 않는다.
    plan = MonthlyPlan(price=30_000, customers_per_month=0, cost_per_customer=10_000, fixed_cost=50_000)
    assert estimate_month(plan)["손익분기 고객 수"] == 3


def test_price_not_above_cost_is_rejected():
    plan = MonthlyPlan(price=5_000, customers_per_month=3, cost_per_customer=5_000, fixed_cost=0)
    with pytest.raises(ValueError, match="가격이 고객 1명당 비용보다 높아야 합니다."):
        estimate_month(plan)


def test_negative_values_are_rejected():
    plan = MonthlyPlan(price=10_000, customers_per_month=-1, cost_per_customer=0, fixed_cost=0)
    with pytest.raises(ValueError, match="음수"):
        estimate_month(plan)


def test_every_prompt_carries_the_safety_rule_and_customer():
    prompts = build_prompts(SAMPLE_IDEA)
    assert list(prompts) == ["[1] 아이디어 발산", "[2] 고객 검증 질문", "[3] 소개 페이지 문구"]
    for prompt in prompts.values():
        assert SAFETY_RULE in prompt
        assert SAMPLE_IDEA.customer in prompt
