import argparse
import os
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
import numpy as np

# Paths
ROOT_DIR = Path(__file__).resolve().parent
RELEASE_DIR = ROOT_DIR / "CAPyle_releaseV2" / "release"
CA_FILE = RELEASE_DIR / "ca_descriptions" / "gol_2d.py"

# Ensure capyle modules are importable
sys.path.append(str(RELEASE_DIR))
sys.path.append(str(RELEASE_DIR / "capyle"))
sys.path.append(str(RELEASE_DIR / "capyle" / "ca"))
sys.path.append(str(RELEASE_DIR / "capyle" / "guicomponents"))

from capyle.ca import CAConfig  # noqa: E402
import capyle.utils as utils  # noqa: E402

# Make temp files go under release dir
CAConfig.ROOT_PATH = str(RELEASE_DIR)

def render_step(grid, state_colors, out_path):
    cmap = ListedColormap(state_colors)
    bounds = [i - 0.5 for i in range(len(state_colors) + 1)]
    norm = BoundaryNorm(bounds, len(state_colors))
    plt.figure(figsize=(5, 5))
    plt.imshow(grid, cmap=cmap, norm=norm, interpolation="nearest")
    plt.axis("off")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, bbox_inches="tight", pad_inches=0)
    plt.close()


def run_once(sim_index, start_location, wind_dir, wind_strength, output_dir):
    print(f"Starting simulation {sim_index} "
          f"(start={start_location.upper()}, wind={wind_dir.upper()}@{wind_strength})")
    os.environ["START_LOCATION"] = start_location.upper()
    os.environ["WIND_DIRECTION"] = wind_dir.upper()
    os.environ["WIND_STRENGTH"] = str(wind_strength)
    if os.environ.get("WATER_DROP"):
        print(f"  Water drop at {os.environ['WATER_DROP']} after {os.environ.get('WATER_DROP_DELAY', '0')} step(s)")

    config = CAConfig(str(CA_FILE))
    config = utils.prerun_ca(config)
    config, timeline = utils.run_ca(config)
    if timeline is None:
        raise RuntimeError("Simulation failed to produce a timeline.")

    steps = list(range(1, timeline.shape[0], 50))
    last_step = timeline.shape[0] - 1
    if last_step not in steps:
        steps.append(last_step)

    # determine when fire reaches town (adjacent to town cells)
    town_mask = timeline[0] == 6
    padded = np.pad(town_mask, 1, mode="constant", constant_values=False)
    dilated = np.zeros_like(padded, dtype=bool)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            dilated |= np.roll(np.roll(padded, dy, axis=0), dx, axis=1)
    town_neighbourhood = dilated[1:-1, 1:-1]
    town_contact_step = None
    for idx, grid in enumerate(timeline):
        if np.any((grid == 1) & town_neighbourhood):
            town_contact_step = idx
            break

    state_colors = config.state_colors
    for step in steps:
        out_path = output_dir / f"sim{sim_index}_step{step}.png"
        render_step(timeline[step], state_colors, out_path)
    if town_contact_step is not None:
        print(f"Simulation {sim_index}: fire reached town at step {town_contact_step}")
        out_path = output_dir / f"sim{sim_index}_town_step{town_contact_step}.png"
        render_step(timeline[town_contact_step], state_colors, out_path)
    else:
        print(f"Simulation {sim_index}: fire never reached town")

def main():
    parser = argparse.ArgumentParser(
        description="Run forest fire simulation repeatedly and capture screenshots.")
    parser.add_argument("start_location",
                        choices=["POWER_PLANT", "INCINERATOR", "BOTH"],
                        help="Where to ignite the fire. (Required)")
    parser.add_argument("runs", nargs="?", type=int, default=1,
                        help="Number of simulations to run (default: 1).")
    parser.add_argument("--wind-direction", "-d", default="NONE",
                        choices=["NONE", "N", "S", "E", "W", "NE", "NW", "SE", "SW"],
                        help="Wind direction (default: NONE).")
    parser.add_argument("--wind-strength", "-s", type=float, default=50,
                        help="Wind strength (default: 50).")
    parser.add_argument("--water-drop", "-w",
                        help='Optional water drop rectangle as "x1,y1:x2,y2".')
    parser.add_argument("--water-drop-delay", "-y", type=int, default=0,
                        help="Delay in steps before applying the water drop (default: 0).")
    parser.add_argument("--output-dir", "-o", default="sim_outputs",
                        help="Directory to save screenshots.")
    args = parser.parse_args()

    if not CA_FILE.exists():
        print(f"CA description not found at {CA_FILE}")
        sys.exit(1)

    output_dir = Path(args.output_dir)

    if args.water_drop:
        os.environ["WATER_DROP"] = args.water_drop
    else:
        os.environ.pop("WATER_DROP", None)
    os.environ["WATER_DROP_DELAY"] = str(max(0, args.water_drop_delay))

    for i in range(args.runs):
        try:
            run_once(i, args.start_location, args.wind_direction,
                     args.wind_strength, output_dir)
        except Exception as e:
            print(f"Simulation {i} failed: {e}")
            sys.exit(1)
    print(f"Completed {args.runs} run(s). Screenshots saved under {output_dir}.")

if __name__ == "__main__":
    main()
