#!/usr/bin/env python3
"""
Script to execute all Jupyter notebooks in sequence using nbclient.
Saves executed notebooks with timestamp.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

try:
    import nbclient
    import nbformat
except ImportError:
    print("ERROR: nbclient and nbformat are required. Install with:")
    print("  pip install nbclient nbformat")
    sys.exit(1)


def run_notebooks():
    """Execute all notebooks in order."""

    script_dir = Path(__file__).parent.absolute()
    code_dir = script_dir / ""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = script_dir / "notebook_runs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"run_{timestamp}.log"

    # List of notebooks to run (in order)
    notebooks = [
        "1 Set up data.ipynb",
        "2 Generate oncogenic-activation signature.ipynb",
        "3 Decompose oncogenic-activation signature and define transcriptional components.ipynb",
        "4 Annotate transcriptional components.ipynb",
        "5 Define cellular states and make Onco-GPS map.ipynb",
        "6 Annotate cellular states.ipynb",
        "7 Display genomic features on Onco-GPS map.ipynb",
        "8 Define global cellular states and make global Onco-GPS map.ipynb",
        "9 Display genomic features on global Onco-GPS map.ipynb",
    ]

    print(f"Starting notebook execution at {datetime.now()}")
    print(f"Log file: {log_file}")
    print("-" * 60)

    completed = 0
    failed = 0
    total = len(notebooks)

    with open(log_file, "w") as log:
        log.write(f"Notebook execution log - {datetime.now()}\n")
        log.write(f"Total notebooks: {total}\n")
        log.write("=" * 60 + "\n\n")

        for notebook in notebooks:
            completed += 1
            notebook_path = code_dir / notebook
            output_name = f"{notebook[:-6]}_executed_{timestamp}.ipynb"
            output_file = code_dir / output_name

            if not notebook_path.exists():
                msg = f"[{completed}/{total}] ERROR: Notebook not found: {notebook_path}"
                print(msg)
                log.write(msg + "\n")
                failed += 1
                continue

            msg = f"[{completed}/{total}] Running: {notebook}"
            print(msg)
            log.write(msg + "\n")

            try:
                # Read the notebook
                with open(notebook_path) as f:
                    nb = nbformat.read(f, as_version=4)

                # Inject a setup cell at the beginning to add code_dir to sys.path
                setup_cell = nbformat.v4.new_code_cell(
                    f"import sys\nif {repr(str(code_dir))} not in sys.path:\n    sys.path.insert(0, {repr(str(code_dir))})"
                )
                nb.cells.insert(0, setup_cell)

                # Execute the notebook
                client = nbclient.NotebookClient(nb, cwd=str(code_dir))
                client.execute()

                # Write the executed notebook
                with open(output_file, "w") as f:
                    nbformat.write(nb, f)

                msg = "  ✓ Completed successfully"
                print(msg)
                log.write(msg + "\n")

            except nbclient.exceptions.CellExecutionError as e:
                msg = f"  ✗ FAILED: Cell execution error\n{str(e)[:500]}"
                print(msg)
                log.write(msg + "\n")
                failed += 1
            except Exception as e:
                msg = f"  ✗ FAILED: {type(e).__name__}: {str(e)[:500]}"
                print(msg)
                log.write(msg + "\n")
                failed += 1

            log.write("\n")

        # Summary
        log.write("=" * 60 + "\n")
        summary = f"Execution completed at {datetime.now()}\n"
        summary += f"Summary: {total - failed}/{total} notebooks completed successfully\n"
        print("-" * 60)
        print(summary)
        log.write(summary)

        if failed == 0:
            print("✓ All notebooks executed successfully!")
            log.write("✓ All notebooks executed successfully!\n")
            return 0
        else:
            print(f"✗ WARNING: {failed} notebook(s) failed!")
            log.write(f"✗ WARNING: {failed} notebook(s) failed!\n")
            return 1


if __name__ == "__main__":
    sys.exit(run_notebooks())
