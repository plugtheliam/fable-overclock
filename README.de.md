<div align="center">

[English](README.md) · [中文](README.zh.md) · [日本語](README.ja.md) · [Español](README.es.md) · **Deutsch** · [Français](README.fr.md) · [한국어](README.ko.md)

# fable-overclock

## Lass Opus, Sonnet und DeepSeek auf Fable-Niveau laufen.
### Hol dir Fable-Output aus dem Modell, das dir bleibt.

Sonnet und DeepSeek erfinden
Zahlen und überspringen die Prüfung. Opus baut zu viel und treibt am Auftrag vorbei.
fable-overclock korrigiert das *Verhalten*, nicht das Modell: Die günstigen Modelle belegen jede Zahl mit einer
Quelle und sagen „ich weiß es nicht" statt zu raten; Opus tut genau das, worum du gebeten hast,
und hört dann auf. Gleiches Modell — Output, den du wirklich ausliefern kannst.
Gemessen, nicht versprochen: Bei DeepSeek stieg der Anteil der Zahlen mit Quelle von **4% auf 100%**.

Der Name ist wörtlich gemeint — wie beim Übertakten einer CPU wird der Chip, den du schon hast, jedes Mal an sein echtes Limit getrieben, durch Verfahren statt durch Glück. Es hebt nicht den Roh-IQ eines Modells. Ein Befehl. Nur stdlib. Funktioniert
mit dem Modell, das du ohnehin schon laufen lässt.

