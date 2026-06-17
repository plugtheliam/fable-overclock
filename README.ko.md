<div align="center">

[English](README.md) · [中文](README.zh.md) · [日本語](README.ja.md) · [Español](README.es.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · **한국어**

# fable-overclock

## Opus와 Sonnet, DeepSeek을 Fable급으로 돌려라.
### 아직 돌릴 수 있는 모델에서 Fable급 결과물을 뽑아낸다.

Sonnet과 DeepSeek은 숫자를 지어내고 검증을 건너뛴다. Opus는 시키지도 않은 일을 과하게 벌이고
요청 범위를 한참 넘어선다. fable-overclock이 손보는 건 모델이 아니라 그 *행동*이다. 값싼 모델은
모든 수치에 출처를 달고, 찍는 대신 UNKNOWN이라 말한다. Opus는 시킨 것만 정확히 하고 멈춘다.
같은 모델인데, 그대로 내보낼 결과물이 나온다. 말이 아니라 측정값이다 — DeepSeek에서 출처를 단
수치 비율이 **4% → 100%**로 올랐다.

이름은 말 그대로다 — CPU 오버클럭처럼, 가진 칩을 매번 진짜 한계까지 밀어붙인다. 운이 아니라
절차로. 모델의 순수 IQ를 올리는 게 아니다. 명령어 하나. stdlib만 쓴다. 지금 돌리는 모델에 그대로
붙는다.

![MIT](https://img.shields.io/badge/license-MIT-green)
![zero deps](https://img.shields.io/badge/deps-stdlib%20only-brightgreen)
![Claude Code](https://img.shields.io/badge/Claude%20Code-plugin%20%2B%20hook-8A63D2)
![tuned for](https://img.shields.io/badge/tuned-Opus%20%C2%B7%20Sonnet%20%C2%B7%20DeepSeek-orange)
![tests](https://img.shields.io/badge/tests-green-success)

</div>

![fable-overclock flagging a claim with no source](assets/demo-2x.gif)

## 모델마다 무엇을 얻는가

모델마다 값비싼 습관이 하나씩 있다 — 조용히 다시 짜게 만드는 코드, 틀린 숫자 하나, 존재하지도
않는 API를 좇다 날린 오후. fable-overclock은 그 습관을 하나하나 알고, 차단한다 — 그리고 증명한다:
테스트에서 게이트가 **지어낸 숫자 100%를 잡아냈고, 오탐은 0%였다**.

| 모델 | 너를 갉아먹는 습관 | 대신 얻는 것 |
|---|---|---|
| **Opus** | 과하게 벌이고, 요청 범위를 넘어 헤맨다 | 시킨 것만 정확히 하고 멈춘다 — 그리고 제쳐둔 더 단순한 선택지를 알려준다 |
| **Sonnet** | 검증을 건너뛰고, 출처를 빠뜨린다 | 모든 수치에 출처를 달고, "끝"이라 말하기 전에 요구사항을 하나씩 검증한다 |
| **DeepSeek** | 숫자도 API도 통째로 지어낸다 | 자신만만한 거짓말 대신 `UNKNOWN`. 나머지는 두 번째 모델이 다시 확인한다 |

이걸 두 겹으로 해낸다. 모델이 첫 토큰을 쓰기도 전에 **계약(contract)**이 로드되어, 규율이
처음부터 잡혀 있다. 결정론적 **게이트**가 받침대다 — 출력을 스스로 채점하고(LLM 심판 없이),
출처 없는 숫자·지어낸 숫자를 착지 직전에 잡아낸다. 그 결과는, 한 줄 한 줄 사실 확인할 필요 없는
결과물. 전체 동작은
[`docs/HOW-IT-WORKS.md`](docs/HOW-IT-WORKS.md).

## 왜 지금인가

<!-- FABLE-MOMENT:start — time-bound. Remove when Fable access is restored to non-US founders. -->
2026년 6월, 미국 수출 규제가 모든 외국 국적자에게서 Anthropic의 Fable 5와 Mythos 5를
끊어버렸다. 미국 밖 개발자라면, 프런티어 모델이 하룻밤 사이 스택에서 사라진 셈이다. 되찾을 길은
없다. 그러니 남은 모델로 프런티어급 결과물을 뽑아내게 만들어라 — 바람이 아니라 측정으로.
<!-- FABLE-MOMENT:end -->

## 직접 확인해봐라

같은 모델, 같은 프롬프트: *"지난달 투자자 업데이트를 핵심 수치와 함께 써줘."*

**DeepSeek, 그냥 단독으로**
```
지난 분기 매출이 38% 늘었고, 이탈률은 2.1%로 떨어졌으며, 사용자 14,000명이 늘었습니다.
```
자신만만하다. 근거는 하나도 없다. 그런 숫자를 준 적이 없는데 — 모델이 지어낸 것이다. 그대로
내보내는 순간, 그 실수는 네 것이 된다.

**DeepSeek, fable-overclock 위에서**
```
지난달 수치가 제게 없습니다 (UNKNOWN). 매출, 이탈률, 사용자 데이터를 주시면
각 숫자마다 출처를 달아서 써드리겠습니다.
```

지어내기를 멈추는 순간, 출력도 함께 바뀐다 — 일일이 검증해야 하는 초안에서, 그대로 보내도 되는
결과물로. "모델이 썼다"와 "내가 책임질 수 있다"의 차이가 바로 이것이다.

## 설치

### 옵션 1 — Claude Code 플러그인 (권장)

```
/plugin marketplace add https://github.com/plugtheliam/fable-overclock
/plugin install fable-overclock@plugtheliam
```

전체 `https://` URL을 써라. 짧은 `plugtheliam/fable-overclock` 형태로 넣으면 Claude Code가
SSH로 clone을 시도하는데, GitHub SSH 키가 없는 머신에서는 실패한다. 업데이트는
`/plugin marketplace update plugtheliam`, 제거는 `/plugin uninstall fable-overclock@plugtheliam`.

### 옵션 2 — 수동 (어떤 환경이든, stdlib만)

```bash
git clone https://github.com/plugtheliam/fable-overclock && cd fable-overclock
harness/install.sh                 # --global for every project · --uninstall to remove
export MYINC_PROFILE=sonnet        # or opus / deepseek / codex
```

지어낸 숫자, 지금 당장 잡아봐라 — 설치도 API 키도 없이:

```bash
printf 'Revenue grew 38%% last quarter and we added 14,000 users.\n' \
  | python3 harness/gate/refuse.py        # flagged: two figures, no source
```

### 켜고 끄기

게이트는 산문 문서(`.md`, `.txt` 등)만 보고 코드는 건드리지 않는다. 바꾸려면 아무 세션에서나
입력해라:

```
foc off        # 이 프로젝트에서 게이트 일시정지
foc on         # 재개
foc status     # 지금 켜져 있나?
foc off all    # 머신 전체 (아무 명령에나 `all` 추가)
```

또는 `MYINC_GATE=off`. 코드까지 포함해 쓰는 모든 것에 적용하고 싶으면? `MYINC_GATE_ALL=1`.

## 증거

도구에 딸려오는 게이트로 직접 채점한다 — LLM 심판도, 숨은 채점표도 없다. 명령어 하나로 그대로
재현된다: `python3 harness/tests/bench.py`.

| Detection (offline, n=20) | value |  | DeepSeek, OFF → ON | OFF | ON |
|---|---|---|---|---|---|
| made-up claims caught | **100%** |  | figures that carry a source | 4% | **100%** |
| real claims wrongly flagged | **0%** |  | abstains when it can't know | 10/12 | **12/12** |

이 수치는 모델이 얼마나 잘 추론하느냐가 아니라, 어떻게 *행동*하느냐를 잰다 — 적당한 규모(보고
프롬프트 20개 + 알 수 없는 사실 12개), 단일 실행에서. 숫자가 크다는 게 핵심이 아니라, 재현된다는
게 핵심이다. 네 모델로 직접 돌려봐라. 방법론과 한계는 [`docs/BENCHMARK.md`](docs/BENCHMARK.md).

## 다른 도구와 비교하면

|  | fable-overclock | NeMo Guardrails | Guardrails AI | DeepEval |
|---|---|---|---|---|
| Claude Code 안에서 동작 (plugin + hook) | ✅ | ❌ | ❌ | ❌ |
| 의존성 0, 시작에 API 키 불필요 | ✅ | ❌ | ❌ | ❌ |
| 모델별 튜닝 | ✅ | ❌ | ❌ | ❌ |
| 지어내지 말고 보류하라고 모델에 지시 | ✅ | partial | partial | ❌ (eval only) |
| 두 번째 모델이 주장을 교차 검증 | ✅ | ✅ (hallucination rail) | ❌ | ❌ |
| 별도 실행이 아니라 편집하는 동안 동작 | ✅ | ❌ | ❌ | ❌ |

교차 검증 자체는 새로운 게 아니다 — NeMo의 hallucination rail도 이미 두 번째 모델로 주장을
검증한다. 여기서 다른 점은, 전부가 Claude Code 안에 살고, 명령어 하나로 설치되며, 모델별로
튜닝돼 있다는 것이다.

## 못 하는 것

네 모델이 할 수 있는 일의 천장을 올려주지는 않는다. 대신 틀리는 바닥을 낮춘다 — 지어낸 숫자,
출처 없는 주장, 과제를 벗어난 표류. 이런 걸 줄인다. 없애주지는 않는다. 모델 가중치를 바꾸지
않으며, *출처가 달린* 숫자가 정확하다고 보장하지도 못한다 — 출처가 있는지를 확인하고, 나머지는
검증기에 맡긴다. 숫자를 곧이곧대로 믿지 말고, 네 모델로 직접 `harness/tests/bench.py`를 돌려봐라.

## 공개적으로 만든다

수출 규제로 Fable을 잃은 미국 밖의 한 창업가가, 우리처럼 여전히 돌릴 수 있는 모델을 위한 신뢰성
도구를 만든다. X에서 따라와라: [@liampluglab](https://x.com/liampluglab). 매니지드 버전은
[myinc.app](https://myinc.app)에 있다. **myinc-os** 툴킷의 일부다.

## 라이선스

MIT. [`LICENSE`](LICENSE) 참고.
