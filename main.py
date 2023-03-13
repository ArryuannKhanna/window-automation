import cv2
import pycaw
import mediapipe
import handTrackingModule as HAND
import numpy as np
import pyautogui

# pycaw setup
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# opencv
cam = cv2.VideoCapture(0)
cam.set(3, 1080)
cam.set(4, 720)
# our module setup
detector = HAND.handDetector(detectionConfi=0.7, trackingConfi=0.7)


# variables
currentTime = 0
prevTime = 0
lmListR = []
boundaryBoxR = []
displayPercentage = 0
displayBar = 420
area = 0
colorVolume = (255, 96, 200)
maxLength = 100
minLenght = 10

wScreen, hScreen = pyautogui.size()
cTime, pTime = 0, 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0
mouseSmootheningFactor = 4
flag = True

while flag:
    success, img = cam.read()
    hands, img = detector.findHands(img)

    command = "No action"
    if hands:
        visibleHand = hands[0]
        if len(hands) == 1:
            if(visibleHand["type"] == "Left"):
                leftHand = hands[0]
                lmListL = leftHand["lmList"]
                boundaryBoxL = leftHand["bbox"]
                fingersL = detector.fingersUp(leftHand)
                fingersUpLeft = fingersL.count(1)
                
                if fingersUpLeft == 0:
                    command = "Volume Control"
            
                elif fingersUpLeft == 1:
                    command = "Do You Want To Exit ?"
           
        elif len(hands) == 2:
            if(hands[0]["type"] == "Right"):
                rightHand = hands[0]
                lmListR = hands[0]["lmList"]
                boundaryBoxR = hands[0]["bbox"]

                leftHand = hands[1]
                lmListL = hands[1]["lmList"]
                boundaryBoxL = hands[1]["bbox"]
                command = "no commnd"
            else:
                rightHand = hands[1]
                lmListR = hands[1]["lmList"]
                boundaryBoxR = hands[1]["bbox"]

                leftHand = hands[0]
                lmListL = hands[0]["lmList"]
                boundaryBoxL = hands[0]["bbox"]
           
            fingersL = detector.fingersUp(leftHand)
            fingersUpLeft = fingersL.count(1)
            
            if fingersUpLeft == 0:
                command = "Volume Control"
                if(len(lmListR) != 0):
                    area = boundaryBoxR[2] * boundaryBoxR[3] // 100
                    maxLength = 100
                    minLenght = 10
                    if 100 < area < 1000:
                        if 100 < area < 250:
                            maxLength = 100
                            minLenght = 10
                        else:
                            maxLength = 200
                            minLenght = 40
                   
                    length, lineInfo, img = detector.findDistance(
                        lmListR[4][0:2], lmListR[8][0:2], img)
                
                    displayBar = np.interp(
                        length, [minLenght, maxLength], [420, 69])
                    displayPercentage = np.interp(
                        length, [minLenght, maxLength], [0, 100])
                    incrementSteps = 5
                    displayPercentage = incrementSteps * \
                        round(displayPercentage / incrementSteps)
                    fingersR = detector.fingersUp(rightHand)
                    if fingersR[4]:
                        volume.SetMasterVolumeLevelScalar(
                            displayPercentage/100, None)
                        cv2.circle(img, (lineInfo[4], lineInfo[5]),
                                   6, (0, 0, 0), cv2.FILLED)  
                        cv2.putText(img, f'setting mode', (120, 69),
                                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
                        colorVolume = (255, 0, 0)
                    else:
                        colorVolume = (255, 0, 0)
                    if length < 50:
                        cv2.circle(img, (lineInfo[4], lineInfo[5]),
                                   6, (420, 69, 69), cv2.FILLED)
                # drawings
                cv2.rectangle(img, (50, 69), (75, 420), (9, 6, 9), 3)
                cv2.rectangle(img, (50, int(displayBar)), (75, 420),
                              (96, 40, 42), cv2.FILLED)
                currentVol = int(
                    volume.GetMasterVolumeLevelScalar()*100)
                cv2.putText(img, f'Volume:{int(currentVol)}%', (400, 69),
                            cv2.FONT_HERSHEY_PLAIN, 2, colorVolume, 2)
                cv2.putText(img, f'{int(displayPercentage)}%', (30, 450),
                            cv2.FONT_HERSHEY_PLAIN, 2, (9, 40, 9), 2)

            elif fingersUpLeft == 1:
                command = "Do You Want To Exit ?"
                if(len(lmListR) != 0):
                    length, lineInfo, img = detector.findDistance(
                        lmListR[4][0:2], lmListR[8][0:2], img)
                    if length < 20:
                        cv2.circle(img, (lineInfo[4], lineInfo[5]),
                                   6, (420, 69, 69), cv2.FILLED)
                        flag = False
                        print("EXITED")

    

    cv2.putText(img, str(command), (60, 100),
                cv2.FONT_HERSHEY_TRIPLEX, 1, (420, 0, 0), 2)
    cv2.imshow("I", img)
    cv2.waitKey(1)


