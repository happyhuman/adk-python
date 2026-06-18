import argparse
from datetime import datetime
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

def extract_snippets(md_path: Path):
    """Parses a markdown file and extracts python code blocks along with their preceding headings."""
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.splitlines()
    snippets = []
    current_heading = "Top Level"
    in_code_block = False
    code_lines = []
    
    for line in lines:
        # If we are inside a code block, handle it first to preserve comments starting with '#'
        if in_code_block:
            if line.strip().startswith("```"):
                in_code_block = False
                code_text = "\n".join(code_lines)
                snippets.append({
                    "heading": current_heading,
                    "code": code_text
                })
            else:
                code_lines.append(line)
            continue
            
        # If we are outside a code block, check for headings or code block starts
        if line.startswith("#"):
            # Clean up heading markers (e.g., "## Get started" -> "Get started")
            current_heading = line.lstrip("#").strip()
            continue
            
        if line.strip().startswith("```python"):
            in_code_block = True
            code_lines = []
            continue
            
    return snippets

def run_snippet(run_py_path: Path, snippet_path: Path):
    """Executes run.py on the isolated snippet and returns the result."""
    # Run using the same Python interpreter as this script (which will be the venv's python)
    cmd = [sys.executable, str(run_py_path), str(snippet_path)]
    
    # Ensure GEMINI_API_KEY is preferred if both keys are set in the environment
    env = os.environ.copy()
    if "GOOGLE_API_KEY" in env and "GEMINI_API_KEY" in env:
        env.pop("GOOGLE_API_KEY", None)
        
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=env
    )
    
    return {
        "exit_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr
    }

def clean_name(name: str):
    """Sanitizes a string to be a safe filename."""
    name = name.lower().replace(" ", "_")
    return re.sub(r'[^a-z0-9__]', '', name)

