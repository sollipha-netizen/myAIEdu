"""7주차 예시 코드가 실습 가이드의 약속(분량, 정직 조건, 사실 포함)을 지키는지 확인한다."""

from brand_prompts import (
    HONESTY_RULE,
    ONE_LINER_MAX_CHARS,
    SAMPLE_PROFILE,
    CareerProfile,
    build_all_prompts,
)


def test_three_prompts_are_built_in_practice_order():
    prompts = build_all_prompts(SAMPLE_PROFILE)
    assert list(prompts) == ["[1] 한 줄 소개", "[2] 3줄 프로필", "[3] SNS 소개글"]


def test_every_prompt_carries_the_honesty_rule_and_facts():
    # 정직 조건이 빠지면 AI가 성과를 지어낼 수 있으므로 모든 질문에 있어야 한다.
    for prompt in build_all_prompts(SAMPLE_PROFILE).values():
        assert HONESTY_RULE in prompt
        assert SAMPLE_PROFILE.career in prompt
        assert SAMPLE_PROFILE.audience in prompt


def test_one_liner_prompt_states_the_length_limit():
    prompt = build_all_prompts(SAMPLE_PROFILE)["[1] 한 줄 소개"]
    assert f"{ONE_LINER_MAX_CHARS}자 이내" in prompt


def test_missing_achievements_are_written_as_none_instead_of_blank():
    profile = CareerProfile("총무 18년", [], "꼼꼼함", "신입 총무 담당자", "친절하게")
    prompt = build_all_prompts(profile)["[2] 3줄 프로필"]
    assert "- 성과: 없음" in prompt
