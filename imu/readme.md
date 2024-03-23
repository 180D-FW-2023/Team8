
# `imu` Documentation
## Overview
This folder contains the file that reads IMU data

## Code
### `imu_reading.py`
This script is the backbone of the IMU data handling process. Operating on a dedicated thread, it establishes a connection to Ably, a real-time data streaming platform, and continuously retrieves IMU data that has been published to the server. The design focuses on maintaining a constant, reliable flow of data while minimizing latency and ensuring data integrity.

Source and References

The threading model and IMU data retrieval methods are based on general Python multithreading practices and the official Ably Python SDK documentation.
Connection and data handling practices were guided by Ably's real-time messaging documentation.
## Implementation

### Keys

We currently use a global, rate-unlimited key. This is a security flaw, has been redacted in the submission, and should be moved to an AWS Secrets that are dynamically loaded.

## Potential Bugs and Limitations

- Security Vulnerability: The current use of a global, rate-unlimited key poses a significant security risk. Unauthorized access to this key could lead to data breaches or misuse of the IMU data streaming service.
- Dependency on External Services: The system's reliance on Ably for data transmission and AWS Secrets Manager for key management introduces potential points of failure. Network issues or service outages could disrupt the IMU data flow.
- Performance: slower systems, including intel-based macs, experienced minor lag when dealing with the several threads.

## Future Improvements

- Enhanced Security: Implementing dynamic key loading from AWS Secrets Manager will significantly improve the security posture by eliminating hard-coded credentials.
- Performance Optimization: Ongoing performance reviews and optimizations can reduce latency, improve data throughput, and ensure the system remains responsive under varying load conditions.