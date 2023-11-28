from TailgatingTracking.CentroidTrackingAlgorithm import CentroidTrackingAlgorithm
from TailgatingTracking.TrackableObject import TrackableObject
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import dlib
import cv2
import pandas as pd
from pydub import AudioSegment
from pydub.playback import play


ap = argparse.ArgumentParser()
ap.add_argument("--prototxt", required=True,help="path to Caffe prototxt file")
ap.add_argument("--caffemodel", required=True,help="path to Caffe .caffemodel file")
ap.add_argument("--input", type=str,help="path to input video file")
ap.add_argument("--output", type=str,help="path to output video file")
ap.add_argument("-cl", "--confidence", type=float, default=0.4,help="minimum probability to remove weak detections")
ap.add_argument("-sf", "--skip-frames", type=int, default=30,help="number of frames skipped")
args = vars(ap.parse_args())

CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat","bottle", "bus", "car", "cat", "chair", "cow", "diningtable","dog", "horse", "motorbike", "person", "pottedplant", "sheep","sofa", "train", "tvmonitor"]

print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["caffemodel"])

if not args.get("input", False):
    print("starting video stream...")
    vs = VideoStream(src=0).start()

else:
	print("opening video file...")
	vs = cv2.VideoCapture(args["input"])

videowriter = None

WidthOfVideo = None
HeightOfVideo = None

csvData = []
fields = ["Time","Count"]
df2 = pd.read_csv("./Inputs/CardInputs.csv", usecols = ['Card Entry'])

CentroidTracker = CentroidTrackingAlgorithm(MaxFramesAfterDisappeared=40, MaxDistance=50)
trackers = []
trackableObjects = {}
sound = AudioSegment.from_file("./Inputs/beep-03.mp3")


totalFrames = 0
totalCount = 0
TotalTimeElapsed = 0
#TotalCardEntries = 0
EntriesPerSec = 0
TotalTailgates = 0

fps = FPS().start()

