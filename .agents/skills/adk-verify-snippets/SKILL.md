---
name: adk-verify-snippets
description: >
  Extracts and verifies the runnability and code coverage of all Python code blocks inside a Markdown file.
  Generates a detailed compilation and execution report.
metadata:
  author: Antigravity
  version: 1.0.0
---

# Verify Markdown Snippets Skill

This skill allows you to systematically verify the correctness, compile-readiness, and line coverage of Python code snippets embedded within a Markdown document (like tutorials, guides, or READMEs).

It extracts all ` ```python ` blocks, executes them in process-isolated environments using the bundled `run.py` harness, and generates a structured test report.

---

## 🛠️ How to Use the Skill

To verify a Markdown file (e.g. `docs/my_guide.md`) and generate its runnability report:

```bash
uv run --no-sync python .agents/skills/verify-markdown-snippets/scripts/verify_md.py <path_to_markdown_file.md>
```

For example:
```bash
uv run --no-sync python .agents/skills/verify-markdown-snippets/scripts/verify_md.py docs/my_guide.md
```

This will automatically create a detailed report file called **`docs/my_guide_report.md`** in the same directory.

---

## 📝 Snippet Code Conventions

Each python code snippet inside the Markdown file is verified using our generalized `run.py` contract. For a code block to be fully testable for both loadability and runnability:

1.  **Expose a Global ADK Component (Optional for Runnability)**:
    If the snippet instantiates a global `Workflow`, `Agent`, or `App`, the runner will automatically execute it and measure its execution.
2.  **Provide a Custom Test Input (Optional)**:
    If the snippet defines a global `test_input` variable, the runner will use it during execution.
3.  **Basic Python Snippets (Loadability Only)**:
    If a code block does not define any runnable ADK components, the runner will verify that it compiles and loads without error, and report a 100% coverage report for the lines present in the block.

---

## 📊 The Generated Report Structure

The generated `<filename>_report.md` will contain:
1.  **Executive Summary**: A high-level table listing every discovered snippet, its preceding Markdown heading, its status (Passed/Failed), and its line coverage.
2.  **Detailed Breakdown**:
    *   The exact extracted python code block.
    *   The detailed execution stdout logs.
    *   Any stderr traceback/exceptions (pointing directly to the breaking line of code!).
    *   A clean, focused 5-line coverage table showing exactly what lines of the snippet were executed.

---

## ⚠️ Crucial Behavioral Constraints (For AI Agents)

*   **Strictly Read-Only Workspace**: The skill's operations on the repository are strictly **read-only**. The agent **MUST NOT** modify, create, or delete any existing source files, test files, configuration files, or documentation files in the repository (with the sole exceptions of writing temporary execution files to `.temp_snippets` and generating the final `<filename>_report.md` report file).
*   **Strictly Report, Do Not Fix**: The sole purpose of this skill is to **identify and report** compile-time and run-time issues within the Markdown document's snippets.
*   **No Unsolicited Patches**: When executing this skill, the agent **MUST NOT** attempt to rewrite the source Markdown file, modify its code blocks, or automatically generate code fixes/patches.
*   **Focus on the Report**: The agent should run the verification, let the script generate the `<filename>_report.md` file, and present the executive summary table to the user. Do not offer solutions or rewrite recommendations unless the user explicitly asks for them.
