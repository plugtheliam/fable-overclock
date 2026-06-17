<div align="center">

[English](README.md) · [中文](README.zh.md) · [日本語](README.ja.md) · **Español** · [Deutsch](README.de.md) · [Français](README.fr.md) · [한국어](README.ko.md)

# fable-overclock

## Haz que Opus, Sonnet y DeepSeek rindan a nivel Fable.
### Saca salida de nivel Fable del modelo que aún puedes ejecutar.

Sonnet y DeepSeek se inventan las cifras y se saltan la verificación. Opus sobre-construye y se
aleja de lo que le pediste. fable-overclock arregla el *comportamiento*, no el modelo: los modelos
baratos citan cada cifra y dicen "no lo sé" en lugar de adivinar; Opus hace exactamente lo que
pediste, y luego para. El mismo modelo — con salida que de verdad puedes lanzar. Medido, no
prometido: en DeepSeek, la proporción de cifras que llevan una fuente pasó de **4% a 100%**.

El nombre es literal — como hacer overclock a una CPU, exprime el chip que ya tienes hasta su
límite real, cada vez, por procedimiento y no por suerte. No le sube el coeficiente intelectual al
modelo. Un comando. Solo stdlib. Funciona con el modelo que ya ejecutas.

![MIT](https://img.shields.io/badge/license-MIT-green)
![zero deps](https://img.shields.io/badge/deps-stdlib%20only-brightgreen)
![Claude Code](https://img.shields.io/badge/Claude%20Code-plugin%20%2B%20hook-8A63D2)
![tuned for](https://img.shields.io/badge/tuned-Opus%20%C2%B7%20Sonnet%20%C2%B7%20DeepSeek-orange)
![tests](https://img.shields.io/badge/tests-green-success)

</div>

![fable-overclock señalando una afirmación sin fuente](assets/demo-2x.gif)

## Lo que gana cada modelo

Cada modelo tiene una costumbre cara — una reescritura silenciosa, un número equivocado, una
tarde perdida con una API que nunca existió. fable-overclock conoce cada una y la corta en seco —
y lo demuestra: en las pruebas, la puerta marcó el **100% de los números fabricados con cero falsos positivos**.

| Modelo | La costumbre que te cuesta | Lo que obtienes en su lugar |
|---|---|---|
| **Opus** | sobre-construye, se aleja de lo pedido | exactamente lo que pediste, y luego para — y nombra las opciones más simples que se saltó |
| **Sonnet** | se salta la verificación, suelta sus fuentes | cada cifra citada, cada requisito verificado antes de darlo por terminado |
| **DeepSeek** | inventa números y APIs enteras | `UNKNOWN` en lugar de una mentira segura; un segundo modelo revisa el resto |

Lo logran dos capas. Un **contrato** se carga antes de que el modelo escriba su primer token, así
que la disciplina está ahí desde el principio. Una **puerta** determinista es el respaldo —
puntúa la salida ella misma (sin juez LLM) y atrapa cualquier número sin fuente o inventado antes de que aterrice. La recompensa: salida que no
tienes que verificar línea por línea. Recorrido completo en
[`docs/HOW-IT-WORKS.md`](docs/HOW-IT-WORKS.md).

## Por qué ahora

<!-- FABLE-MOMENT:start — time-bound. Remove when Fable access is restored to non-US founders. -->
En junio de 2026, los controles de exportación de EE. UU. cortaron el acceso a Fable 5 y Mythos 5
de Anthropic para todo extranjero. Si eres un desarrollador fuera de EE. UU., el modelo de
frontera desapareció de tu stack de la noche a la mañana. No puedes recuperarlo. Así que haz que
el modelo que te queda haga trabajo de nivel frontera — medido, no esperado.
<!-- FABLE-MOMENT:end -->

## Compruébalo tú mismo

Mismo modelo, mismo prompt: *"Escribe la actualización para inversores del mes pasado con las
cifras clave."*

**DeepSeek, por su cuenta**
```
Los ingresos crecieron un 38% el trimestre pasado, la cancelación bajó al 2.1% y
sumamos 14,000 usuarios.
```
Seguro de sí mismo. Sin ninguna fuente. Nunca le diste esas cifras — se las inventó. Lanza eso y
el error ahora es tuyo.

**DeepSeek, con fable-overclock**
```
No tengo las cifras del mes pasado (UNKNOWN). Dame los datos de ingresos,
cancelación y usuarios y la escribo — cada número citado a su fuente.
```

En el momento en que deja de adivinar, tu salida cambia con él: de un borrador que tienes que
verificar a algo que puedes enviar tal cual. Esa es la diferencia entre "un modelo escribió esto"
y "respondo por esto".

## Instalación

### Opción 1 — Plugin de Claude Code (recomendado)

```
/plugin marketplace add https://github.com/plugtheliam/fable-overclock
/plugin install fable-overclock@plugtheliam
```

Usa la URL completa `https://`. La forma corta `plugtheliam/fable-overclock` hace que Claude Code
clone por SSH, lo cual falla en máquinas sin una clave SSH de GitHub. Actualiza con
`/plugin marketplace update plugtheliam`, elimina con `/plugin uninstall fable-overclock@plugtheliam`.

### Opción 2 — Manual (cualquier configuración, solo stdlib)

```bash
git clone https://github.com/plugtheliam/fable-overclock && cd fable-overclock
harness/install.sh                 # --global for every project · --uninstall to remove
export MYINC_PROFILE=sonnet        # or opus / deepseek / codex
```

Atrapa un número inventado ahora mismo — sin instalar, sin clave de API:

```bash
printf 'Revenue grew 38%% last quarter and we added 14,000 users.\n' \
  | python3 harness/gate/refuse.py        # flagged: two figures, no source
```

### Enciéndelo o apágalo

La puerta revisa tu prosa (`.md`, `.txt`, …) y deja el código en paz. Para cambiar eso, escribe en
cualquier sesión:

```
foc off        # pause the gate for this project
foc on         # resume
foc status     # is it on?
foc off all    # machine-wide (add `all` to any command)
```

O define `MYINC_GATE=off`. ¿Lo quieres en *todo* lo que escribes, código incluido? `MYINC_GATE_ALL=1`.

## La prueba

Puntuado por la puerta que trae la herramienta — sin juez LLM, sin rúbrica oculta. Reprodúcelo con
un comando: `python3 harness/tests/bench.py`.

| Detección (offline, n=20) | valor |  | DeepSeek, OFF → ON | OFF | ON |
|---|---|---|---|---|---|
| afirmaciones inventadas atrapadas | **100%** |  | cifras que llevan fuente | 4% | **100%** |
| afirmaciones reales mal señaladas | **0%** |  | se abstiene cuando no puede saberlo | 10/12 | **12/12** |

Esto mide cómo se *comporta* el modelo, no qué tan bien razona — sobre un conjunto modesto (20 prompts de informe + 12 prompts de hechos imposibles de saber), una sola corrida. Lo importante no es que las cifras sean enormes, sino que son reproducibles. Córrelo en tu propio modelo. Método y advertencias:
[`docs/BENCHMARK.md`](docs/BENCHMARK.md).

## Cómo se compara

|  | fable-overclock | NeMo Guardrails | Guardrails AI | DeepEval |
|---|---|---|---|---|
| Corre dentro de Claude Code (plugin + hook) | ✅ | ❌ | ❌ | ❌ |
| Cero dependencias, sin clave de API para empezar | ✅ | ❌ | ❌ | ❌ |
| Ajustado por modelo | ✅ | ❌ | ❌ | ❌ |
| Le dice al modelo que se abstenga, no que invente | ✅ | partial | partial | ❌ (eval only) |
| Un segundo modelo verifica las afirmaciones | ✅ | ✅ (hallucination rail) | ❌ | ❌ |
| Funciona mientras editas, no como una corrida aparte | ✅ | ❌ | ❌ | ❌ |

La verificación cruzada no es nueva — el rail de alucinación de NeMo ya verifica afirmaciones con
un segundo modelo. Lo distinto aquí: vive dentro de Claude Code, se instala con un comando, y está
ajustado por modelo.

## Lo que no hace

No subirá el techo de lo que tu modelo puede hacer. Baja el suelo de lo que hace mal: números
inventados, afirmaciones sin fuente, desvío de la tarea. Reduce eso. No lo borra. No cambia los
pesos del modelo, y no puede prometer que un número *citado* sea correcto — verifica que haya una
fuente y deja que el verificador haga el resto. No te fíes de las cifras a ciegas; corre
`harness/tests/bench.py` en tu propio modelo.

## Construido en público

Por un fundador fuera de EE. UU. que perdió Fable por los controles de exportación y construye
herramientas de fiabilidad para los modelos que los demás aún podemos ejecutar. Sígueme en X:
[@liampluglab](https://x.com/liampluglab). Hay una versión gestionada en
[myinc.app](https://myinc.app). Parte del kit **myinc-os**.

## Licencia

MIT. Mira [`LICENSE`](LICENSE).
