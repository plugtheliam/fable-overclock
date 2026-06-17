<div align="center">

[English](README.md) · [中文](README.zh.md) · **日本語** · [Español](README.es.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [한국어](README.ko.md)

# fable-overclock

## Opus も Sonnet も DeepSeek も、Fable 級で走らせる。
### いま手元で動くモデルから Fable 級の出力を引き出す。

Sonnet も DeepSeek も数字を勝手にでっち上げ、
確認を飛ばす。Opus は作り込みすぎて、頼んだ範囲を踏み越えていく。fable-overclock が直すのは
モデルではなく、その*振る舞い*だ。安いモデルはすべての数値に出典を付け、当て推量の代わりに「わからない」と言う。
Opus は頼んだことだけをやって、そこで止まる。同じモデルで、そのまま出せる出力に変わる。
口約束ではなく実測だ——DeepSeek では、出典付きの数値の割合が **4% から 100% へ** 上がった。

名前のとおりだ——CPU のオーバークロックのように、運任せではなく手順によって、すでに手元にあるチップを毎回その本当の限界まで押し上げる。モデルの素のIQを上げるわけではない。コマンドひとつ。stdlib のみ。いま使っているモデルでそのまま動く。

![MIT](https://img.shields.io/badge/license-MIT-green)
![zero deps](https://img.shields.io/badge/deps-stdlib%20only-brightgreen)
![Claude Code](https://img.shields.io/badge/Claude%20Code-plugin%20%2B%20hook-8A63D2)
![tuned for](https://img.shields.io/badge/tuned-Opus%20%C2%B7%20Sonnet%20%C2%B7%20DeepSeek-orange)
![tests](https://img.shields.io/badge/tests-green-success)

</div>

![fable-overclock flagging a claim with no source](assets/demo-2x.gif)

## モデルごとに、得られるもの

どのモデルにも、高くつく癖がひとつある——黙ったままの書き換え、間違った数字、存在しないAPIに費やす午後。
fable-overclock はそれぞれの癖を知り尽くして、封じ込める。——しかも証明できる:テストでは、ゲートがでっち上げの数字を **100% 捕捉し、誤検知はゼロ** だった。

| モデル | あなたの時間を奪う癖 | 代わりに手に入るもの |
|---|---|---|
| **Opus** | 作り込みすぎ、頼んだ範囲を踏み越える | 頼んだことだけをやって、そこで止まる——そして見送ったより簡単な選択肢を名指しする |
| **Sonnet** | 確認を飛ばし、出典を落とす | すべての数値に出典、完了と言う前にすべての要件を検証 |
| **DeepSeek** | 数字もAPIまるごともでっち上げる | 自信たっぷりの嘘の代わりに `UNKNOWN`。残りは二つ目のモデルが裏取りする |

これを支えるのは二層構造だ。モデルが最初のトークンを書く前に**契約**が読み込まれ、規律は最初から
そこにある。決定論的な**ゲート**が最後の砦——出力自体を採点し(LLM 審判なし)、出典のない数字やでっち上げの数字を、着地する前に
すべて捕まえる。見返りは、一行ずつファクトチェックしなくていい出力だ。詳しい解説は
[`docs/HOW-IT-WORKS.md`](docs/HOW-IT-WORKS.md) に。

## なぜ、いまなのか

<!-- FABLE-MOMENT:start — time-bound. Remove when Fable access is restored to non-US founders. -->
2026年6月、米国の輸出規制が Anthropic の Fable 5 と Mythos 5 をすべての外国人から遮断した。
あなたが米国外の開発者なら、フロンティアモデルは一夜にしてスタックから消えた。取り戻すことはできない
——なら、手元に残ったモデルにフロンティア級の仕事をさせればいい。願望ではなく、実測で。
<!-- FABLE-MOMENT:end -->

## 自分の目で確かめる

同じモデル、同じプロンプト:*「先月の投資家向けアップデートを、主要な数字を入れて書いて。」*

**DeepSeek、素のまま**
```
Revenue grew 38% last quarter, churn fell to 2.1%, and we added 14,000 users.
```
自信満々。だが出典はゼロ。その数字をあなたは一度も渡していない——でっち上げたのだ。それをそのまま
出せば、ミスはもうあなたのものだ。

**DeepSeek、fable-overclock 上**
```
先月の数字は持っていません(UNKNOWN)。売上・チャーン・ユーザーのデータをください。
それぞれの数値を出典付きで明記して書きます。
```

当て推量をやめた瞬間、あなたの出力も一緒に変わる——ファクトチェックの要るドラフトから、そのまま
送れるものへ。「モデルが書いた」と「自分が責任を持てる」の差は、ここにある。

## インストール

### 方法1 — Claude Code プラグイン(推奨)

```
/plugin marketplace add https://github.com/plugtheliam/fable-overclock
/plugin install fable-overclock@plugtheliam
```

`https://` 付きのフルURLを使うこと。短い `plugtheliam/fable-overclock` 形式だと Claude Code が
SSH でクローンしようとして、GitHub の SSH キーがないマシンでは失敗する。更新は
`/plugin marketplace update plugtheliam`、削除は `/plugin uninstall fable-overclock@plugtheliam` で。

### 方法2 — 手動(どんな環境でも、stdlib のみ)

```bash
git clone https://github.com/plugtheliam/fable-overclock && cd fable-overclock
harness/install.sh                 # --global for every project · --uninstall to remove
export MYINC_PROFILE=sonnet        # or opus / deepseek / codex
```

でっち上げの数字を、いますぐ捕まえる——インストール不要、APIキー不要:

```bash
printf 'Revenue grew 38%% last quarter and we added 14,000 users.\n' \
  | python3 harness/gate/refuse.py        # flagged: two figures, no source
```

### オン・オフの切り替え

ゲートが見るのは散文(`.md`、`.txt`、…)で、コードには手を出さない。これを変えたければ、どの
セッションでも次のように打つ:

```
foc off        # pause the gate for this project
foc on         # resume
foc status     # is it on?
foc off all    # machine-wide (add `all` to any command)
```

または `MYINC_GATE=off` を設定する。コードも含めて書くもの*すべて*に効かせたい?なら `MYINC_GATE_ALL=1`。

## 証拠

評価は、このツールに同梱されたゲート自身が採点——LLM 審判もなければ、隠された採点基準もない。
コマンドひとつで再現できる:`python3 harness/tests/bench.py`。

| 検出(オフライン, n=20) | 値 |  | DeepSeek, OFF → ON | OFF | ON |
|---|---|---|---|---|---|
| でっち上げの主張を捕捉 | **100%** |  | 出典を伴う数値 | 4% | **100%** |
| 本物の主張を誤検知 | **0%** |  | 知り得ないときは断る | 10/12 | **12/12** |

これらが測るのはモデルの*振る舞い*であって、推論の出来ではない——適度な規模(レポート用プロンプト20件＋知り得ない事実のプロンプト12件)、単一の実行で。数字が大きいことではなく、再現できることが要点だ。自分のモデルで回してみてほしい。手法と注意点は
[`docs/BENCHMARK.md`](docs/BENCHMARK.md) に。

## ほかとの違い

|  | fable-overclock | NeMo Guardrails | Guardrails AI | DeepEval |
|---|---|---|---|---|
| Claude Code の中で動く(plugin + hook) | ✅ | ❌ | ❌ | ❌ |
| 依存ゼロ、開始にAPIキー不要 | ✅ | ❌ | ❌ | ❌ |
| モデルごとにチューニング | ✅ | ❌ | ❌ | ❌ |
| でっち上げではなく断れとモデルに指示 | ✅ | partial | partial | ❌ (eval only) |
| 二つ目のモデルが主張を相互チェック | ✅ | ✅ (hallucination rail) | ❌ | ❌ |
| 別実行ではなく、編集しながら効く | ✅ | ❌ | ❌ | ❌ |

相互チェック自体は新しくない——NeMo の hallucination rail はすでに二つ目のモデルで主張を検証する。
ここで違うのは、それが Claude Code の中に住み、コマンドひとつで入り、モデルごとにチューニング
されていることだ。

## やらないこと

モデルにできることの天井は上げない。下げるのは、間違える床のほうだ——でっち上げの数字、出典のない
主張、タスクからの逸脱。これらを減らす。消し去りはしない。モデルの重みを書き換えることもないし、
*出典付き*の数字が正しいと保証することもできない——出典が存在することを確認し、あとは検証側に
任せる。数字を鵜呑みにせず、自分のモデルで `harness/tests/bench.py` を回してほしい。

## 公開の場で作っている

輸出規制で Fable を失った米国外のファウンダーが、残された私たちが回せるモデルのための信頼性ツールを
作っている。X でフォローを:[@liampluglab](https://x.com/liampluglab)。マネージド版は
[myinc.app](https://myinc.app) に。**myinc-os** ツールキットの一部。

## ライセンス

MIT。[`LICENSE`](LICENSE) を参照。
