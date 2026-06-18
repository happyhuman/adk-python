import argparse
import asyncio
import importlib.util
import inspect
import os
import sys
import traceback
from pathlib import Path

# --- Optional Coverage Integration ---
try:
    import coverage
    HAS_COVERAGE = True
except ImportError:
    HAS_COVERAGE = False

# --- Imports for ADK Inspection ---
from google.adk.agents.base_agent import BaseAgent
from google.adk.apps import App
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.workflow import Workflow
from google.genai import types

def load_target_module(file_path: Path):
    """Dynamically loads a Python file as a module, catching import/compilation/definition errors."""
    module_name = file_path.stem
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not resolve module spec for file '{file_path.name}'")
    
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    
    # Executing the module runs all top-level code, which will catch:
    # - SyntaxError / IndentationError
    # - ImportError (e.g. from google.adk.workflow import build_node)
    # - ValidationError (e.g. instantiating Workflow with invalid edges)
    spec.loader.exec_module(module)
    return module

def discover_adk_component(module):
    """Scans the module namespace to discover runnable ADK components, prioritizing root components."""
    # 1. Search for Workflow
    for name, obj in inspect.getmembers(module):
        if isinstance(obj, Workflow):
            return obj, "Workflow"

    # 2. Search for Agent (filtering out sub-agents to locate the Root Agent)
    agents = []
    sub_agent_ids = set()
    for name, obj in inspect.getmembers(module):
        if isinstance(obj, BaseAgent):
            agents.append(obj)
            # Track which agents are registered as sub-agents of another agent
            if hasattr(obj, "sub_agents") and obj.sub_agents:
                for sub in obj.sub_agents:
                    sub_agent_ids.add(id(sub))
                    
    # Find the agent(s) that are not sub-agents of any other agent in the module
    root_agents = [a for a in agents if id(a) not in sub_agent_ids]
    if root_agents:
        # Return the first root agent discovered
        return root_agents[0], "Agent"

    # 3. Search for App
    for name, obj in inspect.getmembers(module):
        if isinstance(obj, App):
            return obj, "App"
    return None, None

async def run_component(component, component_type, test_input):
    """Unified runner to execute the discovered component."""
    print(f"\n🔍 Discovered ADK {component_type} in target file.")
    print(f"🚀 Running execution test with input: '{test_input}'...\n")

    runnable_node = component.root_node if component_type == "App" else component

    session_service = InMemorySessionService()
    runner = Runner(app_name="runnability_test", node=runnable_node, session_service=session_service)
    session = await session_service.create_session(app_name="runnability_test", user_id="tester")

    user_message = types.Content(
        parts=[types.Part(text=str(test_input))],
        role="user"
    )

    async for event in runner.run_async(
        user_id="tester",
        session_id=session.id,
        new_message=user_message
    ):
        print(f"🎬 [Event] Author: {event.author}")
        if event.output:
            print(f"🔹 Output: {event.output}")
        if hasattr(event, "content") and event.content and event.content.parts:
            text = "".join(p.text for p in event.content.parts if p.text)
            if text:
                print(f"📝 Content Output:\n{'-'*40}\n{text}\n{'-'*40}")

def main():
    parser = argparse.ArgumentParser(description="Generalized ADK Runnability & Loadability Tester")
    parser.add_argument("file", type=str, help="Path to the python file containing the agent/workflow to test")
    args = parser.parse_args()

    file_path = Path(args.file).resolve()
    if not file_path.exists():
        print(f"❌ Error: File '{file_path}' does not exist.")
        sys.exit(1)

    print(f"🔬 Testing file: {file_path.name}")
    print("=" * 60)

    # Initialize coverage programmatically to track ONLY the target file
    cov = None
    if HAS_COVERAGE:
        cov = coverage.Coverage(
            branch=True,
            data_file=None # Keep coverage data in-memory only, no .coverage file needed
        )
        cov.start()
    else:
        print("ℹ️  Install 'coverage' package to enable automated code coverage reporting.")

    try:
        # 1. Test Loadability (Imports, Syntax, Instantiation/Validation)
        print("📋 Phase 1: Loading & Compiling...")
        try:
            module = load_target_module(file_path)
            print(f"✅ Load Success: '{file_path.name}' compiled and loaded without any issues.")
        except Exception as e:
            print(f"❌ Load Failure: Failed to compile/load '{file_path.name}':")
            print("-" * 60)
            traceback.print_exc(file=sys.stdout)
            print("-" * 60)
            sys.exit(1)

        # 2. Discover Component
        print("\n📋 Phase 2: Component Discovery...")
        component, comp_type = discover_adk_component(module)
        if not component:
            print(f"⚠️  No runnable ADK components (Workflow, Agent, or App) found in '{file_path.name}'.")
            print("   Loadability check passed, but runnability test was skipped.")
            sys.exit(0)

        # Get test input from module, or fallback
        test_input = getattr(module, "test_input", "Test input topic")

        # 3. Test Runnability
        print(f"\n📋 Phase 3: Executing {comp_type}...")
        try:
            asyncio.run(run_component(component, comp_type, test_input))
            print(f"\n✅ Run Success: Component '{comp_type}' executed successfully.")
        except Exception as e:
            print(f"\n❌ Run Failure: Component failed during execution:")
            print("-" * 60)
            traceback.print_exc(file=sys.stdout)
            print("-" * 60)
            sys.exit(1)
            
    finally:
        # Report coverage of the target file at the very end
        if cov:
            cov.stop()
            print("\n📊 Phase 4: Code Coverage Report (Target File)")
            print("=" * 60)
            try:
                # Report coverage of the target file directly to stdout
                cov.report(morfs=[str(file_path)], file=sys.stdout)
            except coverage.exceptions.NoDataError:
                print("⚠️  No coverage data collected (compilation or execution failed early).")
            except Exception as ce:
                print(f"⚠️  Failed to generate coverage report: {ce}")
            print("=" * 60)

if __name__ == "__main__":
    main()
