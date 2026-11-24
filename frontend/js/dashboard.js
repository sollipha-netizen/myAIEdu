// API 문서 및 실습 대시보드
// 데이터 출처: 백엔드 /openapi.json(엔드포인트 명세), /courses/{id}/curriculum(실습 단계).
// 화면에 값을 직접 복사해 두지 않으므로, 백엔드를 고치면 이 화면도 같이 바뀝니다.
// 공통 함수 getJson, escapeHtml, COURSE_ID는 app.js에서 가져옵니다.

const HTTP_METHODS = ["get", "post", "put", "patch", "delete"];

// 명세의 $ref("#/components/schemas/이름")를 실제 스키마 객체로 바꿉니다.
function resolveSchema(spec, schema) {
  if (!schema || !schema.$ref) return schema;
  const name = schema.$ref.split("/").pop();
  return spec.components.schemas[name];
}

// 스키마 한 조각을 사람이 읽을 수 있는 타입 문자열로 바꿉니다.
function describeType(spec, prop) {
  if (!prop) return "any";
  if (prop.$ref) return prop.$ref.split("/").pop();
  if (prop.enum) return prop.enum.map((value) => JSON.stringify(value)).join(" | ");
  if (prop.anyOf) return prop.anyOf.map((part) => describeType(spec, part)).join(" | ");
  if (prop.type === "array") return `list[${describeType(spec, prop.items)}]`;
  return prop.type || "any";
}

// Field 제약(길이, 범위)을 한국어 문구로 바꿉니다.
function describeConstraints(prop) {
  const parts = [];
  if (prop.minLength != null) parts.push(`최소 ${prop.minLength}자`);
  if (prop.maxLength != null) parts.push(`최대 ${prop.maxLength}자`);
  if (prop.minimum != null) parts.push(`${prop.minimum} 이상`);
  return parts.join(", ");
}

// 요청 본문 스키마에서 필드 목록을 뽑습니다.
function readBodyFields(spec, operation) {
  const content = operation.requestBody && operation.requestBody.content;
  const jsonBody = content && content["application/json"];
  const schema = resolveSchema(spec, jsonBody && jsonBody.schema);
  if (!schema || !schema.properties) return [];

  const required = new Set(schema.required || []);
  return Object.entries(schema.properties).map(([name, prop]) => ({
    name,
    type: describeType(spec, prop),
    required: required.has(name),
    constraints: describeConstraints(prop),
  }));
}

// 관리자 전용 여부. require_admin이 X-Admin-Key 헤더를 요구하면 명세에 header 파라미터로 나옵니다.
function isAdminOnly(operation) {
  return (operation.parameters || []).some(
    (param) => param.in === "header" && param.name.toLowerCase() === "x-admin-key",
  );
}

function renderFieldTable(fields) {
  if (fields.length === 0) return `<p class="muted">요청 본문이 없습니다.</p>`;
  const rows = fields.map((field) => `
    <tr>
      <td><code>${escapeHtml(field.name)}</code></td>
      <td>${escapeHtml(field.type)}</td>
      <td>${field.required ? "필수" : "선택"}</td>
      <td>${escapeHtml(field.constraints)}</td>
    </tr>`).join("");
  return `
    <div class="table-wrap">
      <table class="field-table">
        <thead><tr><th>필드</th><th>타입</th><th>필수</th><th>제약</th></tr></thead>
        <tbody>${rows}</tbody>
      </table>
    </div>`;
}

function renderEndpoint(spec, path, method, operation) {
  const admin = isAdminOnly(operation);
  const statusCodes = Object.keys(operation.responses || {}).join(", ");
  return `
    <details class="endpoint">
      <summary>
        <span class="method method-${method}">${method.toUpperCase()}</span>
        <code>${escapeHtml(path)}</code>
        ${admin ? `<span class="badge badge-admin">관리자 전용</span>` : ""}
      </summary>
      <p class="endpoint-desc">${escapeHtml(operation.summary || operation.operationId || "")}</p>
      ${renderFieldTable(readBodyFields(spec, operation))}
      <p class="muted">응답 코드: ${escapeHtml(statusCodes)}</p>
    </details>`;
}

