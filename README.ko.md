# ShortsScope — 쇼츠 영상을 프레임 단위로 살펴보는 도구

[English](README.md) · **한국어**

AI가 필요에 따라 호출하는 모델 독립적인 CLI입니다. **빠른 프레임 추출 → 마지막 프레임 보강 → 번호·시간이 있는 장면 모음 이미지**를 만듭니다. OpenClaw에서 쓰기 위해 시작했지만 OpenClaw에 종속되지 않습니다. [claude-video](https://github.com/bradautomates/claude-video)의 커뮤니티 포크이며 원저작자 MIT 고지를 유지합니다. 목적은 참고 영상을 분석해 **자신의 쇼츠 제작에 활용하는 것**입니다.

세 기능은 독립적으로 사용할 수 있습니다.

- **`extract`**: 로컬 영상에서 개별 프레임·장면 모음 이미지·manifest를 생성합니다.
- **`measure`**: 선택적으로 로컬에서 움직임·OCR·포즈 가시성 근거를 측정합니다.
- **`analyze`**: AI용 분석 요청을 준비하거나, 다른 AI의 응답을 가져와 검증하거나, 명시적으로 Codex를 호출합니다.

자동으로 영상을 다운로드하거나 새 영상을 만들지 않습니다. `extract`는 모델 호출·업로드가 없고 `analyze`도 기본은 오프라인 준비입니다. `--backend codex`를 지정한 경우에만 별도 인증된 서비스로 선택한 이미지를 보냅니다. 어떤 구간을 얼마나 볼지는 호출하는 AI가 정합니다.

## AI에게 설치 요청하기 — 복사·붙여넣기

현재 사용하는 **실행 환경에 맞는 코드 블록 하나**를 복사하세요. 저장소 복제 → 가상환경 → 스킬 등록 → 실제 인식 확인 순서로 진행합니다. 로컬 도구와 영구 저장 공간이 없는 일반 웹 채팅에서는 설치까지 실행할 수 없습니다.

### Codex

```text
https://github.com/JangHyuckYun/shorts-scope 를 현재 Codex 환경에 설치해줘.
먼저 해당 저장소의 docs/install/README.md와 docs/install/codex.md를 읽어줘.
영구 보관할 사용자 디렉터리에 git clone하되 기존 파일·변경은 보존해줘.
저장소의 Python venv를 만들고 requirements-compact.txt를 설치한 뒤 FFmpeg/ffprobe를 확인해줘.
scripts/install_skill.py를 읽고 --host codex --dry-run으로 경로를 확인한 뒤 현재 사용자용 스킬을 설치해줘.
설치된 실행기 작동과 Codex의 shorts-scope 스킬 인식을 각각 확인해줘.
관련 없는 설정 변경·기존 스킬 덮어쓰기·선택 모델 설치는 하지 마.
영구 로컬 실행이 불가능하면 설치 완료라고 하지 말고 필요한 환경을 알려줘.
끝나면 실제 설치 위치와 $shorts-scope 사용 예시를 보여줘.
```

[Codex 상세 설치 가이드](docs/install/codex.md)

### Claude Code

```text
https://github.com/JangHyuckYun/shorts-scope 를 현재 Claude Code 환경에 설치해줘.
먼저 해당 저장소의 docs/install/README.md와 docs/install/claude.md를 읽어줘.
영구 보관할 사용자 디렉터리에 git clone하고 기존 작업은 덮어쓰지 마.
저장소 venv와 requirements-compact.txt를 설치하고 FFmpeg/ffprobe를 확인해줘.
scripts/install_skill.py를 검토한 뒤 --host claude --dry-run으로 경로를 보고 현재 사용자용으로 설치해줘.
설치된 실행기를 실행하고 Claude Code가 shorts-scope 스킬을 인식하는지 확인해줘.
설치 중 관련 없는 설정 변경이나 유료 분석 호출, 선택 모델 설치는 하지 마.
일반 Claude 웹처럼 로컬 실행 환경이 없으면 설치됐다고 하지 말고 제한을 설명해줘.
실제 설치 위치와 /shorts-scope 사용법을 알려줘.
```

[Claude Code 상세 설치 가이드](docs/install/claude.md)

### Grok

```text
https://github.com/JangHyuckYun/shorts-scope 를 설치하고 싶어.
먼저 너를 실행하는 호스트, 영구 로컬 셸·파일 접근 가능 여부, 그 호스트의 공식 스킬 등록 방식을 확인해줘.
저장소의 docs/install/README.md와 docs/install/grok.md를 읽어줘.
OpenClaw 안에서 Grok을 쓰는 환경이면 docs/install/openclaw.md에 따라 실제 에이전트 워크스페이스에 설치해줘.
다른 로컬 에이전트가 Agent Skills를 지원한다면 확인된 등록 경로에만 generic 설치기를 dry-run 후 사용해줘.
Grok 등록 API나 ~/.grok/skills 폴더를 임의로 만들지 마.
로컬 실행이 없는 일반 Grok 웹이면 설치 완료라고 하지 말고 OpenClaw 등 로컬 호스트를 통한 설치 경로를 안내해줘.
채팅으로 API 키를 요구하거나 관련 없는 설정을 변경하지 마.
```

[Grok·호스트 구분 상세 가이드](docs/install/grok.md)

### OpenClaw

```text
https://github.com/JangHyuckYun/shorts-scope 를 현재 OpenClaw 에이전트에 설치해줘.
먼저 저장소의 docs/install/README.md와 docs/install/openclaw.md를 읽어줘.
실제 에이전트 워크스페이스와 실행 머신을 신뢰할 수 있는 런타임 정보로 확인해줘. 기본 경로를 추측하지 마.
그 머신의 영구 디렉터리에 git clone하고 기존 작업을 보존해줘.
저장소 venv에 requirements-compact.txt를 설치하고 FFmpeg/ffprobe를 확인해줘.
scripts/install_skill.py를 읽고 --host openclaw --workspace <실제 워크스페이스> --dry-run 후 설치해줘.
설치된 실행기를 실행하고 동일 에이전트·Gateway의 skills list/info/check로 실제 스킬 인식을 확인해줘.
기존 설치 정책은 지키고 허용 목록을 바꾸거나 거절을 우회하지 마.
설치 중 유료 모델 호출·선택 가중치 설치는 하지 마.
파일 설치와 실제 인식 확인을 구분해 설치 위치와 사용 예시를 보여줘.
```

[OpenClaw 상세 설치 가이드](docs/install/openclaw.md)

Grok을 OpenClaw에서 사용한다면 OpenClaw 방식으로 설치합니다. 일반 Grok 웹의 로컬 스킬 등록은 확인되지 않았습니다. 설치기는 경로와 실행기를 검사하지만 **호스트가 스킬을 실제로 인식하는지는 별도 확인**해야 합니다. [공통 설치·업데이트 안내](docs/install/README.md)

## 공개 저장소로 실제 설치·사용 검증

공개 GitHub를 새로 clone해 실제 OpenClaw 워크스페이스에 설치했고, 스킬 인식과 설치된 실행기를 통한 추출·실제 모델 분석을 확인했습니다. [실행 기록·생성 이미지·원본 결과·남은 오류](docs/INSTALL_VERIFICATION.md)에서 증거를 볼 수 있습니다.

## 직접 설치하고 프레임 추출하기

Python 3.10 이상과 PATH에 등록된 FFmpeg/ffprobe가 필요합니다. Pillow는 이 추출 기능의 필수 의존성입니다. 아래 명령은 Linux/macOS 또는 Windows의 WSL 환경 기준입니다.

```sh
git clone https://github.com/JangHyuckYun/shorts-scope.git
cd shorts-scope
python3 -m venv .venv
.venv/bin/pip install -r requirements-compact.txt
.venv/bin/python cli.py extract video.mp4 --out output/overview
```

표준 출력은 JSON이며 실패하면 종료 코드가 0이 아닙니다. 출력 디렉터리는 비어 있어야 합니다. `sheet.jpg` 또는 PNG, 개별 프레임, `manifest.json`, 선택적으로 사용할 `prompt.txt`를 생성합니다. JSON에는 상대 파일 경로·시간·적용 옵션·처리 시간이 기록됩니다. AI에는 파일 경로 문자열만 보내지 말고 **실제 이미지를 읽게 하세요.** `END`는 선택 구간의 마지막 디코딩 프레임이며 정확한 시각을 뜻하지 않습니다.

## AI가 조절할 수 있는 추출 인자

- `--sampler keyframes|uniform`: 기본은 원본의 빠른 키프레임 추출·대체 경로를 재사용합니다. `uniform`은 시간 간격을 고르게 배분합니다.
- `--start 초`, `--end 초`: 분석할 구간. 끝 시각은 제외하며 기본은 영상 전체입니다.
- `--max-frames N`: 끝 프레임을 포함한 전체 예산 2–24장, 기본 8장. 실제 장수는 더 적을 수 있습니다.
- `--no-endpoint`: 마지막 프레임 예약·추가를 끕니다.
- `--no-dedup`: 키프레임 중복 제거를 끕니다. 균등 추출의 시간 기준 프레임은 중복 제거하지 않습니다.
- `--width N`: 프레임 너비 160–640, 기본 240.
- `--max-height N`: 셀 이미지 높이 상한 160–1280. 기본은 너비의 두 배이며 종횡비를 유지합니다.
- `--columns N`: 열 수 1–6, 기본 3.
- `--padding N`: 셀 사이 여백 0–64px, 기본 12. 여백을 없애면 시점 혼동이 늘 수 있습니다.
- `--format jpg|png`: 기본 JPG.
- `--quality N`: JPEG 품질 1–95, 기본 85. PNG에는 적용하지 않습니다.
- `--out DIR`: 새 출력 디렉터리 또는 빈 디렉터리. 필수입니다.

```sh
# 전체를 가볍게 확인
.venv/bin/python cli.py extract video.mp4 --out output/coarse \
  --max-frames 6 --columns 3 --width 240

# 10–14초 구간을 더 촘촘하게 확인
.venv/bin/python cli.py extract video.mp4 --out output/detail \
  --start 10 --end 14 --sampler uniform --max-frames 12 \
  --columns 4 --width 320 --padding 16 --format png

# 마지막 프레임 추가·중복 제거 없이 추출
.venv/bin/python cli.py extract video.mp4 --out output/raw \
  --no-endpoint --no-dedup
```

기존 `python skills/watch/scripts/compact.py ...` 진입점도 유지됩니다. CLI 실행만으로 OpenClaw 설정이나 설치된 스킬이 바뀌지 않습니다. 원본 `/watch` 스킬 등록·마켓플레이스·자동 설정 훅·기존 배포 자동화는 이 포크에서 제거했습니다. 예전 Python 유틸리티는 소스 호환성을 위해 남겨두되 설치는 위의 ShortsScope 안내를 따르세요. [원본 출처·유지한 고지](UPSTREAM.md)

## 선택한 프레임의 세부 분석

분석은 작은 격자 이미지 대신 **선택한 개별 프레임**을 읽어 사물·위치·자세, 글자와 스타일, 프레임 사이 움직임, 편집 관찰과 제작 제안을 기록합니다.

```sh
# 모델 호출 없이 이미지 목록·프롬프트·JSON 형식 준비
.venv/bin/python cli.py analyze output/overview/manifest.json --out output/request

# 다른 AI의 원본 JSON 응답을 검증해 결과·보고서 저장
.venv/bin/python cli.py analyze output/overview/manifest.json --out output/analysis \
  --backend import --response response.json

# 별도 인증된 Codex를 명시적으로 호출하는 선택 기능
.venv/bin/python cli.py analyze output/overview/manifest.json --out output/codex-analysis \
  --backend codex --model gpt-5.6-luna --effort low --timeout 180
```

Codex 어댑터는 `--image`, `--output-schema`, `--json`, `--ignore-user-config`, `--ephemeral`을 지원하는 별도 설치·인증된 CLI가 필요합니다. 계정에서 사용할 수 있는 이미지 입력 모델을 선택하세요. 준비·가져오기에는 OpenClaw나 Codex가 필요하지 않습니다.

결과는 AI용 `analysis.json`과 사람이 읽는 `report.md`입니다. 관찰과 제작 제안을 구분합니다. 서체 느낌·굵기·외곽선·그림자는 **영상에서 보이는 형태의 추정**이며 편집기 설정 복원이 아닙니다. `exact_font_name`은 항상 null입니다. 모든 영상 프레임을 빠짐없이 분석하거나 객체 추적·음성·OCR 정확도를 보장하지 않습니다. 후속 구간 제안은 데이터이며 자동 실행하지 않습니다.

[분석 항목·사용법·검증 상세](docs/SHORTS_ANALYSIS.md)

## 로컬 측정 근거 추가하기

```sh
# 선택 기능: 로컬 측정 의존성 설치
.venv/bin/python -m pip install -r requirements-evidence.txt
.venv/bin/python cli.py measure output/detail/manifest.json --out output/evidence \
  --motion-roi 0,0,1,0.35

# 촘촘한 측정값은 유지하고 AI에는 선택한 프레임만 전달
.venv/bin/python cli.py analyze output/detail/manifest.json --out output/grounded \
  --evidence output/evidence/evidence.json --select-frames 1,3,5,7
```

ROI는 실제로 배경이 보이는 영역을 선택해야 합니다. 위쪽 띠가 모든 영상에서 배경인 것은 아닙니다. 선택 OCR 기능은 글자 위치·확대 이미지·사용자가 제공한 폰트 후보 비교를 추가합니다. 선택 포즈 기능은 발이 충분히 보이는지 확인하는 보조 수단이지 **걷기·달리기 분류기**가 아닙니다.

[측정 명령·한계](docs/EVIDENCE.md) · [전후 비교 결과](docs/BENCHMARK.md)

## 원본과 다른 점

빠른 키프레임 추출과 중복 제거는 원본을 재사용합니다. 추가한 기능은 마지막 프레임 보존, 번호가 있는 크기 제한 장면 모음, 구간·배치·인코딩 조절, JSON 출력입니다. 별도 분석 어댑터에는 모델 독립적인 응답 형식·위치 및 참조 검증·보고서를 추가했습니다. 새로운 영상 모델이나 새로운 격자 입력 연구 기법은 아닙니다.

## 검증 범위와 한계

25.7초짜리 한 영상의 초기 실험에서 입력 토큰 21,981→17,638, 전처리 2.45→0.46초를 측정했습니다. 프롬프트·해상도·실행 환경의 문맥이 달라졌으므로 일반적인 정확도·속도·요금 절감이나 현재 CLI 성능을 보장하는 수치는 아닙니다. 걷기/달리기 구분은 아직 검증되지 않았습니다. 작은 셀은 세부 정보를 잃고 큰 이미지는 모델에서 축소될 수 있습니다. 프레임 수만 늘려도 정확도가 좋아진다는 보장은 없습니다. 균등 추출은 현재 시점별 탐색을 사용하며 좁은 구간을 다시 보는 용도이지 가장 빠른 방식이라는 주장이 아닙니다.

[선행 연구·개선 방향](docs/RESEARCH.md) · [개발 배경](docs/OPENCLAW.md) · [라이선스 검토](docs/LICENSE_REVIEW.md)

## 라이선스

[MIT](LICENSE). 원저작자 고지를 유지합니다. 제3자 영상·스크린샷·댓글·모델 가중치는 포함하지 않습니다. 외부 FFmpeg 빌드와 사용하는 콘텐츠의 이용 조건은 별개입니다. OpenClaw·Anthropic·OpenAI·xAI의 공식 프로젝트가 아닙니다. 연결된 상세 문서는 현재 영어로 제공합니다.
