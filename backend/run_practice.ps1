# 실습 모드 서버 실행 스크립트
# 페이지(frontend)와 API를 같은 주소에서 함께 제공합니다.
# 실습 모드(PRACTICE_MODE=1)에서는 수강생 등록과 신청이 저장되지 않습니다.
#
# 사용법 (backend 폴더에서):
#   .\run_practice.ps1                 # 기본 포트 8000
#   .\run_practice.ps1 -Port 9000      # 다른 포트
#
# Python 실행 명령은 PYTHON_EXE 환경 변수로 지정할 수 있습니다.
#   예: $env:PYTHON_EXE = "C:\...\Python312\python.exe"
# 지정하지 않으면 "py -3"를 씁니다.

param(
    [int]$Port = 8000
)

$ErrorActionPreference = "Stop"

# 실습 모드를 강제로 켭니다. 이 스크립트로 띄우면 저장 기능이 꺼집니다.
$env:PRACTICE_MODE = "1"

Set-Location -Path $PSScriptRoot

if ($env:PYTHON_EXE) {
    $python = $env:PYTHON_EXE
    $pythonArgs = @("-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "$Port")
} else {
    $python = "py"
    $pythonArgs = @("-3", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "$Port")
}

Write-Host "실습 모드 서버를 시작합니다. 주소: http://<이 PC의 IP>:$Port"
Write-Host "이 PC에서 확인: http://127.0.0.1:$Port"
& $python @pythonArgs
