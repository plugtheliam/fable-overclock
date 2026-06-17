<div align="center">

[English](README.md) · [中文](README.zh.md) · [日本語](README.ja.md) · [Español](README.es.md) · [Deutsch](README.de.md) · **Français** · [한국어](README.ko.md)

# fable-overclock

## Faites tourner Opus, Sonnet et DeepSeek au niveau de Fable.
### Tirez du niveau Fable du modèle qui vous reste.

Sonnet et DeepSeek
inventent des chiffres et zappent la vérification. Opus en fait trop et dérive bien au-delà de
votre demande. fable-overclock corrige le *comportement*, pas le modèle : les modèles bon marché sourcent
chaque chiffre et disent « je ne sais pas » au lieu de deviner ; Opus fait exactement ce que
vous avez demandé, puis s'arrête. Même modèle — un rendu que vous pouvez vraiment livrer.
Mesuré, pas promis : sur DeepSeek, la part des chiffres accompagnés d'une source est passée de **4% à 100%**.

Le nom est à prendre au pied de la lettre — comme l'overclocking d'un CPU, il pousse la puce que vous avez déjà jusqu'à sa vraie limite, à chaque fois, par méthode et non par chance. Ça n'augmente pas le QI brut d'un modèle. Une seule commande. stdlib uniquement. Fonctionne avec
le modèle que vous utilisez déjà.

