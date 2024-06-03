import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
import handTrackingModule as htm

pyautogui.FAILSAFE = False
##########################################
wCam, hCam = 640, 480
cTime = 0
pTime = 0
frameR = 100  # Frame Redction
smoothing = 7
plocX, plocY = 0, 0
clocX, clocY = 0, 0
##########################################

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
detector = htm.handDetector(maxHands=2)

wScr, hScr = pyautogui.size()
# print(wScr, hScr)

while True:

    # 1. find the landmark
    success, img = cap.read()

    if not success:
        break

    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)

    # 2. get the tip of the index and middle finger
    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]
        # print(x1, y1, x2, y2)

        # 3. check which finger are up
        fingers = detector.fingersUp()
        # print(fingers)

        # 4. Only Index finger Moving : Mode
        if fingers[1] == 1 and fingers[2] == 0:
            # 5. convert conrdinate
            cv2.rectangle(img, (frameR, frameR), (wCam - frameR,
                          hCam - frameR), (255, 255, 0), 2, cv2.LINE_4)
            # x3 = np.interp(x1, (frameR, wCam-frameR), (0, wScr))
            # y3 = np.interp(x1, (frameR, hCam-frameR), (0, hScr))
            x3 = int(x1 * wScr / wCam)
            y3 = int(x1 * hScr / hCam)
            # print(x3, y3)

            # 6. Smoothen Values
            clocX = plocX + (x3 - plocX) / smoothing
            clocY = plocY + (x3 - plocY) / smoothing

            # 7. Move Mouse
            pyautogui.moveTo(wScr-clocX, clocY, duration=0.01)
            cv2.circle(img, (x1, y1), 10, (255, 0, 255),
                       cv2.FILLED, cv2.LINE_4)
            plocX, plocY = clocX, clocY
        # 8. Both Index and Middle finger are up: Clicking Mode
        if fingers[1] == 1 and fingers[2] == 1:
            # 9. Find distance between fingers
            length, img, lineInfo = detector.findDistance(8, 12, img)
            # print(length)
            # 10. Click mouse if distance short
            if length <= 40:
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 10, (0, 255, 0),
                           cv2.FILLED, cv2.LINE_4)
                pyautogui.click(lineInfo[4], lineInfo[5], duration=0.01)
                # pyautogui.leftClick(lineInfo[4], lineInfo[5], duration=0.01)

    # 11. Frame Rate
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, f"Fps: {str(int(fps))}", (20, 50),
                cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2, cv2.LINE_4)

    cv2.imshow("AI VIRTUAL MOUSE", img)

    if cv2.waitKey(1) & 0xff == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
