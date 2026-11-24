# 7·8주차 상세 학습 자료

`4050 AI 실전 입문` 과정의 7주차와 8주차 강의록, 실습 가이드, 예시 코드입니다.
강사용 원고와 수강생 배포용 자료를 겸합니다.

## 구성

| 주차 | 주제 | 강의록 | 실습 가이드 | 예시 코드 |
|---|---|---|---|---|
| 7 | 퍼스널 브랜딩 완성형 | [lecture.md](week07/lecture.md) | [practice.md](week07/practice.md) | [brand_prompts.py](week07/examples/brand_prompts.py), [brand_profile.html](week07/examples/brand_profile.html) |
| 8 | 나의 경험, AI를 만나 비즈니스가 되다 | [lecture.md](week08/lecture.md) | [practice.md](week08/practice.md) | [business_canvas.py](week08/examples/business_canvas.py), [landing_page.html](week08/examples/landing_page.html) |

## 예시 코드 실행

예시 코드는 표준 라이브러리만 씁니다. 설치할 것이 없고, AI 서비스 키도 필요 없습니다.
파이썬 예시는 **AI에게 붙여 넣을 질문(프롬프트)을 만들어 주는 도구**입니다. 만든 질문은 ChatGPT, Claude, Gemini 등 평소 쓰는 AI 대화창에 붙여 넣습니다.

```bash
cd docs/curriculum/week07/examples
python brand_prompts.py          # 7주차: 브랜딩 질문 만들기

cd ../../week08/examples
python business_canvas.py        # 8주차: 비즈니스 질문 만들기와 수익 계산
```

HTML 예시는 파일을 더블클릭해 브라우저로 엽니다. 서버가 필요 없습니다.

예시 코드 테스트:

```bash
python -m pytest docs/curriculum -q
```

## 확인 필요 항목

- [확인 필요] 현재 DB 시드(`backend/scripts/seed_curriculum.py`)의 7·8주차 제목은 `나만의 AI 활용 루틴 만들기`, `마무리: 이력서·자기소개서 다듬기`입니다. 이 자료의 주제와 다르므로, 주제를 확정하면 DB 값도 함께 고쳐야 화면과 일치합니다.
- [확인 필요] 1회 수업 시간. 이 자료는 **120분(강의 50분 + 실습 60분 + 공유 10분)** 기준으로 짰습니다.
- 자료 위치: 목표 구조(`src/back`, `src/front`)는 아직 마이그레이션 전이고, 학습 자료는 앱 코드가 아니므로 `docs/curriculum/`에 둡니다.
