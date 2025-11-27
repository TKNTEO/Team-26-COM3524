# Team 26 COM3524 - Modelling a Forest Fire

This repo provides the code for Team 26 COM3524 assignment. You can run them through a GUI menu (`run_tool.py`) or directly from the command line (`run_sim.py`). 
### Follow the steps below to get started:

## 1) Prerequisites
- Python 3.8+ and `pip`
- Git (to clone the repo)
- Docker Desktop (or Docker Engine on Linux)
- X11 server for GUI support: VcXsrv (Windows), XQuartz (macOS), built-in on most Linux distros

## 2) Get the code
```bash
git clone https://github.com/TKNTEO/Team-26-COM3524
cd Team-26-COM3524
```

## 3) Start the container (choose your OS script)
- Linux: `./linux.sh`
- macOS: `./mac.sh`
- Windows (PowerShell or cmd): `.\windows.bat`

Each script mounts the repo and drops you into a shell inside the container (`root@com3524:/src#`).

## 4) Run the GUI tool menu (run_tool.py)
Inside the container shell:
```bash
python run_tool.py
```
Press `Apply configuration & run CA` in the bottom-left of the GUI window, then press play to watch the simulation run.
## 5) Run CLI simulations (run_sim.py)
> `run_sim.py` is CLI-only; no GUI window appears. Screenshots are written to the output directory you choose.

Basic form:
```bash
python run_sim.py [START_LOCATION] [RUNS] [options]
```
- `START_LOCATION`: `POWER_PLANT`, `INCINERATOR`, or `BOTH`
- `RUNS` (optional): number of simulations to run (default 1)
- Available options:
  - `--wind_direction` (`-d`): `NONE` (default), `N`, `S`, `E`, `W`, `NE`, `NW`, `SE`, `SW`
  - `--wind_strength` (`-s`): wind strength (default 50)
  - `--water-drop` (`-w`): rectangle `x1,y1:x2,y2`
  - `--water-drop-delay` (`-y`): steps before drop is applied (default 0)
  - `--output-dir` (`-o`): where to save screenshots (default `sim_outputs`)

### Examples
- Single run from power plant with east wind:
  ```bash
  python run_sim.py POWER_PLANT 1 --wind_direction E
  ```
- Five runs, stronger wind, custom output folder:
  ```bash
  python run_sim.py POWER_PLANT 5 --wind_direction E --wind_strength 40 --output-dir sim_outputs
  ```
- Two runs, water drop after 20 steps:
  ```bash
  python run_sim.py INCINERATOR 2 --water-drop 30,30:40,40 --water-drop-delay 20
  ```

### Outputs and stats
- Screenshots for sampled steps are saved under the chosen output dir (`sim_outputs` if not chosen).
- If fire reaches the town, a `simX_town.png` is saved and the step number is reported.
- When multiple runs reach the town, the script prints the average step to contact.