![MIT](https://img.shields.io/badge/license-MIT-green)
![zero deps](https://img.shields.io/badge/deps-stdlib%20only-brightgreen)
![Claude Code](https://img.shields.io/badge/Claude%20Code-plugin%20%2B%20hook-8A63D2)
![tuned for](https://img.shields.io/badge/tuned-Opus%20%C2%B7%20Sonnet%20%C2%B7%20DeepSeek-orange)
![tests](https://img.shields.io/badge/tests-green-success)

</div>

![fable-overclock flagging a claim with no source](assets/demo-2x.gif)

## Was jedes Modell gewinnt

Jedes Modell hat eine teure Angewohnheit — ein stilles Umschreiben, eine falsche Zahl, ein
verlorener Nachmittag wegen einer API, die es nie gab. fable-overclock kennt jede einzelne und
schaltet sie ab — und beweist es: Im Test markierte das Gate **100% der erfundenen Zahlen, bei null Fehlalarmen**.

| Modell | Die Angewohnheit, die dich teuer zu stehen kommt | Was du stattdessen bekommst |
|---|---|---|
| **Opus** | baut zu viel, treibt am Auftrag vorbei | genau das, worum du gebeten hast, dann stoppt es — und nennt die einfacheren Optionen, die es ausgelassen hat |
| **Sonnet** | überspringt die Prüfung, verliert seine Quellen | jede Zahl belegt, jede Anforderung verifiziert, bevor es „fertig" sagt |
| **DeepSeek** | erfindet Zahlen und ganze APIs | `UNKNOWN` statt einer selbstbewussten Lüge; ein zweites Modell prüft den Rest gegen |

Zwei Schichten erledigen das. Ein **Vertrag** wird geladen, bevor das Modell sein erstes Token
schreibt — so ist die Disziplin von Anfang an da. Ein deterministisches **Gate** ist das
Sicherheitsnetz — es bewertet die Ausgabe selbst (kein LLM-Judge) und fängt jede unbelegte oder erfundene Zahl ab, bevor sie landet. Der Lohn:
Output, den du nicht Zeile für Zeile faktenchecken musst. Komplette Tour in
[`docs/HOW-IT-WORKS.md`](docs/HOW-IT-WORKS.md).

## Warum gerade jetzt

<!-- FABLE-MOMENT:start — time-bound. Remove when Fable access is restored to non-US founders. -->
Im Juni 2026 kappten US-Exportkontrollen Anthropics Fable 5 und Mythos 5 für jeden ausländischen
Staatsbürger. Wenn du als Entwickler außerhalb der USA arbeitest, ist das Frontier-Modell über
Nacht aus deinem Stack verschwunden. Du kannst es nicht zurückbekommen. Also bring das Modell, das dir
bleibt, dazu, Frontier-Arbeit zu leisten — gemessen, nicht erhofft.
<!-- FABLE-MOMENT:end -->

## Sieh es dir selbst an

Gleiches Modell, gleicher Prompt: *„Schreib das Investoren-Update vom letzten Monat mit den
wichtigsten Zahlen."*

**DeepSeek, auf sich allein gestellt**
```
Revenue grew 38% last quarter, churn fell to 2.1%, and we added 14,000 users.
```
Selbstbewusst. Durch nichts belegt. Du hast ihm diese Zahlen nie gegeben — es hat sie erfunden.
Liefere das aus, und der Fehler gehört jetzt dir.

**DeepSeek, mit fable-overclock**
```
I don't have last month's figures (UNKNOWN). Give me revenue, churn, and user
data and I'll write it — each number cited to its source.
```

In dem Moment, in dem es aufhört zu raten, ändert sich dein Output mit: von einem Entwurf, den du
faktenchecken musst, zu etwas, das du so wie es ist verschicken kannst. Das ist der Unterschied
zwischen „ein Modell hat das geschrieben" und „dahinter kann ich stehen".

## Installation

### Option 1 — Claude Code Plugin (empfohlen)

```
/plugin marketplace add https://github.com/plugtheliam/fable-overclock
/plugin install fable-overclock@plugtheliam
```

Nimm die vollständige `https://`-URL. Die Kurzform `plugtheliam/fable-overclock` bringt Claude Code
dazu, über SSH zu klonen, was auf Maschinen ohne GitHub-SSH-Key fehlschlägt. Aktualisieren mit
`/plugin marketplace update plugtheliam`, entfernen mit `/plugin uninstall fable-overclock@plugtheliam`.

### Option 2 — Manuell (jedes Setup, nur stdlib)

```bash
git clone https://github.com/plugtheliam/fable-overclock && cd fable-overclock
harness/install.sh                 # --global for every project · --uninstall to remove
export MYINC_PROFILE=sonnet        # or opus / deepseek / codex
```

Schnapp dir jetzt sofort eine erfundene Zahl — ohne Installation, ohne API-Key:

```bash
printf 'Revenue grew 38%% last quarter and we added 14,000 users.\n' \
  | python3 harness/gate/refuse.py        # flagged: two figures, no source
```

### Ein- oder ausschalten

Das Gate prüft deine Prosa (`.md`, `.txt`, …) und lässt Code in Ruhe. Um das zu ändern, tippe in
einer beliebigen Session:

```
foc off        # pause the gate for this project
foc on         # resume
foc status     # is it on?
foc off all    # machine-wide (add `all` to any command)
```

Oder setze `MYINC_GATE=off`. Du willst es bei *allem*, was du schreibst, inklusive Code?
`MYINC_GATE_ALL=1`.

## Der Beweis

Bewertet vom Gate, das das Tool mitliefert — kein LLM-Richter, kein verstecktes Punkteschema.
Reproduzierbar mit einem Befehl: `python3 harness/tests/bench.py`.

| Detection (offline, n=20) | value |  | DeepSeek, OFF → ON | OFF | ON |
|---|---|---|---|---|---|
| made-up claims caught | **100%** |  | figures that carry a source | 4% | **100%** |
| real claims wrongly flagged | **0%** |  | abstains when it can't know | 10/12 | **12/12** |

Diese messen, wie sich das Modell *verhält*, nicht wie gut es schlussfolgert — an einem überschaubaren Satz (20 Report-Prompts + 12 Prompts zu nicht wissbaren Fakten), ein einziger Lauf. Der Punkt ist nicht, dass die Zahlen riesig sind, sondern dass sie reproduzierbar sind. Lass es auf deinem eigenen Modell laufen. Methode und
Vorbehalte: [`docs/BENCHMARK.md`](docs/BENCHMARK.md).

## Im Vergleich

|  | fable-overclock | NeMo Guardrails | Guardrails AI | DeepEval |
|---|---|---|---|---|
| Läuft in Claude Code (Plugin + Hook) | ✅ | ❌ | ❌ | ❌ |
| Null Abhängigkeiten, kein API-Key zum Start | ✅ | ❌ | ❌ | ❌ |
| Pro Modell abgestimmt | ✅ | ❌ | ❌ | ❌ |
| Sagt dem Modell, es soll sich enthalten, nicht erfinden | ✅ | partial | partial | ❌ (eval only) |
| Zweites Modell prüft Behauptungen gegen | ✅ | ✅ (hallucination rail) | ❌ | ❌ |
| Funktioniert beim Editieren, nicht als separater Lauf | ✅ | ❌ | ❌ | ❌ |

Der Gegencheck ist nicht neu — NeMos Halluzinations-Rail verifiziert Behauptungen längst mit einem
zweiten Modell. Was hier anders ist: Es lebt in Claude Code, installiert sich mit einem Befehl und
ist pro Modell abgestimmt.

## Was es nicht tut

Es hebt nicht die Decke dessen, was dein Modell kann. Es senkt den Boden dessen, was es falsch
macht: erfundene Zahlen, unbelegte Behauptungen, Abdriften vom Auftrag. Es reduziert das. Es löscht
es nicht aus. Es ändert keine Modellgewichte, und es kann nicht versprechen, dass eine *belegte*
Zahl korrekt ist — es prüft, dass eine Quelle da ist, und überlässt den Rest dem Verifizierer.
Nimm die Zahlen nicht auf Treu und Glauben; lass `harness/tests/bench.py` auf deinem eigenen Modell
laufen.

## In der Öffentlichkeit gebaut

Von einem Gründer außerhalb der USA, der Fable an Exportkontrollen verloren hat und
Zuverlässigkeits-Tools für die Modelle baut, die uns anderen bleiben. Folge mit auf X:
[@liampluglab](https://x.com/liampluglab). Eine gehostete Version gibt es unter
[myinc.app](https://myinc.app). Teil des **myinc-os**-Toolkits.

## Lizenz

MIT. Siehe [`LICENSE`](LICENSE).
