# DSP505Project

## Abstract
One of the most common and widespread security breaches affecting
organizations today is a social engineering attack known as tailgating (also
referred to as piggybacking). Tailgating is a physical security breach in
which an unauthorized person follows an authorized individual to enter a
typically secured area.
The repository proposes an idea to detect tailgating into a
restricted premise using computer vision techniques.
The idea proposed here makes use of an automated system which makes
use of a Single Shot Detector (SSD) in order to detect and classify humans
in a video segment. The humans segmented in the video are then tracked
using a tracking algorithm in order to detect movements and to find out
the number of people which enter the restricted area.
This count is then verified with the number of authorised accesses and for
a mismatch, the system could be programmed to alert about a possible
tailgating incident.

## Problem statement
Given a CCTV camera footage of a secured door entry, detect anyone
tailgating using an automated system. The system should segment
individuals from the video and detect whether they are tailgating or not.

## Installation and Usage
The code environment is given, which can be directly activated
then once activated, run the commmand
```bash
python3 apptk.py
```
to run the windows application created using Tkinter. Add the necessary inputs and click run.<br>
This will create another window over the inputs

## Implementation
The complete process can be divided into three phases namely:
1. **Object Detection:** Object detection, in computer vision
context, is defined as an ability to find specific objects of
interest in an image.
This phase includes the usage of a Single Shot Detector such
as MobileNet SSD which would detect if new objects have
entered the view. By using SSD, we only need to take one
single shot to detect multiple objects within the image.
For each new object detected we create an object tracker
with the new bounding box coordinates for which then we
find the centroid.
2. **Object Tracking:** Object tracking is the process of taking an
initial set of object detections such as bounding box
coordinates, creating a unique id for each detection and then
tracking each of the unique objects detected using the
centroid associated with each of the objects.
The object tracking algorithm relies on the Euclidean
distance between existing object centroids and new object
centroids captured in subsequent frames in the video. The
primary assumption of the centroid tracking algorithm is that
a given object will potentially move in between subsequent
frames, but the distance between the centroids for
frames F(t) and F(t+1) (for some arbitrary ‘t’) will
be smaller than all other distances between objects.
Therefore, if we choose to associate centroids with minimum distances between subsequent frames, we can build our
object tracker
3. **Tailgating tracking:**
In this phase the number of humans passing through the gate
which are detected in the frame is compared with the
number of authorised entries and for a mismatch the system
would raise an alert to the necessary authorities about the
possible tailgating.
The number of authorised entries can be found by the
number of card entries at the entry gate

The complete process flow diagram is shown below:
![Tailgating Process](/Assets/TailgatingDetection.png "Tailgating Process")

## Output
As shown in the output images, we have a pre-defined virtual gate through which people are passing through. <br>
Tailgates are only defined on people who are going out of the restricted area, that is, from top to bottom are not considered as tailgate
![Tailgating Output](/Assets/TGOutput.png "Tailgating Process")
![Tailgating Output](/Assets/TGOutput1.png "Tailgating Process")

Output are as shown in video and an alerting beep which will play when a tailgate is detected.