![MIT](https://img.shields.io/badge/license-MIT-green)
![zero deps](https://img.shields.io/badge/deps-stdlib%20only-brightgreen)
![Claude Code](https://img.shields.io/badge/Claude%20Code-plugin%20%2B%20hook-8A63D2)
![tuned for](https://img.shields.io/badge/tuned-Opus%20%C2%B7%20Sonnet%20%C2%B7%20DeepSeek-orange)
![tests](https://img.shields.io/badge/tests-green-success)

</div>

![fable-overclock flagging a claim with no source](assets/demo-2x.gif)

## Ce que chaque modèle y gagne

Chaque modèle a une habitude qui coûte cher — une réécriture silencieuse, un chiffre faux, un
après-midi perdu à cause d'une API qui n'a jamais existé. fable-overclock connaît chacune
d'elles et les coupe net — et le prouve : lors des tests, le gate a signalé **100% des chiffres fabriqués, avec zéro faux positif**.

| Modèle | L'habitude qui vous coûte | Ce que vous obtenez à la place |
|---|---|---|
| **Opus** | en fait trop, dérive au-delà de la demande | exactement ce que vous avez demandé, puis il s'arrête — et il nomme les options plus simples qu'il a écartées |
| **Sonnet** | zappe la vérif, perd ses sources | chaque chiffre sourcé, chaque exigence vérifiée avant qu'il ne déclare le travail fini |
| **DeepSeek** | invente des chiffres et des APIs entières | `UNKNOWN` au lieu d'un mensonge assuré ; un second modèle revérifie le reste |

Deux couches s'en chargent. Un **contrat** se charge avant que le modèle n'écrive son premier
token, pour que la discipline soit là dès le départ. Un **gate** déterministe est le filet de
sécurité — il note la sortie lui-même (sans juge LLM) et attrape tout chiffre non sourcé ou inventé avant qu'il n'atterrisse. Le gain : un
rendu que vous n'avez pas à vérifier ligne par ligne. Explication complète dans
[`docs/HOW-IT-WORKS.md`](docs/HOW-IT-WORKS.md).

## Pourquoi maintenant

<!-- FABLE-MOMENT:start — time-bound. Remove when Fable access is restored to non-US founders. -->
En juin 2026, les contrôles à l'exportation américains ont coupé l'accès aux Fable 5 et Mythos 5
d'Anthropic pour tout ressortissant étranger. Si vous êtes un développeur hors États-Unis, le
modèle de pointe a disparu de votre stack du jour au lendemain. Impossible de le récupérer. Alors faites faire au modèle qui vous reste un travail de pointe — mesuré, pas espéré.
<!-- FABLE-MOMENT:end -->

## Voyez par vous-même

Même modèle, même prompt : *« Rédige le compte-rendu investisseurs du mois dernier avec les chiffres clés. »*

**DeepSeek, livré à lui-même**
```
Revenue grew 38% last quarter, churn fell to 2.1%, and we added 14,000 users.
```
Assuré. Sourcé par rien. Vous ne lui avez jamais donné ces chiffres — il les a inventés.
Livrez ça et l'erreur est désormais la vôtre.

**DeepSeek, sous fable-overclock**
```
I don't have last month's figures (UNKNOWN). Give me revenue, churn, and user
data and I'll write it — each number cited to its source.
```

Dès l'instant où il cesse de deviner, votre rendu change avec lui : d'un brouillon que vous
devez vérifier, à quelque chose que vous pouvez envoyer tel quel. C'est toute la différence
entre « un modèle a écrit ça » et « je peux en répondre ».

## Installation

### Option 1 — plugin Claude Code (recommandé)

```
/plugin marketplace add https://github.com/plugtheliam/fable-overclock
/plugin install fable-overclock@plugtheliam
```

Utilisez l'URL `https://` complète. La forme courte `plugtheliam/fable-overclock` pousse Claude
Code à cloner via SSH, ce qui échoue sur les machines sans clé SSH GitHub. Mettez à jour avec
`/plugin marketplace update plugtheliam`, retirez avec `/plugin uninstall fable-overclock@plugtheliam`.

### Option 2 — manuelle (n'importe quelle config, stdlib uniquement)

```bash
git clone https://github.com/plugtheliam/fable-overclock && cd fable-overclock
harness/install.sh                 # --global for every project · --uninstall to remove
export MYINC_PROFILE=sonnet        # or opus / deepseek / codex
```

Attrapez un chiffre inventé tout de suite — sans installation, sans clé API :

```bash
printf 'Revenue grew 38%% last quarter and we added 14,000 users.\n' \
  | python3 harness/gate/refuse.py        # flagged: two figures, no source
```

### Activez-le ou désactivez-le

Le gate vérifie votre prose (`.md`, `.txt`, …) et laisse le code tranquille. Pour changer ça,
tapez dans n'importe quelle session :

```
foc off        # pause the gate for this project
foc on         # resume
foc status     # is it on?
foc off all    # machine-wide (add `all` to any command)
```

Ou définissez `MYINC_GATE=off`. Vous le voulez sur *tout* ce que vous écrivez, code compris ?
`MYINC_GATE_ALL=1`.

## La preuve

Noté par le gate que l'outil embarque — pas de juge LLM, pas de barème caché. Reproduisez-le
avec une seule commande : `python3 harness/tests/bench.py`.

| Détection (hors ligne, n=20) | valeur |  | DeepSeek, OFF → ON | OFF | ON |
|---|---|---|---|---|---|
| affirmations inventées attrapées | **100%** |  | chiffres qui portent une source | 4% | **100%** |
| affirmations réelles signalées à tort | **0%** |  | s'abstient quand il ne peut pas savoir | 10/12 | **12/12** |

Ces mesures concernent la façon dont le modèle se *comporte*, pas sa qualité de raisonnement — sur un ensemble modeste (20 prompts de rapport + 12 prompts de faits impossibles à connaître), une seule exécution. L'important n'est pas que les chiffres soient énormes, mais qu'ils soient reproductibles. Lancez-le sur votre propre modèle.
Méthode et réserves : [`docs/BENCHMARK.md`](docs/BENCHMARK.md).

## Comment ça se compare

|  | fable-overclock | NeMo Guardrails | Guardrails AI | DeepEval |
|---|---|---|---|---|
| Tourne à l'intérieur de Claude Code (plugin + hook) | ✅ | ❌ | ❌ | ❌ |
| Zéro dépendance, aucune clé API pour démarrer | ✅ | ❌ | ❌ | ❌ |
| Calibré par modèle | ✅ | ❌ | ❌ | ❌ |
| Dit au modèle de s'abstenir, pas d'inventer | ✅ | partial | partial | ❌ (eval only) |
| Un second modèle recoupe les affirmations | ✅ | ✅ (hallucination rail) | ❌ | ❌ |
| Fonctionne pendant que vous éditez, pas en passe séparée | ✅ | ❌ | ❌ | ❌ |

Le recoupement n'est pas neuf — le rail anti-hallucination de NeMo vérifie déjà les
affirmations avec un second modèle. Ce qui change ici : ça vit à l'intérieur de Claude Code,
s'installe en une seule commande, et est calibré par modèle.

## Ce qu'il ne fait pas

Il ne relèvera pas le plafond de ce que votre modèle sait faire. Il abaisse le plancher de ce
qu'il rate : chiffres inventés, affirmations non sourcées, dérive hors du sujet. Il réduit ces
erreurs. Il ne les efface pas. Il ne change pas les poids du modèle, et il ne peut pas garantir
qu'un chiffre *cité* est correct — il vérifie qu'une source est là et laisse le vérificateur
faire le reste. Ne prenez pas les chiffres pour argent comptant ; lancez
`harness/tests/bench.py` sur votre propre modèle.

## Construit en public

Par un fondateur hors États-Unis qui a perdu Fable à cause des contrôles à l'exportation et qui
bâtit des outils de fiabilité pour les modèles qu'il nous reste à tous. Suivez ça sur X :
[@liampluglab](https://x.com/liampluglab). Une version managée vit sur
[myinc.app](https://myinc.app). Fait partie de la boîte à outils **myinc-os**.

## Licence

MIT. Voir [`LICENSE`](LICENSE).
