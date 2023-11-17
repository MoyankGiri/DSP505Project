class TrackableObject:
    def __init__(self,objectID,centroid):

        self.objectID = objectID  #unique id for object
        self.centroids = [centroid] #centroid list of object

        self.counted = False  #to check if the object is used or not