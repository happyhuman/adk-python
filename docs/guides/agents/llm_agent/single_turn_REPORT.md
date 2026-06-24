# 🔬 ADK Markdown Snippet Verification Report

* **Source File**: [single_turn.md](file:///Users/shahins/projects/mine/adk-python/docs/guides/agents/llm_agent/single_turn.md)
* **Verified On**: `2026-06-23 19:02:40`

## 📈 Executive Summary

| Snippet | Preceding Heading | Load Phase | Run Phase | Coverage | Details |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Snippet 1** | `Example` | ❌ **FAIL** | ➖ **SKIPPED** | — | `ImportError: cannot import name 'build_node' from 'google.adk.workflow' (/Users/shahins/projects/mine/adk-python/src/google/adk/workflow/__init__.py)` |
| **Snippet 2** | `Example` | ✅ **PASS** | ✅ **PASS** | `100` | All checks passed successfully. |
| **Snippet 3** | `Context-Aware Sub-Agent Example` | ❌ **FAIL** | ➖ **SKIPPED** | — | `NameError: name 'LlmAgent' is not defined` |

---

## 🔍 Detailed Snippet Reports

### ❌ Snippet 1: `Example`

#### 📝 Code Block
```python
from google.adk.agents import LlmAgent
from google.adk.workflow import Workflow, build_node

# Defaults to mode="single_turn" when run as a node
writer_agent = LlmAgent(
    name="writer",
    instruction="Write a short story about the input topic."
)

writer_node = build_node(writer_agent)

wf = Workflow(
    name="story_generator",
    edges=[
        ("START", writer_node),
        (writer_node, "END")
    ]
)
```

#### 🖥️ Loadability & Runnability Logs
```
🔬 Testing file: snippet_1_example.py
============================================================
📋 Phase 1: Loading & Compiling...
❌ Load Failure: Failed to compile/load 'snippet_1_example.py':
------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/shahins/projects/mine/adk-python/.agents/skills/adk-verify-snippets/scripts/run.py", line 206, in main
    module = load_target_module(file_path)
  File "/Users/shahins/projects/mine/adk-python/.agents/skills/adk-verify-snippets/scripts/run.py", line 52, in load_target_module
    spec.loader.exec_module(module)
    ~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^
  File "<frozen importlib._bootstrap_external>", line 762, in exec_module
  File "<frozen importlib._bootstrap>", line 491, in _call_with_frames_removed
  File "/private/var/folders/cm/82x0j39d2076xcfjpm5qcxxr00gp60/T/verify_snippets_09387wsx/snippet_1_example.py", line 2, in <module>
    from google.adk.workflow import Workflow, build_node
ImportError: cannot import name 'build_node' from 'google.adk.workflow' (/Users/shahins/projects/mine/adk-python/src/google/adk/workflow/__init__.py)
------------------------------------------------------------
```

#### 📊 Coverage Report
```
📊 Phase 4: Code Coverage Report (Target File)
============================================================
Name                                                                                                     Stmts   Miss Branch BrPart  Cover
------------------------------------------------------------------------------------------------------------------------------------------
/private/var/folders/cm/82x0j39d2076xcfjpm5qcxxr00gp60/T/verify_snippets_09387wsx/snippet_1_example.py       5      3      0      0    40%
------------------------------------------------------------------------------------------------------------------------------------------
TOTAL                                                                                                        5      3      0      0    40%
============================================================

```

---

### ✅ Snippet 2: `Example`

#### 📝 Code Block
```python
from google.adk.agents import LlmAgent

# Define a specialized single-turn sub-agent
translator_agent = LlmAgent(
    name="translator",
    instruction="Translate the input text to Spanish.",
    mode="single_turn"  # Must be explicit if not auto-wrapped in workflow
)

# Define the parent agent and assign the sub-agent
bilingual_writer = LlmAgent(
    name="bilingual_writer",
    instruction="Write a poem about the topic, then use the translator tool to translate it.",
    sub_agents=[translator_agent] # Exposes 'translator' as a tool to bilingual_writer
)
```

#### 🖥️ Loadability & Runnability Logs
```
🔬 Testing file: snippet_2_example.py
============================================================
📋 Phase 1: Loading & Compiling...
✅ Load Success: 'snippet_2_example.py' compiled and loaded without any issues.

📋 Phase 2: Component Discovery...

📋 Phase 3: Executing Agent...

🔍 Discovered ADK Agent in target file.
🚀 Running execution test with input: 'Test input topic'...

🎬 [Event] Author: bilingual_writer
📝 Content Output:
----------------------------------------
### Test Input

A lonely string of text arrives,
To see if the machine survives.
A test input, a simple key,
To unlock what the code might be.

Through functions, loops, and logic gates,
It travels where the program waits.
Will it pass, or will it break?
What difference will a symbol make?

A gentle pulse, a quiet spark,
A guiding light within the dark.
The test succeeds, the output clear,
No bugs to find, no faults to fear.

***

Now, translating this poem into Spanish...
----------------------------------------
🎬 [Event] Author: translator
🎬 [Event] Author: translator
🎬 [Event] Author: bilingual_writer
📝 Content Output:
----------------------------------------
Aquí tienes la traducción del poema al español:

### Entrada de Prueba

Una solitaria cadena de texto llega,
Para ver si la máquina sobrevive.
Una entrada de prueba, una simple clave,
Para desbloquear lo que el código podría ser.

A través de funciones, bucles y puertas lógicas,
Viaja hacia donde el programa espera.
¿Pasará, o se romperá?
¿Qué diferencia hará un símbolo?

Un suave pulso, una chispa silenciosa,
Una luz guía en la oscuridad.
La prueba tiene éxito, el resultado es claro,
Sin errores que encontrar, ni fallos que temer.
----------------------------------------
🎬 [Event] Author: bilingual_writer
🎬 [Event] Author: bilingual_writer
📝 Content Output:
----------------------------------------
Here is the translation of the poem:

### Entrada de Prueba

Una solitaria cadena de texto llega,
Para ver si la máquina sobrevive.
Una entrada de prueba, una simple clave,
Para desbloquear lo que el código podría ser.

A través de funciones, bucles y puertas lógicas,
Viaja hacia donde el programa espera.
¿Pasará, o se romperá?
¿Qué diferencia hará un símbolo?

Un suave pulso, una chispa silenciosa,
Una luz guía en la oscuridad.
La prueba tiene éxito, el resultado es claro,
Sin errores que encontrar, ni fallos que temer.
----------------------------------------

✅ Run Success: Component 'Agent' executed successfully.

=== STDERR/TRACEBACK ===
/Users/shahins/projects/mine/adk-python/src/google/adk/models/llm_request.py:256: UserWarning: [EXPERIMENTAL] feature FeatureName.JSON_SCHEMA_FOR_FUNC_DECL is enabled.
  declaration = tool._get_declaration()
```

#### 📊 Coverage Report
```
📊 Phase 4: Code Coverage Report (Target File)
============================================================
Name                                                                                                     Stmts   Miss Branch BrPart  Cover
------------------------------------------------------------------------------------------------------------------------------------------
/private/var/folders/cm/82x0j39d2076xcfjpm5qcxxr00gp60/T/verify_snippets_09387wsx/snippet_2_example.py       3      0      0      0   100%
------------------------------------------------------------------------------------------------------------------------------------------
TOTAL                                                                                                        3      0      0      0   100%
============================================================

```

---

### ❌ Snippet 3: `Context-Aware Sub-Agent Example`

#### 📝 Code Block
```python
verifier_agent = LlmAgent(
    name="verifier",
    instruction="Verify that the draft meets all constraints discussed in the chat.",
    mode="single_turn",
    include_contents="default"  # Allows the sub-agent to see the parent's conversation history
)

editor_agent = LlmAgent(
    name="editor",
    instruction="Discuss the draft with the user and use verifier to check constraints.",
    sub_agents=[verifier_agent]
)
```

#### 🖥️ Loadability & Runnability Logs
```
🔬 Testing file: snippet_3_contextaware_subagent_example.py
============================================================
📋 Phase 1: Loading & Compiling...
❌ Load Failure: Failed to compile/load 'snippet_3_contextaware_subagent_example.py':
------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/shahins/projects/mine/adk-python/.agents/skills/adk-verify-snippets/scripts/run.py", line 206, in main
    module = load_target_module(file_path)
  File "/Users/shahins/projects/mine/adk-python/.agents/skills/adk-verify-snippets/scripts/run.py", line 52, in load_target_module
    spec.loader.exec_module(module)
    ~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^
  File "<frozen importlib._bootstrap_external>", line 762, in exec_module
  File "<frozen importlib._bootstrap>", line 491, in _call_with_frames_removed
  File "/private/var/folders/cm/82x0j39d2076xcfjpm5qcxxr00gp60/T/verify_snippets_09387wsx/snippet_3_contextaware_subagent_example.py", line 1, in <module>
    verifier_agent = LlmAgent(
                     ^^^^^^^^
NameError: name 'LlmAgent' is not defined
------------------------------------------------------------
```

#### 📊 Coverage Report
```
📊 Phase 4: Code Coverage Report (Target File)
============================================================
Name                                                                                                                           Stmts   Miss Branch BrPart  Cover
----------------------------------------------------------------------------------------------------------------------------------------------------------------
/private/var/folders/cm/82x0j39d2076xcfjpm5qcxxr00gp60/T/verify_snippets_09387wsx/snippet_3_contextaware_subagent_example.py       2      1      0      0    50%
----------------------------------------------------------------------------------------------------------------------------------------------------------------
TOTAL                                                                                                                              2      1      0      0    50%
============================================================

```

---

