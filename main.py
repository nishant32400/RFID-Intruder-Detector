import os
import cv2
import face_recognition
import numpy as np
import time
import datetime
from twilio.rest import Client
import pynfc

# Replace with your Twilio account details
account_sid = "YOUR_ACCOUNT_SID"
auth_token = "YOUR_AUTH_TOKEN"
client = Client(account_sid, auth_token)

def send_alert(message):
    """Sends an SMS alert using Twilio."""
    client.messages.create(
        to="YOUR_PHONE_NUMBER",
        from_="YOUR_TWILIO_NUMBER",
        body=message
    )

def get_encoded_faces():
    """Encodes all faces in the faces directory."""
    encoded = {}
    for dirpath, dnames, fnames in os.walk("./faces"):
        for f in fnames:
            if f.endswith(".jpg") or f.endswith(".png"):
                face = face_recognition.load_image_file(os.path.join(dirpath, f))
                encoding = face_recognition.face_encodings(face)[0]
                encoded[f.split(".")[0]] = encoding
    return encoded

def unknown_image_encoded(img):
    """Encodes a face given the image file."""
    face = face_recognition.load_image_file(img)
    encoding = face_recognition.face_encodings(face)[0]
    return encoding

def classify_face(frame, faces, faces_encoded, known_face_names):
    """Classifies the face in the frame and returns the face names."""
    face_locations = face_recognition.face_locations(frame)
    unknown_face_encodings = face_recognition.face_encodings(frame, face_locations)

    face_names = []
    for face_encoding in unknown_face_encodings:
        matches = face_recognition.compare_faces(faces_encoded, face_encoding)
        name = "Unknown"
        face_distances = face_recognition.face_distance(faces_encoded, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]
        face_names.append(name)

        for (top, right, bottom, left), name in zip(face_locations, face_names):
            cv2.rectangle(frame, (left - 20, top - 20), (right + 20, bottom + 20), (255, 0, 0), 2)
            cv2.rectangle(frame, (left - 20, bottom - 15), (right + 20, bottom + 20), (255, 0, 0), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left - 20, bottom + 15), font, 1.0, (255, 255, 255), 2)
    return face_names

def read_rfid_sensor():
    """Reads RFID card and returns card ID."""
    clf = pynfc.Nfc()
    while True:
        tag = clf.poll()
        if tag:
            return tag.uid.hex()

# Example database linking RFID card IDs to face IDs
authorized_faces = {
    "authorized_rfid_id_1": "authorized_face_id_1",
    "authorized_rfid_id_2": "authorized_face_id_2"
}

cap = cv2.VideoCapture(0)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_fullbody.xml")

detection = False
detection_stopped_time = None
timer_started = False
SECONDS_TO_RECORD_AFTER_DETECTION = 5

frame_size = (int(cap.get(3)), int(cap.get(4)))
fourcc = cv2.VideoWriter_fourcc(*"mp4v")

faces = get_encoded_faces()
faces_encoded = list(faces.values())
known_face_names = list(faces.keys())

while True:
    _, frame = cap.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces_detected = face_cascade.detectMultiScale(gray, 1.3, 5)
    bodies = body_cascade.detectMultiScale(gray, 1.3, 5)

    rfid_detected = read_rfid_sensor()
    face_detected = len(faces_detected) > 0

    if rfid_detected and face_detected:
        face_names = classify_face(frame, faces, faces_encoded, known_face_names)
        if authorized_faces.get(rfid_detected) not in face_names:
            print("RFID and face do not match. Alerting!")
            send_alert("Intruder detected: RFID and face do not match!")
        else:
            print("Authorized access.")

    if len(faces_detected) + len(bodies) > 0:
        if detection:
            timer_started = False
        else:
            detection = True
            current_time = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
            out = cv2.VideoWriter(f"{current_time}.mp4", fourcc, 20, frame_size)
            print("Started Recording!")
    elif detection:
        if timer_started:
            if time.time() - detection_stopped_time >= SECONDS_TO_RECORD_AFTER_DETECTION:
                detection = False
                timer_started = False
                out.release()
                print('Stop Recording!')
        else:
            timer_started = True
            detection_stopped_time = time.time()

    if detection:
        out.write(frame)

    cv2.imshow("Camera", frame)

    if cv2.waitKey(1) == ord('q'):
        break

if 'out' in locals():
    out.release()
cap.release()
cv2.destroyAllWindows()
