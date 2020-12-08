import math
"""
Types of Sensors:
- temp
- humid
- gas
-

"""




class SensorInput:
    def __init__(self, _type, _value, _location):
        self.type = _type
        self.value = _value
        self.location = _location

"""
Calculates the distance between 2 points in 3-dimensional space
"""
def distance_3d(p1, p2):
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2 + (p2[2] - p1[2])**2)