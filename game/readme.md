
# `game` Documentation
## Overview
This subfolder contains helper classes for updating and displaying the menu and game states. `Manager` is the top level class that is used to control members from `Launcher` and `GameState`. A `manager` object is instantiated and called from the main thread of `.\controller.py`. 

## Code
### `manager.py`
Contains the `Manager` class. This class contains instances of `Launcher` and `GameState`.  

### `launcher.py`
Contains the `Launcher` class. This class contains a state machine structure of call-return logic in its methods. The menu pages take input from the player and use the state machine to change menus, as well as store settings information for the `Manager`. 

### `game_details.py`, `actor.py`, `striker.py`, etc.
Contains the `GameState` class and all of its member classes. This class creates the real-time state of the game while it is being played. It manages all changes to actors, such as the ball and CPU, based on user striker input from the fusion. 
