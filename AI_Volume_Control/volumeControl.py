import cv2
import time
import numpy as np
# import alsaaudio  # For volume

# For volume
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL

from handTrackingModule import handDetector

#####################################
pTime = 0
cTime = 0
valBar = 340
valPer = 0
#####################################

cap = cv2.VideoCapture(0)
cap.set(3, 540)
cap.set(4, 380)

detector = handDetector(maxHands=1)

# this code for linux
# m = alsaaudio.Mixer()
# vol = m.getvolume()
# vol = int(vol[0])

# Get the default audio playback device
# this code for windows
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

while True:
    success, img = cap.read()

    if not success:
        break

    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img, draw=False)

    if len(lmList) != 0:
        x1, y1 = lmList[4][1:]
        x2, y2 = lmList[8][1:]
        # print(x1, y1, x2, y2)

        fingers = detector.fingersUp()

        if fingers[0] == 1 and fingers[1] == 1:
            length, img, lineInfo = detector.findDistance(4, 8, img)

            # print(length)
            vol = np.interp(int(length), [50, 140], [0, 100])
            valBar = np.interp(int(length), [50, 140], [340, 140])
            valPer = np.interp(int(length), [50, 140], [0, 100])
            # m.setvolume(int(vol))
            volume.SetMasterVolumeLevelScalar(int(vol)/100, None)
            # print(int(vol)/100)

    cv2.rectangle(img, (40, 140), (75, 340), (255, 0, 0), 2)
    cv2.rectangle(img, (40, int(valBar)), (75, 340), (255, 0, 0), cv2.FILLED)
    cv2.putText(img, f"{str(int(valPer))} %", (40, 360),
                cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 2, cv2.LINE_4)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, f"Fps: {str(int(fps))}", (20, 50),
                cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2, cv2.LINE_4)

    cv2.imshow("Volume Controller", img)

    if cv2.waitKey(1) & 0xff == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
