# 네이버 플레이스 자동 답글 시스템

네이버 플레이스의 리뷰에 자동으로 답글을 작성하는 프로그램입니다. OpenAI API를 활용하여 각 리뷰의 감정과 내용에 맞는 맞춤형 답글을 생성합니다.

## 주요 기능

- **자동 로그인**: 네이버 계정으로 자동 로그인
- **업체 선택**: 등록된 업체 자동 선택
- **AI 답글 생성**: OpenAI GPT-4o-mini를 활용한 맥락 기반 답글 생성
- **감정 분석**: 긍정/부정/중립 리뷰에 따른 적절한 톤 선택
- **템플릿 폴백**: API 키가 없거나 오류 발생 시 템플릿 기반 답글 사용
- **스크래핑 방지**: 랜덤 딜레이(5-10초)로 봇 감지 회피
- **GUI 설정**: 사용자 친화적인 설정 인터페이스

## 필수 요구사항

- Python 3.13 이상
- Chrome 브라우저
- 네이버 계정
- OpenAI API 키 (선택 사항)

## 설치 방법

### 1. 필요한 패키지 설치

```bash
py -m pip install selenium pyperclip webdriver-manager openai
```

### 2. 파일 구조

```
gold-keywords/
├── config_gui.py              # 설정 GUI 프로그램
├── naverplace-auto-login.py   # 메인 자동화 스크립트
├── ai_reply_generator.py      # AI 답글 생성 엔진
└── config.json                # 설정 파일 (자동 생성)
```

## 사용 방법

### 1단계: 설정 입력

GUI 프로그램을 실행하여 설정을 입력합니다:

```bash
python config_gui.py
```

입력 항목:
- **네이버 아이디**: 로그인할 네이버 계정
- **네이버 비밀번호**: 계정 비밀번호
- **업체명**: 관리할 네이버 플레이스 업체명
- **OpenAI API 키**: (선택) AI 답글 생성을 위한 API 키

> **참고**: OpenAI API 키가 없으면 템플릿 기반 답글이 사용됩니다.

### 2단계: 프로그램 실행

설정 창에서 **"저장 후 실행"** 버튼을 클릭하거나, 수동으로 실행:

```bash
python naverplace-auto-login.py
```

## OpenAI API 키 발급 방법

1. [OpenAI Platform](https://platform.openai.com/) 가입
2. API Keys 메뉴에서 새 키 생성
3. 생성된 키를 config_gui.py에 입력

**비용**: GPT-4o-mini는 답글당 약 0.001~0.005달러 (매우 저렴)

## AI 답글 생성 원리

### 감정별 답글 전략

| 감정 | 답글 전략 |
|------|-----------|
| **긍정** | 감사 표현 + 구체적 내용 언급 + 재방문 유도 |
| **부정** | 진심 어린 사과 + 문제점 인정 + 개선 약속 |
| **중립** | 방문 감사 + 피드백 수용 + 개선 의지 |

### 답글 작성 원칙

- 80-120자 내외 (간결함)
- 고객이 언급한 키워드 1-2개 포함 (진정성)
- 이모지 1-2개 사용 (친근함)
- 형식적 문구 지양
- 변명이나 책임 회피 금지

### 예시

**리뷰**: "커피가 정말 맛있었어요! 직원분들도 친절하시고 분위기도 좋았습니다."

**AI 답글**: "커피 맛있게 드셨다니 정말 기쁩니다! 😊 친절한 서비스도 만족스러우셨다니 감사합니다. 다음에도 좋은 시간 보내실 수 있도록 노력하겠습니다!"

---

**리뷰**: "음식이 너무 짜고 서비스가 별로였어요. 실망스러웠습니다."

**AI 답글**: "불편을 드려 정말 죄송합니다. 음식 간과 서비스 부분 즉시 개선하도록 하겠습니다. 더 나은 모습으로 다시 찾아뵙고 싶습니다."

## 보안 기능

- **봇 감지 방지**:
  - 클립보드 기반 입력 (pyperclip)
  - Automation flags 비활성화
  - 랜덤 대기 시간 (5-10초)
  - 자연스러운 사용자 행동 모방

- **자격 증명 보호**:
  - config.json에 안전하게 저장
  - GUI에서 비밀번호 마스킹
  - 하드코딩 방지

## 문제 해결

### 리뷰 버튼을 찾을 수 없는 경우

현재 알려진 이슈: 네이버 플레이스는 iframe 구조를 사용하므로, 리뷰 버튼을 찾지 못할 수 있습니다.

**해결 방법** (향후 업데이트 예정):
```python
# iframe으로 전환
driver.switch_to.frame("entryIframe")
# 리뷰 버튼 찾기
review_button = driver.find_element(...)
```

### Import 오류

```bash
# 패키지 재설치
py -m pip install --upgrade selenium pyperclip webdriver-manager openai
```

### Chrome 버전 호환성

webdriver-manager가 자동으로 호환 버전을 다운로드합니다. 문제 발생 시:

```bash
py -m pip install --upgrade webdriver-manager
```

## EXE 파일 생성 (배포용)

PyInstaller를 사용하여 실행 파일 생성:

```bash
# PyInstaller 설치
py -m pip install pyinstaller

# 설정 GUI EXE 생성
pyinstaller --onefile --windowed --name "네이버플레이스설정" config_gui.py

# 메인 프로그램 EXE 생성
pyinstaller --onefile --name "네이버플레이스자동답글" naverplace-auto-login.py
```

생성된 파일: `dist/네이버플레이스설정.exe`, `dist/네이버플레이스자동답글.exe`

## 주의사항

1. **네이버 이용 약관 준수**: 과도한 자동화는 계정 제재 대상이 될 수 있습니다.
2. **API 비용**: OpenAI API 사용 시 비용이 발생합니다 (매우 적지만).
3. **리뷰 검토**: AI가 생성한 답글을 자동 등록하기 전에 반드시 검토하세요.
4. **실행 빈도**: 너무 자주 실행하면 스크래핑으로 감지될 수 있습니다.

## 라이선스

개인 및 상업적 사용 가능합니다.

## 기여

버그 리포트 및 기능 제안 환영합니다!

## 버전 기록

- **v1.0** (2025-11-07)
  - 초기 릴리스
  - OpenAI GPT-4o-mini 통합
  - GUI 설정 인터페이스
  - 감정 분석 기반 답글 생성
  - 템플릿 폴백 기능
