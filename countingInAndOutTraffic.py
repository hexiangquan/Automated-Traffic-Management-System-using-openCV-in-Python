import cv2
import sys
import math
import time as t

import numpy as np
import scipy
# import math

# video_source = "tra2.avi"
video_source = "car3.mp4"
# video_source = "Alibi.avi"

# Set up tracker.
# Instead of MIL, you can also use
# BOOSTING, KCF, TLD, MEDIANFLOW or GOTURN
TrackerType = "MEDIANFLOW"

cascadePath = "car4-1.xml"

def cent_dist(a,b):
    temp = math.sqrt( pow((a[1]-b[1]),2)+pow((a[0]-b[0]),2))
    return temp

def checkOverlap(a,b):
    (x1, y1, w1, h1) = a
    (x2, y2, w2, h2) = b

    if(x1 < (x2 +w2/2)):
        if(x1+w1 > (x2 +w2/2)):
            if(y1 < (y2 +h2/2)):
                if(y1+h1 > (y2 +h2/2)):
                    return True
    if(x2 < (x1 +w1/2)):
        if(x2+w2 > (x1 +w1/2)):
            if(y2 < (y1 +h1/2)):
                if(y2+h2 > (y1 +h1/2)):
                    return True
    return False

def removeOverlaps(objectsFoundLocal):
    objectsFoundTemp = []
    for i in range(0, len(objectsFoundLocal)):
        matchBool = False
        for j in range(i+1, len(objectsFoundLocal)):
            if (checkOverlap(objectsFoundLocal[i],objectsFoundLocal[j])):
                matchBool = True
        if not matchBool:
            objectsFoundTemp.append(objectsFoundLocal[i])
    return objectsFoundTemp

tracker          = {}
status           = {}
trackerLifeTime  = {}
bbox             = {}
bboxOld          = {}
ok               = {}
centroid_car     = {}
centroid_tracker = {}
Dir              = {}

no_trackers=15
for i in range(0,no_trackers):
    trackerLifeTime[i] = 0
    tracker[i]=cv2.Tracker_create(TrackerType)
    status[i] = "OFF"
    ok[i]=False

#cascade init
car_cascade = cv2.CascadeClassifier(cascadePath)

# Video Initialize
video = cv2.VideoCapture(video_source)

# Exit if video not opened.
if not video.isOpened():
    print ("Could not open video")
    sys.exit()

# Read first frame.
ok1, frame = video.read()
ok1, frame = video.read()
ok1, frame = video.read()
ok1, frame = video.read()
ok1, frame = video.read()
ok1, frame = video.read()
ok1, frame = video.read()
ok1, frame = video.read()
ok1, frame = video.read()
ok1, frame = video.read()
# frame = frame[:,(frame.shape[1]/2):frame.shape[1]].copy()
frameTrackersPrev = frame.copy()
frameHaarPrev     = frame.copy()
if not ok1:
    print ('Cannot read video file')
    sys.exit()

#convt gray
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#detect cars
cars = car_cascade.detectMultiScale(gray, 1.3, 5)


#Remove overlaping cars
cars = removeOverlaps(cars)
# cars = esvm_nms(cars, 30)

#initialize all tracker related arrays
for i in range(0, no_trackers):
    bbox[i]    = (0, 0, 0, 0)
    bboxOld[i] = (0, 0, 0, 0)
    tracker[i] = cv2.Tracker_create(TrackerType)
    ok[i]      = tracker[i].init(frame, bbox[i])
    tracker[i] = cv2.Tracker_create(TrackerType)
    status[i]  = "OFF"
    Dir[i]     = "IN"
    ok[i]      = False