// 명세의 모든 엔드포인트를 목록으로 만듭니다.
function renderEndpointList(spec) {
  const blocks = [];
  for (const [path, item] of Object.entries(spec.paths)) {
    for (const method of HTTP_METHODS) {
      if (item[method]) blocks.push(renderEndpoint(spec, path, method, item[method]));
    }
  }
  return blocks.join("");
}

function countOperations(spec) {
  let total = 0;
  let admin = 0;
  for (const item of Object.values(spec.paths)) {
    for (const method of HTTP_METHODS) {
      if (!item[method]) continue;
      total += 1;
      if (isAdminOnly(item[method])) admin += 1;
    }
  }
  return { total, admin };
}

// 실습 카드: 실습이 있는 주차를 찾아 단계를 보여 줍니다.
function renderPractice(curriculum) {
  const week = curriculum.weeks.find((item) => item.practice_title);
  if (!week) return `<p class="muted">등록된 실습이 없습니다.</p>`;
  const steps = (week.practice_steps || []).map((step) => `<li>${escapeHtml(step)}</li>`).join("");
  return `
    <p class="practice-week"><span class="week-no">${week.week_no}주차</span></p>
    <p><strong>${escapeHtml(week.practice_title)}</strong></p>
    <ol class="steps">${steps}</ol>`;
}

function showDashStatus(text, type = "") {
  const el = $("#dash-status");
  el.textContent = text;
  el.className = `message ${type}`.trim();
}

async function loadDashboard() {
  try {
    const [spec, curriculum] = await Promise.all([
      getJson("/openapi.json"),
      getJson(`/courses/${COURSE_ID}/curriculum`),
    ]);

    const { total, admin } = countOperations(spec);
    $("#dash-summary").innerHTML = `
      <div class="stat"><span class="stat-value">${total}</span><span class="stat-label">엔드포인트</span></div>
      <div class="stat"><span class="stat-value">${admin}</span><span class="stat-label">관리자 전용</span></div>
      <div class="stat"><span class="stat-value">${curriculum.weeks.length}</span><span class="stat-label">커리큘럼 주차</span></div>`;

    $("#practice").innerHTML = renderPractice(curriculum);
    $("#api-list").innerHTML = renderEndpointList(spec);
    showDashStatus(`백엔드 연결됨 (${spec.info.title} ${spec.info.version})`, "success");
  } catch (error) {
    // 백엔드가 꺼져 있거나 응답이 잘못된 경우. 나머지 화면은 그대로 동작합니다.
    $("#dash-summary").innerHTML = "";
    $("#practice").innerHTML = "";
    $("#api-list").innerHTML = "";
    showDashStatus(
      "백엔드에 연결할 수 없어 명세를 불러오지 못했습니다. 백엔드 서버(127.0.0.1:8000)가 실행 중인지 확인해 주세요.",
      "error",
    );
  }
}

// ---------- 실행 해보기 ----------
// 버튼 하나가 API 한 번을 호출하고 결과를 바로 보여 줍니다.
// 모든 단계는 읽기 전용이거나, 입력 검증에서 막혀 DB에 저장되지 않는 요청입니다.
// 관리자 API는 키를 페이지에 넣지 않으므로 여기서 호출하지 않습니다.
const PLAYGROUND_STEPS = [
  {
    id: "list",
    method: "GET",
    path: "/courses",
    label: "과정 목록 조회",
    description: "모집 중인 과정이 어떤 모습으로 응답하는지 확인합니다.",
    expect: 200,
    call: () => getJson("/courses"),
    describe: (data) => `모집 중인 과정 ${data.length}개`,
  },
  {
    id: "detail",
    method: "GET",
    path: `/courses/${COURSE_ID}`,
    label: "정원과 잔여 좌석 확인",
    description: "정원, 신청 인원, 남은 자리를 계산한 결과를 봅니다.",
    expect: 200,
    call: () => getJson(`/courses/${COURSE_ID}`),
    describe: (data) =>
      `정원 ${data.capacity}명 · 신청 ${data.enrolled_count}명 · 남은 자리 ${data.seats_left}명`,
  },
  {
    id: "curriculum",
    method: "GET",
    path: `/courses/${COURSE_ID}/curriculum`,
    label: "8주 커리큘럼 조회",
    description: "주차별 주제와 실습 주차가 어디인지 확인합니다.",
    expect: 200,
    call: () => getJson(`/courses/${COURSE_ID}/curriculum`),
    describe: (data) => {
      const practiceWeeks = data.weeks.filter((week) => week.practice_title).map((week) => `${week.week_no}주차`);
      return `${data.weeks.length}개 주차 · 실습 주차: ${practiceWeeks.join(", ") || "없음"}`;
    },
  },
  {
    id: "health",
    method: "GET",
    path: "/health",
    label: "서버 상태 확인",
    description: "백엔드 서버가 응답하는지 가장 간단히 확인합니다.",
    expect: 200,
    call: () => getJson("/health"),
    describe: (data) => `서버 상태: ${data.status}`,
  },
  {
    id: "validate-phone",
    method: "POST",
    path: "/students",
    label: "잘못된 휴대폰 번호 시도",
    description: "일부러 틀린 번호를 보냅니다. 입력 검증에서 막혀 저장되지 않아야 합니다.",
    expect: 422,
    call: () => postJson("/students", { name: "연습용", phone: "12345", consent: true }),
    describe: (_data, message) => `서버 메시지: "${message}" · 저장되지 않았습니다.`,
  },
  {
    id: "validate-consent",
    method: "POST",
    path: "/students",
    label: "동의 없이 등록 시도",
    description: "개인정보 동의를 빼고 보냅니다. 동의 검사에서 막혀야 합니다.",
    expect: 422,
    call: () => postJson("/students", { name: "연습용", phone: "010-0000-0000", consent: false }),
    describe: (_data, message) => `서버 메시지: "${message}" · 저장되지 않았습니다.`,
  },
];

