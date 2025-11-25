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

# Burn duration settings (simulation steps)
BURN_STEPS_CHAPARRAL = 7     # several days
BURN_STEPS_SCRUB = 1         # several hours
BURN_STEPS_DENSE_FOREST = 30 # up to one month

# Wind configuration
# Direction options: NONE, N, S, E, W, NE, NW, SE, SW
WIND_DIRECTION = 'W'
# Strength controls how strongly wind favours downwind spread over other directions
WIND_STRENGTH = 0.5

# Map each wind direction to the neighbour indices (NW, N, NE, W, E, SW, S, SE)
# that are upwind for a target cell. Fire is more likely to travel from these
# neighbours toward the cell when the wind blows in that direction.
WIND_FAVOURED_NEIGHBOURS = {
    'NONE': [],
    'N': [6],          # wind blows north -> stronger influence from south
    'S': [1],          # wind blows south -> stronger influence from north
    'E': [3],          # wind blows east  -> stronger influence from west
    'W': [4],          # wind blows west  -> stronger influence from east
    'NE': [5, 3, 6],   # wind blows north-east
    'NW': [4, 6, 7],   # wind blows north-west
    'SE': [0, 1, 3],   # wind blows south-east
    'SW': [1, 2, 4],   # wind blows south-west
}

# Globals for terrain tracking and burn timers
terrain_map = None          # immutable reference terrain types
burn_timers = None          # remaining burn steps per cell while on fire
burn_duration_grid = None   # lookup of burn duration per terrain cell

def _favoured_fire(neighbourstates):
    direction = WIND_DIRECTION.upper()
    favoured = WIND_FAVOURED_NEIGHBOURS.get(direction, [])
    if not favoured:
        return 0
    favoured_fire = np.zeros_like(neighbourstates[0], dtype=float)
    for idx in favoured:
        favoured_fire += (neighbourstates[idx] == STATE_FIRE)
    return favoured_fire

def _build_burn_duration_grid(base_grid):
    """Precompute how many steps each terrain burns for."""
    durations = np.zeros_like(base_grid, dtype=int)
    durations[base_grid == STATE_CHAP] = BURN_STEPS_CHAPARRAL
    durations[base_grid == STATE_SCRUB] = BURN_STEPS_SCRUB
    durations[base_grid == STATE_DENSE] = BURN_STEPS_DENSE_FOREST
    return durations

def _initialise_burn_support(grid):
    """Initialise burn tracking grids if they don't exist."""
    global burn_timers, burn_duration_grid, terrain_map
    if terrain_map is None:
        terrain_map = grid.copy()
    if burn_duration_grid is None:
        burn_duration_grid = _build_burn_duration_grid(terrain_map)
    if burn_timers is None:
        burn_timers = np.zeros_like(grid, dtype=int)

def transition_func(grid, neighbourstates, neighbourcounts):

    global burn_timers
    old = grid.copy()
    # burning neighbours
    burning_neighbours = neighbourcounts[STATE_FIRE]
    favoured_fire = _favoured_fire(neighbourstates)

    # wind strongly biases ignition toward the downwind neighbour(s)
    crosswind_fire = np.maximum(burning_neighbours - favoured_fire, 0)
    downwind_boost = 1 + favoured_fire * (WIND_STRENGTH * 6)
    crosswind_penalty = 1 - crosswind_fire * (WIND_STRENGTH * 0.75)
    crosswind_penalty = np.clip(crosswind_penalty, 0.2, None)
    wind_multiplier = np.clip(downwind_boost * crosswind_penalty, 0.2, None)

    probability = np.random.random(grid.shape)

   # catching fire probabilities
    probability_dense = 0.01
    probability_chaparral = 0.2
    # Scrubland ignites deterministically once adjacent to fire
    probability_scrub = 0.75

    dense_threshold = np.clip(probability_dense * wind_multiplier, 0, 1)
    chap_threshold  = np.clip(probability_chaparral * wind_multiplier, 0, 1)
    scrub_threshold = np.clip(probability_scrub * wind_multiplier, 0, 1)

    dense_burn = (grid == STATE_DENSE) & (burning_neighbours > 0) & (probability < dense_threshold)
    chap_burn  = (grid == STATE_CHAP)  & (burning_neighbours > 0) & (probability < chap_threshold)
    scrub_burn = (grid == STATE_SCRUB) & (burning_neighbours > 0)

    # all that will catch fire
    will_burn = dense_burn | chap_burn | scrub_burn

    # ensure burn timers exist (fallback if generate_grid wasn't called)
    if burn_timers is None:
        _initialise_burn_support(grid)

    # update burn timers for cells currently on fire
    currently_burning = (grid == STATE_FIRE)
    burn_timers[currently_burning] -= 1
    finished_burning = currently_burning & (burn_timers <= 0)
    continuing_burn = currently_burning & ~finished_burning

    new = old.copy()
    # cells that have finished burning become burnt
    new[finished_burning] = STATE_BURNT
    # keep cells burning if they still have time left
    new[continuing_burn] = STATE_FIRE

    # ignite new cells and set their burn timers based on terrain
    new_ignitions = will_burn & ~currently_burning
    if np.any(new_ignitions):
        burn_timers[new_ignitions] = burn_duration_grid[new_ignitions]
        new[new_ignitions] = STATE_FIRE
    # ensure timers for finished cells are reset
    burn_timers[finished_burning] = 0

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
    config.num_generations = 500
    config.grid_dims = (100,100)
    config.wrap = False

    # ----------------------------------------------------------------------

    if len(args) == 2:
        config.save()
        sys.exit()

    return config

def generate_grid(grid):
    global terrain_map, burn_timers, burn_duration_grid

    grid[:, :] = STATE_CHAP

    # grid[y, x] = state
    grid[10:15, 25:40] = STATE_DENSE
    grid[10:50, 10:25] = STATE_DENSE
    grid[50:70, 10:50] = STATE_DENSE

    grid[20:40, 35:40] = STATE_WATER
    grid[80:85, 50:80] = STATE_WATER

    grid[20:65, 70:75] = STATE_SCRUB

    # snapshot of underlying terrain for burn duration tracking
    terrain_map = grid.copy()
    burn_duration_grid = _build_burn_duration_grid(terrain_map)
    burn_timers = np.zeros_like(grid, dtype=int)

    # Power plant fire
    grid[0, 9] = STATE_FIRE
    # Incinerator fire
    grid[0, 99] = STATE_FIRE

    grid[88:92, 28:32] = STATE_TOWN

    # seed burn timers for initial fires
    initial_burning = (grid == STATE_FIRE)
    burn_timers[initial_burning] = burn_duration_grid[initial_burning]

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
