
# `imu` Documentation
## Overview
This folder contains the file that reads IMU data

## Code
### `imu_reading.py`
Contains the main code that runs on a separate thread, connects to Ably and pulls the IMU data from the server.

## Implementation

### Keys

We currently use a global, rate-unlimited key. This is a security flaw, has been redacted in the submission, and should be moved to an AWS Secrets that are dynamically loaded.