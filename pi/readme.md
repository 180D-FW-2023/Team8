
# `pi` Documentation
## Overview
This folder contains the file that runs on the IMU, used for updating the IMU's calculated velocity. 

## Code
### `berryIMU3.py`
Contains the main file that connects to the IMU, and sends data over Ably

## Implementation

### Automate Run
Whatever hardware used, be it a Pi Zero or an alternative, it must be configured to automatically run when the Pi turns on.
There are several ways to do this (we used a script in the bootloader).
