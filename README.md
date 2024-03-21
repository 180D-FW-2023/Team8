# Virtual Air Hockey
Note: graphics include flashing colors.
## Overview
This project aims to recreate air hockey virtually using a camera and an integrated IMU

## Requirements
- A camera, preferably one that can be put flush and level with the play surface
- A computer, currently. We were having issues with our raspberry pi 4 installing openCV and other python modules; in the future all that will be necessary will be a monitor and cable to connect the raspberry pi to, but optionally a computer will remain compatible.
- The green Air Hockey Striker with integrated IMU

## Setup
1. Install python on your computer of choice.
*We personally use Anaconda as our package manager

3. Using the python and package manager installation method of your choice, install the following in any order: `ably`, `pygame`, `numpy`, and `opencv-contrib-python`. These installations can be performed by opening up your python command prompt and running pip install followed by the names listed above, one at a time individually.
 * Alternatively, use the package manager [pip](https://pip.pypa.io/en/stable/) to install the required dependencies within requirements.txt .
```bash
pip install -r requirements.txt
```

3. Clone this repository or download its code. 
*https://github.com/180D-FW-2023/Team8

## Runtime ##
After everything is installed without errors, run `controller.py` to start the game.
```bash
python3 controller.py 
```
## Troubleshooting ##
* OpenCV Issues: If Python is not able to find certain OpenCV modules, try uninstalling and reinstalling OpenCV, ensuring that opencv-contrib-python is the installed package, not   
* Delay/Lag: If you are experiencing lag, try closing other memory intensive applications such as web browsers.
* Unresponsive Key Presses: If you click a key in the menu and the screen does not change, try holding that key instead of tapping it.
* Pygame Window Freezing: The pygame window can freeze on certain machines if you click into it with your mouse. Simply don’t click with your mouse while the game is running. This appears to be a mac vs. windows issue.

## Codebase
![code](https://github.com/180D-FW-2023/Team8/blob/master/assets/code_diagram.png)
Each module is organzied into its own folder. Naviagte to each module's `readme.md` for more information about software details.

## References
### Fonts
* Title Font: https://www.fontspace.com/pixel-digivolve-font-f22012 (Freeware license)

### Sounds 
* Goal: https://freesound.org/people/deadrobotmusic/sounds/662694/ (Creative Commons 0)
* Win: https://freesound.org/people/tamakari/sounds/105046/ (Creative Commons 0)
* Lose: https://freesound.org/people/michalwa2003/sounds/391133/ (Creative Commons 0)
* Click: https://freesound.org/people/pan14/sounds/263128/ (Creative Commons 0)

