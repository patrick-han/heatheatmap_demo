import serial
import time
import arena
from sense import SensorInput

# Current objective: Have two buttons represented by cubes, switch the color of another cube based on the button clicked

def scene_callback(msg):
    print("scene_callback: ", msg)

def button_callback(event):
    global map_cube
    global map_cube_color
    if event.event_type == arena.EventType.mousedown:
        print("Source: ", event.object_id)
        if (event.object_id == "button_cube_heat"):
            map_cube.update(color = (255,0,0))
        elif (event.object_id == "button_cube_humid"):
            map_cube.update(color = (0,255,0))

arena.init("arena.andrew.cmu.edu", "realm", "patrick_scene")#, scene_callback)

# start_serial(temperature_text, humidity_text, humidity_cube)

def start_serial(temperature_text_obj, humidity_text_obj, humidity_cube_obj):
    # set up the serial line
    ser = serial.Serial('COM6', 9600)
    time.sleep(2)

    while (True):
        b = ser.readline()
        string_n = b.decode()
        string = string_n.rstrip()
        if (string):
            if (string[0] == "T"):
                temperature_text_obj.update(text = "The temperature is: " + string)
            elif (string[0] == "H"):
                humidity_text_obj.update(text = "The humidity is: " + string)
                humidity_val = float(string.split()[2])

                output_start = 1
                output_end = 5
                input_start = 33
                input_end = 50
                slope = (output_end - output_start) / (input_end - input_start)
                output = output_start + slope * (humidity_val - input_start)

                humidity_cube_obj.update(scale = (0.2, output, 0.2))
            print(string)

        time.sleep(0.1)

    ser.close()



button_cube_heat = arena.Object(
        objName = "button_cube_heat",
        objType = arena.Shape.cube,
        location= (6,0,8),
        clickable= True,
        callback = button_callback,
        color = (0,0,0)
)

button_cube_humid = arena.Object(
        objName = "button_cube_humid",
        objType = arena.Shape.cube,
        location= (6,0,10),
        clickable= True,
        callback = button_callback,
        color = (255, 255, 255)
)
map_cube_color = "red"
map_cube = arena.Object(
        objName = "map_cube",
        objType = arena.Shape.cube,
        location= (6,0,6),
        clickable= True,
        color = (255, 0, 0)
)

arena.handle_events()