trackersOn     = 0  #counter for No of active trackers
carCount       = 0     #car counter
carCountIn     = 0     #car counter
carCountOut    = 0     #car counter
stTime         = t.time()
pause          = False
absoluteStTime = t.time()
totalFrames    = 0
while True:
    # Read a new frame
    # print("________________NEW LOOP_____________________________________________________________________________________________________________________________________")
    # print("________________NEW LOOP_____________________________________________________________________________________________________________________________________")
    # print("________________NEW LOOP_____________________________________________________________________________________________________________________________________")
    # print("________________NEW LOOP_____________________________________________________________________________________________________________________________________")
    # print("________________NEW LOOP_____________________________________________________________________________________________________________________________________")
    # print("")
    # print("")
    ok1, frame = video.read()
    # frame = frame[:,(frame.shape[1]/2):frame.shape[1]].copy()
    frameHaar = frame.copy()
    frameTrackers = frame.copy()
    if not ok1:
        break

    #convt gray
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #detect cars
    cars = car_cascade.detectMultiScale(gray, 1.3, 5)
    #Remove overlaping cars
    cars = removeOverlaps(cars)

    # print("len(cars): ", len(cars))

    #prepare centroid of Haar cars
    i=0
    for (x,y,w,h) in cars:
        centroid_car[i]=(x+(w/2),y+(h/2))
        i+=1

    #prepare centroid of Tracker cars   (Not used for Computation. Used only for printing and debugging)
    for i in range(0,no_trackers):
        if status[i] != "OFF":
            temp = (bbox[i][0]+(bbox[i][2]/2),bbox[i][1]+(bbox[i][3]/2))
            # centroid_tracker[i]= temp
        else:
            centroid_tracker[i]=(0,0)

    # print ("car: ",     centroid_car)
    # print ("tracker: ", bbox,"\n\n")
    # print ("tracker: ", centroid_tracker,"\n\n")
    for i in range(0,len(cars)):
        matchFound = False
        for j in range (0,no_trackers):     #checck if any trackers are already tracking the haar car
            if status[j] == "DUP":
                continue
            if status[j] == "OFF":
                continue
            # if status[j] == "LOST":
            #     print ( "klmvkvs")
            #     bbox[j] = bboxOld[j]
            #     print ("bbox = ", bbox)
            #     print ("bboxOld = ", bboxOld)
            if ((checkOverlap(cars[i],bbox[j])) | (checkOverlap(bbox[j],cars[i]))):
                    # print ("Overlap >> CAR: ", cars[i], "TRACKER: ", bbox[j], end = '  ')
                    # print ("      >> CAR: ", i, "TRACKER: ", j)
                    if((cars[i][2] < bbox[j][2]) & (matchFound == False)):
                    # if((matchFound == False)):
                        p1 = (int(bbox[j][0]), int(bbox[j][1]))
                        p2 = (int(bbox[j][0] + bbox[j][2]), int(bbox[j][1] + bbox[j][3]))
                        # cv2.putText(frameTrackers,(str)(j),(int(bbox[j][0] + 5) ,int(bbox[j][1] + 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.75,(0, 0, 255),2)
                        # cv2.putText(frameTrackers,(str)(status[j][0]),(int(bbox[j][0] + 5) ,int(bbox[j][1] - 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.75,(0, 0, 255),2)
                        # print ( "FTrack Text: car: ", i,"tr: ", j, " Col: Red")
                        # cv2.rectangle(frameTrackers, p1, p2, (0,0,255), 1)
                        if status[j] == "NEW":
                            continue
                        #     status[j] = "UD"
                        tracker[j]=cv2.Tracker_create(TrackerType)
                        temp = (cars[i][0], cars[i][1], cars[i][2], cars[i][3])
                        bbox[j] = temp
                        ok[j] = tracker[j].init(frame, temp)
                        # if status[j] == "LOST":
                        #     # status[i] = "LOST"
                        #     # print ("trackerOn -= 1", i, "st = ", status[i])
                        #     trackersOn += 1
                        #     pause = True
                        #     carCount -= 1
                        #     if(Dir[j] == "IN"):
                        #         carCountIn  -= 1
                        #     elif(Dir[j] == "OUT"):
                        #         carCountOut -= 1
                        # print ("Tracker Updated TrNo: ", j, "CarNo: ", i)
                        status[j] = "HUD"
                        matchFound = True
                        p1 = (int(bbox[j][0]), int(bbox[j][1]))
                        p2 = (int(bbox[j][0] + bbox[j][2]), int(bbox[j][1] + bbox[j][3]))
                        # cv2.putText(frameTrackers,(str)(j),(int(bbox[j][0] + 5) ,int(bbox[j][1] + 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.75,(255, 0, 0),2)
                        # cv2.putText(frameTrackers,(str)(status[j][0]),(int(bbox[j][0] + 5) ,int(bbox[j][1] - 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.75,(255, 0, 0),2)
                        # print ( "FTrack Text: car: ", i,"tr: ", j, " Col: Blue")
                        # cv2.rectangle(frameTrackers, p1, p2, (255,0,0), 1)
                        # cv2.imshow('Haar', frameHaar)
                        # cv2.imshow('Trackers', frameTrackers)
                        # pause = True
                        # continue
                    # cv2.putText  (frameHaar, (str)(i),(cars[i][0] + 5 , cars[i][1] + 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    # print ( "FHaar Text: car: ", i,"tr: ", j, " Col: Green")
                    cv2.rectangle(frameHaar, (cars[i][0], cars[i][1]), (cars[i][0]+cars[i][2], cars[i][1]+cars[i][3]), (0, 255, 0), 2)
                    matchFound = True
        if matchFound == False:             #if not already tracked, create new tracker
            for k in range(0,no_trackers):
                if status[k] == "OFF":               #check if tracker is available
                    # print ("Init New  >> CAR: ", cars[i], end = '  ')
                    # print ("NEW >> CAR: ", i, "TRACKER: ", k)
                    # for j in range (0,no_trackers):
                    #     print("car ",cars[i],": trck ",bbox[j]," = ",checkOverlap(cars[i],bbox[j]))
                    # cv2.putText(frameHaar,(str)(i),(cars[i][0] + 5 ,cars[i][1] + 20), cv2.FONT_HERSHEY_SIMPLEX, 1,(0, 0, 255),2)
                    # print ( "FHaar Text: car: ", i,"tr: ", j, " Col: Green")
                    cv2.rectangle(frameHaar, (cars[i][0], cars[i][1]), (cars[i][0]+cars[i][2], cars[i][1]+cars[i][3]), (0, 0, 255), 2)
                    trackerLifeTime[k] = 0
                    tracker[k]=cv2.Tracker_create(TrackerType)
                    temp = (cars[i][0], cars[i][1], cars[i][2], cars[i][3])
                    bbox[k] = temp
                    ok[k] = tracker[k].init(frame, temp)
                    temp = (cars[i][0], cars[i][1], cars[i][2], cars[i][3])
                    bbox[k] = temp
                    trackersOn += 1
                    status[k] = "NEW"
                    break
    # print("\n\n")

    # Update tracker
    # print ("st = ", status)
    for i in range(0,no_trackers):
        if   status[i] == "OFF":      #If tracker is OFF do not update
            # print (i, ": OFF ", end='. ')
            pass
        elif status[i] == "UD":      #If tracker is OFF do not update
            bboxOld[i] = bbox[i]
            # print (i, ": UPD", end='. ')
            if((bbox[i][0] + bbox[i][2]/2) < (frame.shape[1]/2)):
                Dir[i] = "OUT"
            else:
                Dir[i] = "IN"
            ok[i], bbox[i] = tracker[i].update(frame)
            trackerLifeTime[i] += 1
            if not ok[i]:
                status[i] = "LOST"
                # print ("trackerOn -= 1", i, "st = ", status[i])
                trackersOn -= 1
                pause = True
                carCount += 1
                if(Dir[i] == "IN"):
                    carCountIn  += 1
                elif(Dir[i] == "OUT"):
                    carCountOut += 1
            elif bbox[i][2]<20:     #Out Of Sight (Too Small)
                status[i] = "LOST"
                # print ("trackerOn -= 1", i, "st = ", status[i])
                trackersOn -= 1
                carCount += 1
                if(Dir[i] == "IN"):
                    carCountIn  += 1
                elif(Dir[i] == "OUT"):
                    carCountOut += 1
                pause = True
                ok[i]=False
        elif status[i] == "NEW":      #If tracker is NEw do not update
            # print (i, ": NEW", end='. ')
            status[i] = "UD"
        elif status[i] == "HUD":      #If tracker is recently updated from Haar do not update
            # print (i, ": NEW", end='. ')
            status[i] = "UD"
        elif status[i] == "DUP":      #If tracker is duplicate do not update
            # print (i, ": DUP ", end='. ')
            status[i] = "OFF"
            bbox[i] == (0,0,0,0)
            ok[i]=False
        elif status[i] == "LOST":      #If tracker is LOST do not update
            # print (i, ": LOST ", end='. ')
            status[i] = "OFF"
            bbox[i] == (0,0,0,0)
            ok[i]=False

    # print ("")
    # print ("ok = ",ok)
                
    # Remove Duplicate Trackers
    # trackersTemp = {}
    for i in range(0, len(bbox)):
        if(bbox[i] == (0,0,0,0)):
            continue
        if(status[i] == "OFF"):
            continue
        matchBool = False
        for j in range(i+1, len(bbox)):
            if(bbox[j] == (0,0,0,0)):
                continue
            if(status[j] == "OFF"):
                continue
            if (checkOverlap(bbox[i],bbox[j])):
                # print ("Dupl Tracker >> Track1: ", bbox[i], "Track2: ", bbox[j], end = '  ')
                # print ("      >> Tr1: ", i, "Tr2: ", j)
                # print ("initial Status: (i)", i, ": ", status[i], " (j)", j, ": ", status[j])
                status[i] = "DUP"
                trackersOn -= 1
                bbox[i] == (0,0,0,1)
                matchBool = True
    for i in range(0,no_trackers):
        if ok[i]:
            p1 = (int(bbox[i][0]), int(bbox[i][1]))
            p2 = (int(bbox[i][0] + bbox[i][2]), int(bbox[i][1] + bbox[i][3]))
            if((status[i] == "UD")):
                # cv2.putText(frameTrackers,(str)(i),(int(bbox[i][0] + 5) ,int(bbox[i][1] + 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.75,(0, 255, 0),2)
                # cv2.putText(frameTrackers,(str)(status[i][0]),(int(bbox[i][0] + 5) ,int(bbox[i][1] - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.75,(0, 255, 0),2)
                # print ( "FTrack Text: car: ", i,"tr: ", j, " Col: Green")
                cv2.rectangle(frameTrackers, p1, p2, (0,255,0), 1)
            # elif((status[i] == "NEW")):
            #     cv2.putText(frameTrackers,(str)(i),(int(bbox[i][0] + 5) ,int(bbox[i][1] + 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.75,(255, 255, 0),2)
            #     cv2.putText(frameTrackers,(str)(status[i][0]),(int(bbox[i][0] + 5) ,int(bbox[i][1] - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.75,(255, 255, 0),2)
            #     print ( "FTrack Text: car: ", i,"tr: ", j, " Col: Blue-Green")
            #     cv2.rectangle(frameTrackers, p1, p2, (255,0,0), 1)
            #     print ("NEW")
            #     pause = True

    # Display results
    cv2.putText(frameTrackers,(str)(carCountOut),(int(30 ) ,int(110)), cv2.FONT_HERSHEY_SIMPLEX, 2,(0, 0, 255),3)
    cv2.putText(frameTrackers,(str)(carCount   ),(int(300) ,int(110)), cv2.FONT_HERSHEY_SIMPLEX, 2,(0, 0, 255),3)
    cv2.putText(frameTrackers,(str)(carCountIn ),(int(530) ,int(110)), cv2.FONT_HERSHEY_SIMPLEX, 2,(0, 0, 255),3)
    # print ("st = ", status)


    ####### Uncomment These lines to see output of Trackers and Haar
    #In frame Haar red box shows a new detection.
    #The Green Haar Cascades change sizes But the function checkOverlaps checks to see if the detected car is a new detection

    cv2.imshow('Haar', frameHaar)
    cv2.imshow('Trackers', frameTrackers)
    # cv2.imshow('HaarPrev', frameHaarPrev)
    # cv2.imshow('TrackersPrev', frameTrackersPrev)
    #######

    frameTrackersPrev = frameTrackers.copy()
    frameHaarPrev     = frameHaar.copy()
    # print ("TrackLife:", trackerLifeTime)
    # print("trackersOn: ", trackersOn)
    # print("carCount: ", carCount)
    # Exit if ESC pressed
    if pause:
        key = cv2.waitKey(1) & 0xFF
        pause = False
        if ((key == ord('q')) | (key == 27)):
            break
    key = cv2.waitKey(1) & 0xFF
    if ((key == ord('q')) | (key == 27)):
        break
    endTime = t.time()
    totalFrames += 1
    # print ("FPS = ", int(1/(endTime-stTime)), "      FPS = ", int(totalFrames/(endTime-absoluteStTime)))
    # if(totalFrames == 1000):
    #     totalFrames = 0
    #     absoluteStTime = t.time()
    # if(t.time()-absoluteStTime > 20):
    #     break
    stTime = endTime
video.release()
cv2.destroyAllWindows()
