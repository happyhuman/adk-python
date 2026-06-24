# 🔬 ADK Markdown Snippet Verification Report

* **Source File**: [task.md](file:///Users/shahins/projects/mine/adk-python/docs/guides/agents/llm_agent/task.md)
* **Verified On**: `2026-06-23 19:02:28`

## 📈 Executive Summary

| Snippet | Preceding Heading | Load Phase | Run Phase | Coverage | Details |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Snippet 1** | `Example` | ❌ **FAIL** | ➖ **SKIPPED** | — | Failed to compile/load. |

---

## 🔍 Detailed Snippet Reports

### ❌ Snippet 1: `Example`

#### 📝 Code Block
```python
from google.adk.agents import LlmAgent
from pydantic import BaseModel, Field

# 1. Define schemas for Input and Output
class ResearchInput(BaseModel):
    topic: str = Field(description="The topic to research.")
    depth: str = Field(default="brief", description="Depth of research: brief or detailed.")

class ResearchOutput(BaseModel):
    summary: str = Field(description="A summary of the findings.")
    sources: list[str] = Field(description="List of sources used.")

# 2. Define the Task Agent
researcher_agent = LlmAgent(
    name="researcher",
    instruction="Research the given topic and provide a structured summary.",
    mode="task",
    input_schema=ResearchInput,
    output_schema=ResearchOutput,
    # Add tools needed for the task
    tools=[...]
)

# 3. Define the Parent Agent
writer_agent = LlmAgent(
    name="writer",
    instruction="Write a blog post. Use the researcher agent to get info on the topic.",
    sub_agents=[researcher_agent] # Exposes 'researcher' agent to writer
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
  File "/private/var/folders/cm/82x0j39d2076xcfjpm5qcxxr00gp60/T/verify_snippets__vng7hxw/snippet_1_example.py", line 14, in <module>
    researcher_agent = LlmAgent(
        name="researcher",
    ...<5 lines>...
        tools=[...]
    )
  File "/Users/shahins/projects/mine/adk-python/.venv/lib/python3.14/site-packages/pydantic/main.py", line 250, in __init__
    validated_self = self.__pydantic_validator__.validate_python(data, self_instance=self)
pydantic_core._pydantic_core.ValidationError: 3 validation errors for LlmAgent
tools.0.callable
  Input should be callable [type=callable_type, input_value=Ellipsis, input_type=ellipsis]
    For further information visit https://errors.pydantic.dev/2.12/v/callable_type
tools.0.is-instance[BaseTool]
  Input should be an instance of BaseTool [type=is_instance_of, input_value=Ellipsis, input_type=ellipsis]
    For further information visit https://errors.pydantic.dev/2.12/v/is_instance_of
tools.0.is-instance[BaseToolset]
  Input should be an instance of BaseToolset [type=is_instance_of, input_value=Ellipsis, input_type=ellipsis]
    For further information visit https://errors.pydantic.dev/2.12/v/is_instance_of
------------------------------------------------------------
```

#### 📊 Coverage Report
```
📊 Phase 4: Code Coverage Report (Target File)
============================================================
Name                                                                                                     Stmts   Miss Branch BrPart  Cover
------------------------------------------------------------------------------------------------------------------------------------------
/private/var/folders/cm/82x0j39d2076xcfjpm5qcxxr00gp60/T/verify_snippets__vng7hxw/snippet_1_example.py      10      1      0      0    90%
------------------------------------------------------------------------------------------------------------------------------------------
TOTAL                                                                                                       10      1      0      0    90%
============================================================

```

---

