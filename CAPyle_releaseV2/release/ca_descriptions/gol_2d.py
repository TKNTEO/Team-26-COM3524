# Name: Modelling a Forest Fire
# Dimensions: 2

# --- Set up executable path, do not edit ---
import sys
import inspect
this_file_loc = (inspect.stack()[0][1])
main_dir_loc = this_file_loc[:this_file_loc.index('ca_descriptions')]
sys.path.append(main_dir_loc)
sys.path.append(main_dir_loc + 'capyle')
sys.path.append(main_dir_loc + 'capyle/ca')
sys.path.append(main_dir_loc + 'capyle/guicomponents')
# ---

from capyle.ca import Grid2D, Neighbourhood, CAConfig, randomise2d
import capyle.utils as utils
import numpy as np


def transition_func(grid, neighbourstates, neighbourcounts):
    # dead = state == 0, live = state == 1
    # unpack state counts for state 0 and state 1
    # dead_neighbours, live_neighbours = neighbourcounts
    # create boolean arrays for the birth & survival rules
    # if 3 live neighbours and is dead -> cell born
    # birth = (live_neighbours == 3) & (grid == 0)
    # if 2 or 3 live neighbours and is alive -> survives
    # survive = ((live_neighbours == 2) | (live_neighbours == 3)) & (grid == 1)
    # Set all cells to 0 (dead)
    # grid[:, :] = 0
    # Set cells to 1 where either cell is born or survives
    # grid[birth | survive] = 1
    return grid


def setup(args):
    config_path = args[0]
    config = utils.load(config_path)
    # ---THE CA MUST BE RELOADED IN THE GUI IF ANY OF THE BELOW ARE CHANGED---
    config.title = "Modelling a Forest Fire"
    config.dimensions = 2
    # --- 0 = Burnt, 1 = On Fire, 2 = Water, 3 = Dense Forest, 4 = Chaparral, 5 = Scrubland
    config.states = (0, 1, 2, 3, 4, 5)
    # ------------------------------------------------------------------------

    # ---- Override the defaults below (these may be changed at anytime) ----

    # --- 0 = Black, 1 = Orange, 2 = Blue, 3 = Dark Green, 4 = Yellow-Green, 5 = Yellow
    config.state_colors = [(0,0,0),(1,0.5,0),(0.3,0.7,1),(0.1,0.7,0),(0.8,1,0.3),(1,1,0)]
    # config.num_generations = 150
    # config.grid_dims = (200,200)

    # ----------------------------------------------------------------------

    if len(args) == 2:
        config.save()
        sys.exit()

    return config

def generate_grid(grid):
    grid[:, :] = 4

def main():
    # Open the config object
    config = setup(sys.argv[1:])

    # Create grid object
    grid = Grid2D(config, transition_func)

    # Grid generation logic function
    generate_grid(grid)


    # Run the CA, save grid state every generation to timeline
    timeline = grid.run()

    # save updated config to file
    config.save()
    # save timeline to file
    utils.save(timeline, config.timeline_path)


if __name__ == "__main__":
    main()