function renderPlayground() {
  $("#playground").innerHTML = PLAYGROUND_STEPS.map((step) => `
    <div class="play-card">
      <div class="play-head">
        <span class="method method-${step.method.toLowerCase()}">${step.method}</span>
        <code>${escapeHtml(step.path)}</code>
      </div>
      <p class="play-desc">${escapeHtml(step.description)}</p>
      <button type="button" class="btn btn-primary play-btn" data-step="${escapeHtml(step.id)}">
        ${escapeHtml(step.label)}
      </button>
      <div class="play-result" id="result-${escapeHtml(step.id)}" aria-live="polite"></div>
    </div>`).join("");
}

// 응답을 사람이 읽을 수 있는 형태로 줄입니다. 긴 응답은 잘라서 보여 줍니다.
function formatPreview(data) {
  const text = JSON.stringify(data, null, 2) ?? "";
  return text.length > 500 ? `${text.slice(0, 500)}\n...` : text;
}

async function runStep(step, resultEl, button) {
  button.disabled = true;
  resultEl.className = "play-result running";
  resultEl.textContent = "요청을 보내는 중...";

  const started = performance.now();
  let actual = null;
  let data = null;
  let message = "";

  try {
    data = await step.call();
    actual = 200; // 성공 응답은 모두 200 (POST 성공 201은 이 단계에서 쓰지 않음)
  } catch (error) {
    if (error instanceof ApiError) {
      actual = error.status;
      message = error.message;
    } else {
      message = "서버에 연결할 수 없습니다. 백엔드 서버가 실행 중인지 확인해 주세요.";
    }
  } finally {
    button.disabled = false;
  }

  const ms = Math.round(performance.now() - started);
  const passed = actual === step.expect;
  const statusText = actual === null ? "연결 실패" : `HTTP ${actual}`;

  const explain = actual === null
    ? message
    : step.describe(data, message);
  const preview = actual === null
    ? ""
    : `<pre class="play-json">${escapeHtml(formatPreview(data ?? { detail: message }))}</pre>`;

  resultEl.className = `play-result ${passed ? "pass" : "fail"}`;
  resultEl.innerHTML = `
    <p class="play-verdict">${passed ? "✔ 예상한 결과입니다" : "✖ 예상과 다릅니다"} · ${statusText} · ${ms}ms</p>
    <p class="play-explain">${escapeHtml(explain)}</p>
    ${preview}`;
}

function handlePlaygroundClick(event) {
  const button = event.target.closest("button[data-step]");
  if (!button || button.disabled) return;
  const step = PLAYGROUND_STEPS.find((item) => item.id === button.dataset.step);
  if (!step) return;
  runStep(step, $(`#result-${step.id}`), button);
}

function init() {
  renderPlayground();
  $("#playground").addEventListener("click", handlePlaygroundClick);
  loadDashboard();
}

document.addEventListener("DOMContentLoaded", init);
