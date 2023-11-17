from collections import OrderedDict
from scipy.spatial import distance as dist
import numpy as np

class CentroidTrackingAlgorithm:
    def __init__(self,MaxDistance = 50,MaxFramesAfterDisappeared = 50):

        # MaxDistance => Max distance after which the object is classified as disappeared
        # MaxFramesAfterDisappeared => Max number of frames an object stays disappeared before it is de registered

        self.MaxDistance = MaxDistance
        self.MaxFramesAfterDisappeared = MaxFramesAfterDisappeared
        self.NextObjectID = 0  #Unique object ID Assigned to next object
        self.Objects = OrderedDict() #Objects dictionary to store objectid and centroid
        self.Disappeared = OrderedDict() # Keeping track whether object has disappeared or not

    def RegisterNewObjects(self,centroid):

        self.Objects[self.NextObjectID] = centroid
        self.Disappeared[self.NextObjectID] = 0  # Initialises Number of frames for hwich the object has disappeared as 0
        self.NextObjectID += 1  # Increments the next objectid so that no objects have the same id  

    def UnregisterDisappearedObject(self,objID):

        del self.Objects[objID]
        del self.Disappeared[objID]
    
    def UpdateObjectsInFrame(self,RectangleCoordinates):

        if len(RectangleCoordinates) == 0: # i.e. no objects are detected and every object has left the frame
            # Clear out all object previously registered
            for i in list(self.Disappeared.keys()):
                self.Disappeared[i] += 1
                if self.Disappeared[i] >= self.MaxFramesAfterDisappeared:
                    self.UnregisterDisappearedObject(i)
            return self.Objects
        else:
            InputObjectCentroids = np.zeros((len(RectangleCoordinates),2),dtype="int")  # To store every centroid for evry rectangle coordinates given

            for (i,(startX,startY,endX,endY)) in enumerate(RectangleCoordinates) :
                Centroid_X = int((startX + endX)/2.0)
                Centroid_Y = int((startY + endY)/2.0)

                InputObjectCentroids[i] = (Centroid_X,Centroid_Y) 

            if len(self.Objects) > 0:
                
                ListOfObjects = list(self.Objects.keys())
                ListOfCentroidOfObjects = list(self.Objects.values())

                # Calculating distances to associate objects and centroids
                D = dist.cdist(np.array(ListOfCentroidOfObjects),InputObjectCentroids)

                MinRow = D.min(axis = 1).argsort()
                MinCol = D.argmin(axis = 1)[MinRow]

                UsedRows = set()
                UsedColumns = set()

                for (i,j) in zip(MinRow,MinCol):

                    if D[i,j] > self.MaxDistance:
                        continue
                    elif (i in UsedRows) or (j in UsedColumns):
                        continue
                    else:

                        ObjID = ListOfObjects[i]
                        self.Objects[ObjID] = InputObjectCentroids[j]
                        self.Disappeared[ObjID] = 0
                        UsedColumns.add(j)
                        UsedRows.add(i)
                
                RowsNotUsed = set(range(0,D.shape[0])).difference(UsedRows)
                ColumnsNotUsed = set(range(0,D.shape[1])).difference(UsedColumns)

                # If number of centroids is greater than or equal to the number of detected centroids (.i.e. input centroids) then we can conclude some objects have disappeared
                if D.shape[0] >= D.shape[1]:

                    for i in RowsNotUsed:
                        ObjectID = ListOfObjects[i]
                        self.Disappeared[ObjectID] += 1

                        if self.Disappeared[ObjectID] >= self.MaxFramesAfterDisappeared:
                            self.UnregisterDisappearedObject(ObjectID)
                
                # else if number of centroids is lesser than the detected centroids register new objects with missing centroids
                else:
                    for j in ColumnsNotUsed:
                        self.RegisterNewObjects(InputObjectCentroids[j])


                return self.Objects
            
            else:
                for k in range(0,len(InputObjectCentroids)):
                    self.RegisterNewObjects(InputObjectCentroids[k])

        return self.Objects

                 
                





