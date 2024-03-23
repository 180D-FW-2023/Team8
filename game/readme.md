
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

## Potential Bugs and Limitations

- State Synchronization: Ensuring that the state machine in Launcher remains in sync with GameState activities can be challenging, particularly during rapid transitions or unexpected player actions.
- Performance: Real-time game state management, especially with complex interactions and graphics, may stress system resources, potentially leading to performance bottlenecks.

## Future Improvements

- Performance Optimization: Continuous performance assessments and optimizations can help mitigate potential lag or resource contention, especially in resource-intensive game scenes.
- Usability Enhancements: Incorporating player feedback to refine the UI/UX design of the menu system and gameplay feedback could significantly enhance the overall game experience.
- Expandability: Designing the system with extendibility in mind will allow for the easy addition of new game features, levels, and actors.