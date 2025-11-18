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

STATE_BURNT = 0
STATE_FIRE = 1
STATE_WATER = 2
STATE_DENSE = 3
STATE_CHAP = 4
STATE_SCRUB = 5
STATE_TOWN = 6

def transition_func(grid, neighbourstates, neighbourcounts):

    old = grid.copy()
    # burning neighbours
    burning_neighbours = neighbourcounts[STATE_FIRE]

    probability = np.random.random(grid.shape)

   # catching fire probabilities
    probability_dense = 0.5
    probability_chaparral = 0.9
    probability_scrub = 0.95

    dense_burn = (grid == STATE_DENSE) & (burning_neighbours > 0) & (probability < probability_dense)
    chap_burn  = (grid == STATE_CHAP) & (burning_neighbours > 0) & (probability < probability_chaparral)
    scrub_burn = (grid == STATE_SCRUB) & (burning_neighbours > 0) & (probability < probability_scrub)

    # all that will catch fire
    will_burn = dense_burn | chap_burn | scrub_burn
    new = old.copy()
    new[old == STATE_FIRE] = STATE_BURNT
    new[will_burn] = STATE_FIRE

    return new



def setup(args):
    config_path = args[0]
    config = utils.load(config_path)
    # ---THE CA MUST BE RELOADED IN THE GUI IF ANY OF THE BELOW ARE CHANGED---
    config.title = "Modelling a Forest Fire"
    config.dimensions = 2
    # --- 0 = Burnt, 1 = On Fire, 2 = Water, 3 = Dense Forest, 4 = Chaparral, 5 = Scrubland, 6 = Town (end)
    config.states = (0, 1, 2, 3, 4, 5, 6)
    # ------------------------------------------------------------------------

    # ---- Override the defaults below (these may be changed at anytime) ----

    # --- 0 = Black, 1 = Orange, 2 = Blue, 3 = Dark Green, 4 = Yellow-Green, 5 = Yellow, 6 = Pink
    config.state_colors = [(0,0,0),(1,0.5,0),(0.3,0.7,1),(0.1,0.7,0),(0.8,1,0.3),(1,1,0),(0.9,0.1,0.8)]
    config.num_generations = 150
    config.grid_dims = (100,100)
    config.wrap = False

    # ----------------------------------------------------------------------

    if len(args) == 2:
        config.save()
        sys.exit()

    return config

def generate_grid(grid):

    grid[:, :] = STATE_CHAP

    # grid[y, x] = state
    grid[10:15, 25:40] = STATE_DENSE
    grid[10:50, 10:25] = STATE_DENSE
    grid[50:70, 10:50] = STATE_DENSE

    grid[20:40, 35:40] = STATE_WATER
    grid[80:85, 50:80] = STATE_WATER

    grid[20:65, 70:75] = STATE_SCRUB

    # Power plant fire
    grid[0, 9] = STATE_FIRE
    # Incinerator fire
    grid[0, 99] = STATE_FIRE

    grid[88:92, 28:32] = STATE_TOWN

def main():
    # Open the config object
    config = setup(sys.argv[1:])

    # Create grid object
    grid = Grid2D(config, transition_func)

    # Grid generation logic function
    generate_grid(grid.grid)


    # Run the CA, save grid state every generation to timeline
    timeline = grid.run()

    # save updated config to file
    config.save()
    # save timeline to file
    utils.save(timeline, config.timeline_path)


if __name__ == "__main__":
    main()
