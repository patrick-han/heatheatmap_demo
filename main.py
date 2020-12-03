import serial
import time
import arena
from sense import SensorInput

# Current objective: Have two buttons represented by cubes, switch the color of another cube based on the button clicked

def scene_callback(msg):
    print("scene_callback: ", msg)

arena.init("arena.andrew.cmu.edu", "realm", "patrick_scene")#, scene_callback)

def button_callback(event):
    if event.event_type == arena.EventType.mousedown:
        print("Source: ", event.object_id)
        if (event.object_id == "button_cube_temperature"):
            for map_cube in heatmap_cube_list:
                map_cube.update(color=(255, 0, 0))
        elif (event.object_id == "button_cube_humidity"):
            for map_cube in heatmap_cube_list:
                map_cube.update(color=(0, 255, 0))
        elif (event.object_id == "button_cube_wireless"):
            for map_cube in heatmap_cube_list:
                map_cube.update(color=(0, 0, 255))



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


# Buttons for temperature, humidity, and wireless signal strength
button_cube_temperature = arena.Object(
        objName = "button_cube_temperature",
        objType = arena.Shape.cube,
        location= (6,0,8),
        clickable= True,
        callback = button_callback,
        color = (0,0,0)
)

button_cube_humidity = arena.Object(
        objName = "button_cube_humidity",
        objType = arena.Shape.cube,
        location= (6,0,10),
        clickable= True,
        callback = button_callback,
        color = (255, 255, 255)
)

button_cube_wireless= arena.Object(
        objName = "button_cube_wireless",
        objType = arena.Shape.cube,
        location= (6,0,12),
        clickable= True,
        callback = button_callback,
        color = (155, 155, 155)
)


# Heat map cubes, default color is red for now
default_map_cube_color = (255, 0 ,0)
heatmap_cube1 = arena.Object(
        objName = "map_cube1",
        objType = arena.Shape.cube,
        location= (6,0,6),
        clickable= True,
        color = default_map_cube_color
)
heatmap_cube2 = arena.Object(
        objName = "map_cube2",
        objType = arena.Shape.cube,
        location= (6,2,6),
        clickable= True,
        color = default_map_cube_color
)
heatmap_cube_list = [heatmap_cube1, heatmap_cube2]

arena.handle_events()