# Face and RFID Based Intruder Detection System

This project is a security system that uses a webcam to detect faces and an RFID reader to verify access. When an unknown face is detected or the RFID card does not match the face, the system sends an alert through SMS using Twilio and records a video.

## Features
- Face detection and recognition
- RFID card reading and verification
- SMS alerts using Twilio
- Video recording upon detection of an intruder

## Requirements
- Python 3.x
- OpenCV
- face_recognition
- numpy
- pynfc (or any other RFID library you are using)
- RPi.GPIO (if using Raspberry Pi and MFRC522 RFID reader)
- Twilio

## Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/face-rfid-intruder-detection.git
    cd face-rfid-intruder-detection
    ```

2. Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

3. Set up Twilio:
    - Sign up for a Twilio account.
    - Get your Account SID, Auth Token, and a Twilio phone number.

4. Prepare face images:
    - Place face images in the `faces` directory. Ensure the image filenames match the face IDs used in the `authorized_faces` dictionary.

## Usage
1. Connect your RFID reader.
2. Run the script:
    ```bash
    python main.py
    ```

