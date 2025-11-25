import subprocess
import sys
import os
from pathlib import Path

TOOLS = {
    "1": Path("GA_Teaching_Tool/teaching_tool.py"),
    "2": Path("ACO_Teaching_Tool/antsp/app.py"),
    "3": Path("CAPyle_releaseV2/release/main.py")
}

def main():
    script = TOOLS["3"]
    ca_path = Path("CAPyle_releaseV2/release/ca_descriptions/gol_2d.py")

    if not script.exists():
        print("CAPyle script not found.")
        sys.exit(1)

    if not ca_path.exists():
        print("gol_2d.py not found in ca_descriptions.")
        sys.exit(1)

    env = os.environ.copy()
    env["CAPYLE_AUTOLOAD"] = str(ca_path.resolve())

    try:
        subprocess.run([sys.executable, str(script)], check=True, env=env)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running CAPyle: {e}")
    except KeyboardInterrupt:
        print("\nExecution interrupted by user. Goodbye.")
        sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram terminated by user. Goodbye!")
        sys.exit(0)
