
# `pi` Documentation
## Overview
This folder contains the file that runs on the IMU, used for updating the IMU's calculated velocity. 

## Code
### `berryIMU3.py`
This is the core script of the project. It establishes a connection to the IMU, collects data from it, and transmits this data over the Ably real-time messaging service. The script is designed to be both efficient and robust, ensuring that IMU data is captured and transmitted accurately and in real-time.

Source and References

The IMU connection and data handling techniques were adapted from OzzMaker's BerryIMU, a comprehensive guide and library for IMU modules on the Raspberry Pi.
Data transmission utilizes the Ably Python SDK, enabling real-time data streaming capabilities.
## Implementation

### Automate Run
Whatever hardware used, be it a Pi Zero or an alternative, it must be configured to automatically run when the Pi turns on.
There are several ways to do this (we used a script in the bootloader).

## Potential Bugs and Limitations

- Hardware Compatibility: The script is primarily designed for the BerryIMU v3.0. Adjustments may be needed for compatibility with other IMU models or revisions.
- Network Dependencies: The script's ability to transmit data relies on a stable network connection. Interruptions in connectivity may lead to data loss or delays.

## Future Improvements

- Error Handling: Enhance error handling mechanisms to better manage and recover from hardware or network failures.
- Modularity: Increase the code's modularity to facilitate easier adaptation for different IMU models and data transmission services.
