
# `fusion` Documentation
## Overview
This folder contains the file that fuses the IMU and camera data

## Code
### `sensor_fusion.py`
Contains the code that runs on another separate thread, takes in the data from the camera and IMU to determine a final position.

## Potential Bugs and Limitations

- Synchronization Issues: Ensuring that data from the camera and the IMU are properly synchronized can be challenging. Discrepancies in timestamps or delays in data streams can lead to inaccuracies in the fused position.
- Algorithm Complexity: The complexity of sensor fusion algorithms can introduce computational overhead, potentially impacting the system's performance, especially on less powerful hardware.

## Future Improvements
- Algorithm Optimization: Continuous refinement and optimization of the fusion algorithm can improve both the accuracy of the position estimates and the system's overall performance, our current one is very simple
