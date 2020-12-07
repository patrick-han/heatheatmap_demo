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