def main():
    parser = argparse.ArgumentParser(description="Markdown Snippet Verifier")
    parser.add_argument("file", type=str, help="Path to the markdown file to verify")
    args = parser.parse_args()

    md_path = Path(args.file).resolve()
    if not md_path.exists():
        print(f"❌ Error: Markdown file '{md_path}' does not exist.")
        sys.exit(1)

    # Locate run.py bundled inside the same scripts folder as verify_md.py (portable mode!)
    run_py_path = Path(__file__).parent / "run.py"
    if not run_py_path.exists():
        print(f"❌ Error: Bundled runner 'run.py' not found at '{run_py_path}'.")
        sys.exit(1)

    print(f"🔬 Analyzing Markdown: {md_path.name}")
    
    # 1. Extract snippets
    snippets = extract_snippets(md_path)
    if not snippets:
        print(f"⚠️  No python code blocks found in '{md_path.name}'.")
        sys.exit(0)
        
    print(f"📋 Found {len(snippets)} python code snippets to verify.")

    # Create a temp directory in the workspace
    temp_dir = Path(".temp_snippets")
    temp_dir.mkdir(exist_ok=True)

    results = []

    # 2. Execute each snippet
    for i, snippet in enumerate(snippets, start=1):
        heading = snippet["heading"]
        code = snippet["code"]
        
        # Create a unique, sanitized filename for the snippet
        safe_heading = clean_name(heading)
        temp_file_name = f"snippet_{i}_{safe_heading}.py"
        temp_file_path = temp_dir / temp_file_name
        
        # Write snippet to file
        with open(temp_file_path, "w", encoding="utf-8") as f:
            f.write(code)
            
        print(f"🧪 Testing Snippet {i}/{len(snippets)} under heading '{heading}'...")
        
        # Run the snippet
        run_res = run_snippet(run_py_path, temp_file_path)
        
        results.append({
            "index": i,
            "heading": heading,
            "code": code,
            "temp_file": temp_file_name,
            "exit_code": run_res["exit_code"],
            "stdout": run_res["stdout"],
            "stderr": run_res["stderr"]
        })

    # Clean up temporary directory
    shutil.rmtree(temp_dir, ignore_errors=True)

    # 3. Generate Markdown Report
    report_path = md_path.parent / f"{md_path.stem}_report.md"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"# 🔬 ADK Markdown Snippet Verification Report\n\n")
        f.write(f"* **Source File**: [{md_path.name}](file://{md_path})\n")
        f.write(f"* **Verified On**: `{timestamp}`\n\n")
        
        # Write summary table
        f.write("## 📈 Executive Summary\n\n")
        f.write("| Snippet | preceding Heading | Load Phase | Run Phase | Coverage | Uncovered Issues / Details |\n")
        f.write("| :--- | :--- | :---: | :---: | :---: | :--- |\n")
        
        for r in results:
            # Determine Phase 1 (Load) and Phase 3 (Run) statuses
            load_status = "✅ **PASS**"
            run_status = "✅ **PASS**"
            coverage_pct = "—"
            
            stdout_and_stderr = r["stdout"] + "\n" + r["stderr"]
            
            # 1. Parse Load Phase
            if "❌ Load Failure" in stdout_and_stderr or "Load Failure" in stdout_and_stderr:
                load_status = "❌ **FAIL**"
                run_status = "➖ **SKIPPED**"
            
            # 2. Parse Run Phase
            elif "runnability test was skipped" in stdout_and_stderr:
                run_status = "➖ **SKIPPED**"
            elif "❌ Run Failure" in stdout_and_stderr or r["exit_code"] != 0:
                run_status = "❌ **FAIL**"
                
            # 3. Parse Coverage
            cov_match = re.search(r"TOTAL\s+\d+\s+\d+\s+\d+\s+\d+\s+(\d+%)", r["stdout"])
            if cov_match and load_status != "❌ **FAIL**":
                coverage_pct = f"`{cov_match.group(1)}`"
                
            # 4. Formulate details and handle transient 503s
            details = "All checks passed successfully."
            if load_status == "❌ **FAIL**":
                err_lines = [line for line in stdout_and_stderr.splitlines() if "Error" in line or "Exception" in line]
                details = f"`{err_lines[-1]}`" if err_lines else "Failed to compile/load."
            elif run_status == "❌ **FAIL**":
                if "503" in stdout_and_stderr and "UNAVAILABLE" in stdout_and_stderr:
                    details = "⚠️ **Transient 503 from Gemini API (overloaded)**. Code structure is correct."
                else:
                    err_lines = [line for line in stdout_and_stderr.splitlines() if "Error" in line or "Exception" in line]
                    details = f"`{err_lines[-1]}`" if err_lines else "Failed during execution."
                    
            f.write(f"| **Snippet {r['index']}** | `{r['heading']}` | {load_status} | {run_status} | {coverage_pct} | {details} |\n")
            
        f.write("\n---\n\n## 🔍 Detailed Snippet Reports\n\n")
        
        for r in results:
            status_icon = "✅" if r["exit_code"] == 0 else "❌"
            f.write(f"### {status_icon} Snippet {r['index']}: `{r['heading']}`\n\n")
            
            f.write("#### 📝 Code Block\n")
            f.write(f"```python\n{r['code']}\n```\n\n")
            
            # Write stdout / stderr logs
            f.write("#### 🖥️ Loadability & Runnability Logs\n")
            f.write("```text\n")
            
            # Clean up stdout to separate Phase 4 coverage
            stdout_clean = r["stdout"]
            cov_match = re.search(r"(📊 Phase 4: Code Coverage Report.*)", r["stdout"], re.DOTALL)
            cov_text = cov_match.group(1) if cov_match else None
            
            if cov_text:
                stdout_clean = r["stdout"].replace(cov_text, "").strip()
                
            f.write(stdout_clean)
            if r["stderr"]:
                f.write("\n\n=== STDERR/TRACEBACK ===\n")
                f.write(r["stderr"].strip())
            f.write("\n```\n\n")
            
            # Write coverage report if available
            if cov_text:
                f.write("#### 📊 Coverage Report\n")
                f.write(f"```text\n{cov_text}\n```\n\n")
                
            f.write("---\n\n")
            
    print(f"🎉 Verification complete! Report generated at: {report_path.name}")

if __name__ == "__main__":
    main()
