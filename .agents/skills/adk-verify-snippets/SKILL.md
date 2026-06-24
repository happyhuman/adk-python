---
name: adk-verify-snippets
description: >
  Extracts and verifies the runnability and code coverage of all Python code blocks inside a Markdown file.
  Generates a detailed compilation and execution report.
metadata:
  author: Antigravity
  version: 1.4.0
---

# Verify Markdown Snippets Skill

This skill allows you to systematically verify the correctness, compile-readiness, and line coverage of Python code snippets embedded within a Markdown document (like tutorials, guides, or READMEs).

It extracts all ` ```python ` blocks, executes them in process-isolated environments using the bundled `run.py` harness, and generates a structured test report.

> [!CAUTION]
> **STRICT READ-ONLY CONSTRAINT — READ THIS BEFORE DOING ANYTHING ELSE**
>
> When executing this skill, the agent operates in a **strictly read-only** mode with respect to the repository. The agent **MUST NOT**, under any circumstances:
> - **Modify** any existing source file, test file, configuration file, documentation file, or skill file (including this SKILL.md).
> - **Delete** any file in the repository.
> - **Create** any new file in the repository other than the two explicit exceptions listed below.
>
> The **only** two write operations permitted are:
> 1. Writing temporary snippet `.py` files to a uniquely-named **system temp directory** (outside the repository).
> 2. Writing the final `<filename>_REPORT.md` report file into the **same directory as the source Markdown file**.
>
> Any other file system mutation is a violation of this skill's contract. If in doubt, do not write.

---

## 🔧 Prerequisites

Before running this skill, ensure the following are in place:

1.  **ADK Python environment**: The skill must be run from the repository root with the project's virtual environment active (via `uv`).
2.  **`coverage` package**: Install it to enable per-snippet coverage reporting:
    ```bash
    uv pip install coverage
    ```
    If `coverage` is not installed, the runner degrades gracefully — verification still works, but coverage columns in the report will show `—`.
3.  **Gemini API key**: Snippets that instantiate an `Agent`, `App`, or `Workflow` make live calls to the Gemini API. Set one of the following environment variables before running:
    ```bash
    export GEMINI_API_KEY="your-key-here"
    # or
    export GOOGLE_API_KEY="your-key-here"
    ```
    If both are set, `GEMINI_API_KEY` takes precedence. Snippets that do not expose a runnable ADK component (loadability-only checks) do not require an API key.

---

## 🛠️ How to Use the Skill

To verify a Markdown file (e.g. `docs/my_guide.md`) and generate its runnability report:

```bash
uv run --no-sync python .agents/skills/adk-verify-snippets/scripts/verify_md.py <path_to_markdown_file.md>
```

For example:
```bash
uv run --no-sync python .agents/skills/adk-verify-snippets/scripts/verify_md.py docs/my_guide.md
```

This will automatically create a detailed report file called **`docs/my_guide_REPORT.md`** in the same directory as the source file. The full path is printed on completion.

---

## 📝 Snippet Code Conventions

Each Python code block in the Markdown file is verified using the `run.py` contract. Blocks fall into one of four categories:

1.  **Expose a Global ADK Component (Runnability Test)**:
    If the snippet instantiates a global `Workflow`, `Agent`, or `App`, the runner will automatically execute it and measure its execution against the Gemini API.

    **Requirement**: The component must be assigned to a **module-level variable** (i.e., defined at the top level of the snippet, not inside a function or class). The variable name does not matter — the runner scans `vars(module)` to find it automatically. For multi-agent snippets, the runner identifies the root agent by filtering out any agents that are listed as `sub_agents` of another agent in the same snippet.

    **If this requirement is not met** (i.e., no module-level `Workflow`, `Agent`, or `App` instance exists), the runnability test is skipped. The report will show `➖ NO ADK COMPONENT` in the Run Phase column and explain that no runnable component was found at module level.

2.  **Provide a Custom Test Input (Optional)**:
    If the snippet defines a global `test_input` variable, the runner will use that string as the user message during execution instead of the default `"Test input topic"`.
3.  **Basic Python Snippets (Loadability Only)**:
    If a code block does not define any runnable ADK components, the runner will verify that it compiles and loads without error. No API call is made, and coverage is reported as 100% for the lines present.
4.  **Skipping Illustrative / Pseudo-code Blocks**:
    Place the HTML comment `<!-- verify-snippets: ignore -->` on the line **immediately before** the opening ` ```python ` fence to exclude that block from execution entirely. It will appear in the report as `⏭️ SKIPPED`. Use this for conceptual examples, incomplete snippets, or blocks that intentionally require external setup unavailable in CI.

    Example — place the annotation on the line directly above the fence, with no blank line between them:

    ````markdown
    <!-- verify-snippets: ignore -->
    ```python
    # This is pseudo-code — not runnable as-is
    my_agent = Agent(model="gemini-ultra-hypothetical", ...)
    ```
    ````