while True:

    CapturedFrame = vs.read()
    CapturedFrame = CapturedFrame[1] if args.get("input", False) else CapturedFrame

    if args["input"] is not None and CapturedFrame is None:
	    break

    CapturedFrame = imutils.resize(CapturedFrame, width=1000)
    rgb = cv2.cvtColor(CapturedFrame, cv2.COLOR_BGR2RGB)

    if WidthOfVideo is None or HeightOfVideo is None:
	    (HeightOfVideo, WidthOfVideo) = CapturedFrame.shape[:2]

    if args["output"] is not None and videowriter is None:
	    fourcc = cv2.VideoWriter_fourcc(*"MJPG")
	    videowriter = cv2.VideoWriter(args["output"], fourcc, 30,(WidthOfVideo, HeightOfVideo), True)

    status = "Waiting"
    rects = []

    videofps = int(vs.get(cv2.CAP_PROP_FPS))
    TotalTimeElapsed = int(totalFrames / videofps)
    row = [TotalTimeElapsed,totalCount]
    csvData.append(row)
    
    cv2.putText(CapturedFrame, "Total Tailgates = " + str(TotalTailgates), (150, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 2, cv2.LINE_4)
    if totalFrames % args["skip_frames"] == 0:
        status = "Detecting"
        trackers = []
        #TotalCardEntries = TotalCardEntries + df2['Card Entry'][TotalTimeElapsed]
        blob = cv2.dnn.blobFromImage(CapturedFrame, 0.007843, (WidthOfVideo, HeightOfVideo), 127.5)
        net.setInput(blob)
        detections = net.forward()
        
        for i in np.arange(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            
            if confidence > args["confidence"]:
                idx = int(detections[0, 0, i, 1])
                if CLASSES[idx] != "person":
                    continue
                box = detections[0, 0, i, 3:7] * np.array([WidthOfVideo, HeightOfVideo, WidthOfVideo, HeightOfVideo])
                (startX, startY, endX, endY) = box.astype("int")
                tracker = dlib.correlation_tracker()
                rect = dlib.rectangle(startX, startY, endX, endY)
                tracker.start_track(rgb, rect)
                trackers.append(tracker)
        
        '''if(TotalCardEntries < totalCount):
            print("ALERT - TAILGATING TAKEN PLACE at ",TotalTimeElapsed,TotalCardEntries,totalCount)
            TotalCardEntries = totalCount 

        elif(TotalCardEntries > totalCount):
            TotalCardEntries = totalCount'''
        try:
            if (TotalTimeElapsed - 1 >= 0) and ((df2['Card Entry'][TotalTimeElapsed - 1]) and (EntriesPerSec > df2['Card Entry'][TotalTimeElapsed - 1])):
                print("ALERT TAILGATING AT ",TotalTimeElapsed - 1)
                TotalTailgates += 1
                # playsound.playsound('./Inputs/beep-03.mp3')
                play(sound)
                EntriesPerSec = 0
        except KeyError:
            print("No input for card entry for time = ",TotalTimeElapsed)
            #break
        EntriesPerSec = 0
    else:
	    for tracker in trackers:

		    status = "Tracking"

		    tracker.update(rgb)
		    pos = tracker.get_position()

		    startX = int(pos.left())
		    startY = int(pos.top())
		    endX = int(pos.right())
		    endY = int(pos.bottom())

		    rects.append((startX, startY, endX, endY))

    cv2.line(CapturedFrame, (0, HeightOfVideo // 2), (WidthOfVideo, HeightOfVideo // 2), (0, 255, 255), 2)

    objects = CentroidTracker.UpdateObjectsInFrame(rects)

    for (objectID, centroid) in objects.items():
        to = trackableObjects.get(objectID, None)
        if to is None:
            to = TrackableObject(objectID, centroid)
        else:
            y = [c[1] for c in to.centroids]
            direction = centroid[1] - np.mean(y)
            to.centroids.append(centroid)
            if not to.counted:
                if direction > 0 and centroid[1] > HeightOfVideo // 2:
                    totalCount += 1
                    EntriesPerSec += 1
                    if not df2['Card Entry'][TotalTimeElapsed]:
                        print("ALERT TAILGATING at ",TotalTimeElapsed)
                        # playsound.playsound('./Inputs/beep-03.mp3')
                        play(sound)
                        TotalTailgates += 1
                    to.counted = True
        trackableObjects[objectID] = to
        text = "ID {}".format(objectID)
        cv2.putText(CapturedFrame, text, (centroid[0] - 10, centroid[1] - 10),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.circle(CapturedFrame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)

    info = [
		("Count", totalCount),
		("Status", status),
        ("Time",TotalTimeElapsed)
	]

    for (i,(k,t)) in enumerate(info):
	    text = "{} {}".format(k,t)
	    cv2.putText(CapturedFrame, text, (10, HeightOfVideo - ((i * 20) + 20)),cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    if videowriter is not None:
	    videowriter.write(CapturedFrame)

    cv2.imshow("Frame", CapturedFrame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
	    break
    
    totalFrames += 1
    fps.update()

fps.stop()

if videowriter is not None:
	videowriter.release()

if not args.get("input", False):
	vs.stop()

else:
	vs.release()

cv2.destroyAllWindows()

'''for i in csvData:
    print(i)'''
csvData = [list(x) for x in set(tuple(x) for x in csvData)]
csvData.sort()
CsvDataFrame = pd.DataFrame(csvData,columns=fields)
CsvDataFrame = CsvDataFrame.drop_duplicates(subset='Time', keep="last")
CsvDataFrame.to_csv('./Outputs/temp.csv',index=False,header=fields)


listdf2 = df2.values.tolist()
df2col = [i for j in listdf2 for i in j]
df = pd.read_csv("./Outputs/temp.csv")
if(len(df.index) == len(df2.index)):
    df['Card Values'] = df2col
    fields.append("Card Values")
    df.to_csv('./Outputs/Log.csv',index=False,header=fields)
elif(len(df.index) < len(df2.index)):
    print("More card inputs than inputs in video.....\nUsing only part of card inputs")
    df2col = df2col[0:len(df.index)]
    df['Card Values'] = df2col
    fields.append("Card Values")
    df.to_csv('./Outputs/Log.csv',index=False,header=fields)
else:
    print("lesser card inputs than inputs in video.....\nWill use NaN values")
    df = pd.concat([df,df2], ignore_index=True, axis=1)
    fields.append("Card Values")
    df.to_csv('./Outputs/Log.csv',index=False,header=fields)
