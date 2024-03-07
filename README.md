# Virtual Air Hockey
Note: graphics include flashing colors.
## Overview
This project aims to recreate air hockey virtually using a camera and an integrated IMU
## Setup
In order to run the game, you need to install ably, pygame, numpy, opencv, and matplotlib.
To begin, you'll need to clone this repository 
```bash
git clone
```
## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the required dependencies within requirements.txt .

```bash
pip install -r requirements.txt
```

## Runtime ##
After everything is installed without errors, run this command to start the game
```bash
python3 controller.py 
```
## Troubleshooting ##
Lighting Calibration: Currently, lighting calibration must be done manually. The next planned stage in our development is implementing this feature, so this will not be an issue as soon as next week; but currently, if the frames brought up by the game that show camera feedback seem to be picking up too many background objects, you will need to adjust the thresholding values in \disc\capture.py. These values were tuned to the lab environment, so they should work well enough for operation in the lab; but if they cause instability, try adjusting the values based on what is getting picked out of your camera feed (to enable the camera feedback ensure the following lines are not commented out). If too many blacks are getting picked up, try increasing the lower_green V threshold (the third value, HSV color space black corresponds to 0 in value); if too many whites are being detected lower the upper_green V threshold (white corresponds to 255 in value using openCV’s scale). If too many blues are being detected try lowering the upper_green H threshold (the first value, H around 110 is blue). If too many reds or yellows are detected, raise lower_green H threshold (H around 25 is orange). When adjusting, we typically test in increments of five or ten, I.E. if you fall into any of the above cases, adjust the value by five or ten in the direction indicated. Once again, this will be an automatic process by next week. But for now this is how to keep it stable.


Camera Numbering: The current code does not have any means to detect which camera it should be using. Essentially, this will depend on a number of factors. Does your computer have an integrated webcam? Are you running any software that creates a virtual webcam (such as OBS)? We have planned features to automatically determine the correct camera, or in the case of using a raspberry pi 4 this number will always be 0; but for now, you may need to change the number inside the parenthesis for the below bit of code. If your laptop or computer doesn’t have any additional cameras, this number will be 0. If it has any others it will typically be the number of additional cameras (I.E. if your machine has two integrated webcams, you would change the number to a 2). This does get slightly messier if you are running a virtual webcam, but generally the same rule applies, so long as you don’t plug in the IRL webcam before the virtual webcam is initialized.

Delay/Lag: If you are experiencing lag, try closing other memory intensive applications such as web browsers. 

Pygame Window Freezing: The pygame window can freeze on certain machines if you click into it with your mouse. Simply don’t click with your mouse while the game is running. This appears to be a mac vs. windows issue, that we are working to resolve.

## Codebase
![code](https://github.com/180D-FW-2023/Team8/blob/master/assets/code_diagram.png)
## References
Title Font: https://www.fontspace.com/pixel-digivolve-font-f22012 (Freeware license)