---

## ⚠️ Known Limitations

*   **No cumulative / dependent snippet support**: Each snippet is executed in a fully isolated subprocess with no shared state. If a snippet depends on imports, variables, or definitions introduced by a *previous* snippet in the same document, it will fail with a `NameError` or `ImportError`. Author each code block to be self-contained, or annotate dependent snippets with `<!-- verify-snippets: ignore -->`.
*   **120-second execution timeout**: Each snippet subprocess is killed after 120 seconds. Snippets that intentionally block (e.g., long-running servers) must be annotated with `<!-- verify-snippets: ignore -->`.
*   **`<!-- verify-snippets: ignore -->` must be close to the fence**: Blank lines between the annotation and the ` ```python ` fence are tolerated, but any non-blank line (prose, another heading, etc.) between them cancels the annotation. Place the annotation on the line immediately before the opening fence to be safe.
*   **No nested fences inside a code block**: The parser closes a Python block only on a bare ` ``` ` line (no language tag). Lines like ` ```bash ` or ` ```text ` inside the block are treated as literal content. However, a bare ` ``` ` that is the closing fence of a *non-Python* outer block will prematurely terminate any open Python block if the nesting depth is mismatched. Annotate such snippets with `<!-- verify-snippets: ignore -->`.

---

## 📊 The Generated Report Structure

The generated `<filename>_REPORT.md` will contain:
1.  **Executive Summary**: A high-level table listing every discovered snippet, its preceding Markdown heading, its Load phase status, Run phase status, and line coverage percentage.
2.  **Detailed Breakdown**:
    *   The exact extracted Python code block.
    *   The detailed execution stdout logs (phases 1–3).
    *   Any stderr traceback/exceptions (pointing directly to the breaking line of code).
    *   A full `coverage report` output showing exactly which lines of the snippet were executed.

---

## ⚠️ Crucial Behavioral Constraints (For AI Agents)

*   **Read-Only**: See the caution block at the top of this document. The constraint is absolute — no modifications, no deletions, no new files beyond the two permitted exceptions.
*   **Strictly Report, Do Not Fix**: The sole purpose of this skill is to **identify and report** compile-time and run-time issues within the Markdown document's snippets.
*   **No Unsolicited Patches**: When executing this skill, the agent **MUST NOT** attempt to rewrite the source Markdown file, modify its code blocks, or automatically generate code fixes/patches.
*   **Present the Summary Table Verbatim**: After the script completes, the agent MUST read the generated `<filename>_REPORT.md` file and copy the Executive Summary table to the user **exactly as written** — same columns, same column names, same order. The table has exactly these six columns:
    `Snippet | Preceding Heading | Load Phase | Run Phase | Coverage | Details`
    The agent MUST NOT rename, reorder, merge, or drop any column when presenting results. Do not offer solutions or rewrite recommendations unless the user explicitly asks for them.
