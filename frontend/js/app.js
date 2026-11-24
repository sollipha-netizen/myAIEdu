// 화면 렌더링과 수강 신청 처리
// 백엔드가 이 화면과 API를 같은 주소에서 함께 제공하므로 상대 경로를 씁니다.
// 페이지를 백엔드 밖(다른 주소)에서 따로 열 때만 전체 주소를 넣으세요. 예: "https://example.com"
const API_BASE = "";

const $ = (selector) => document.querySelector(selector);

class ApiError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

// 과정과 커리큘럼은 백엔드 API에서 받습니다. 프론트에 데이터를 복사해 두지 않습니다.
const COURSE_ID = 1;
let COURSE = null;      // 과정 정보 (불러오기 전에는 null)
let CURRICULUM = [];    // 주차 목록

async function loadCurriculum() {
  try {
    const [course, curriculum] = await Promise.all([
      getJson(`/courses/${COURSE_ID}`),
      getJson(`/courses/${COURSE_ID}/curriculum`),
    ]);
    COURSE = course;
    CURRICULUM = curriculum.weeks;
    renderCurriculum();
  } catch (error) {
    $("#week-list").innerHTML =
      `<li class="muted">커리큘럼을 불러오지 못했습니다. 서버 연결을 확인해 주세요.</li>`;
  }
}

// 커리큘럼 렌더링 (1주차만 기본으로 펼침)
function renderCurriculum() {
  $("#week-list").innerHTML = CURRICULUM.map((week, index) => {
    const practice = week.practice_title
      ? `<div class="practice">
           <strong>핵심 실습: ${escapeHtml(week.practice_title)}</strong>
           <ol>${(week.practice_steps || []).map((step) => `<li>${escapeHtml(step)}</li>`).join("")}</ol>
         </div>`
      : "";
    return `
      <li>
        <details ${index === 0 ? "open" : ""}>
          <summary><span class="week-no">${week.week_no}주차</span>${escapeHtml(week.title)}</summary>
          <p><strong>학습 목표</strong> ${escapeHtml(week.goal)}</p>
          ${practice}
        </details>
      </li>`;
  }).join("");

  $("#course-price").textContent =
    COURSE.price == null ? "추후 안내" : `${COURSE.price.toLocaleString("ko-KR")}원`;
}

function setMessage(text, type = "") {
  const el = $("#form-message");
  el.textContent = text;
  el.className = `message ${type}`.trim();
}

// 입력값 검사. 문제가 있으면 메시지 문자열, 없으면 null을 반환합니다.
function validate(form) {
  const name = form.name.value.trim();
  const phone = form.phone.value.replace(/-/g, "").trim();

  form.name.classList.toggle("invalid", !name);
  form.phone.classList.toggle("invalid", !/^01[016789]\d{7,8}$/.test(phone));

  if (!name) return "이름을 입력해 주세요.";
  if (!/^01[016789]\d{7,8}$/.test(phone)) return "휴대폰 번호를 확인해 주세요. (예: 010-1234-5678)";
  if (!form.consent.checked) return "개인정보 수집·이용에 동의해 주세요.";
  return null;
}

// 모든 백엔드 호출이 거치는 공통 함수. 오류 응답({"detail": ...})을 ApiError로 바꿉니다.
async function requestJson(path, options = {}) {
  const response = await fetch(API_BASE + path, options);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new ApiError(response.status, data.detail || "요청을 처리하지 못했습니다.");
  }
  return data;
}

async function getJson(path) {
  return requestJson(path);
}

async function postJson(path, body) {
  return requestJson(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

async function handleSubmit(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const submitBtn = $("#submit-btn");

  const problem = validate(form);
  if (problem) {
    setMessage(problem, "error");
    return;
  }

  if (!COURSE) {
    setMessage("과정 정보를 불러오지 못했습니다. 페이지를 새로고침해 주세요.", "error");
    return;
  }

  submitBtn.disabled = true;
  setMessage("신청을 처리하고 있습니다...");

  try {
    // 1) 수강생 등록  2) 과정 신청
    const student = await postJson("/students", {
      name: form.name.value.trim(),
      phone: form.phone.value.replace(/-/g, "").trim(),
      email: form.email.value.trim() || null,
      age_group: form.age_group.value,
      consent: form.consent.checked,
    });
    await postJson("/enrollments", {
      student_id: student.id,
      course_id: COURSE.id,
    });

    setMessage(
      practiceMode
        ? "실습 모드입니다. 입력한 내용은 저장되지 않았습니다."
        : "신청이 접수되었습니다. 감사합니다!",
      "success",
    );
    form.reset();
  } catch (error) {
    if (error instanceof ApiError) {
      setMessage(error.message, "error");
    } else {
      // fetch 자체가 실패한 경우 (서버가 꺼져 있음)
      setMessage("서버에 연결할 수 없습니다. 백엔드 서버가 실행 중인지 확인해 주세요.", "error");
    }
  } finally {
    submitBtn.disabled = false;
  }
}

// 서버가 실습 모드인지 확인해 안내 문구를 보여 줍니다. 확인하지 못하면 일반 모드로 둡니다.
let practiceMode = false;

async function checkPracticeMode() {
  try {
    const health = await getJson("/health");
    practiceMode = Boolean(health.practice_mode);
  } catch (error) {
    practiceMode = false;
  }
  $("#practice-banner").hidden = !practiceMode;
}

function init() {
  $("#apply-form").addEventListener("submit", handleSubmit);
  checkPracticeMode();
  loadCurriculum();
}

document.addEventListener("DOMContentLoaded", init);
