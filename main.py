import serial
import time
import arena
from threading import Thread
from sense import SensorInput


# Global for keeping track of which sensor to display data from
sensor_to_read = "temperature"

'''
Should mutate the cubes based on the sensor reading
'''

def start_serial():
    global sensor_to_read
    global reading_text

    # set up the serial line
    ser = serial.Serial('COM6', 9600)
    time.sleep(2)

    while (True):
        b = ser.readline()
        string_n = b.decode()
        string = string_n.rstrip()
        if (string):
            # if (string[0] == "T"):
            if (sensor_to_read == "temperature"):
                reading_text.update(text = "The temperature is: " + string)
            # elif (string[0] == "H"):
            elif (sensor_to_read == "humidity"):
                reading_text.update(text = "The humidity is: " + string)
                humidity_val = float(string.split()[2])

                # output_start = 1
                # output_end = 5
                # input_start = 33
                # input_end = 50
                # slope = (output_end - output_start) / (input_end - input_start)
                # output = output_start + slope * (humidity_val - input_start)
                #
                # humidity_cube_obj.update(scale = (0.2, output, 0.2))
            print(string)

        time.sleep(0.1)

    ser.close()


def scene_callback(msg):
    print("scene_callback: ", msg)

arena.init("arena.andrew.cmu.edu", "realm", "patrick_scene")#, scene_callback)

'''
Updates the cube colors (Corresponding to temperature, humidity, wireless)
and thereby the sensor data input source (TODO)
based on the corresponding virtual button pressed.
'''
def button_callback(event):
    global sensor_to_read
    if event.event_type == arena.EventType.mousedown:
        print("Source: ", event.object_id)
        if (event.object_id == "button_cube_temperature"):
            sensor_to_read = "temperature"
            for map_cube in first_floor_heatmap_cube_list:
                map_cube.update(color=(255, 0, 0))
        elif (event.object_id == "button_cube_humidity"):
            sensor_to_read = "humidity"
            for map_cube in first_floor_heatmap_cube_list:
                map_cube.update(color=(0, 255, 0))
        elif (event.object_id == "button_cube_wireless"):
            for map_cube in first_floor_heatmap_cube_list:
                map_cube.update(color=(0, 0, 255))


# For testing the number switching
reading_text = arena.Object(
        objName = "reading_",
        objType = arena.Shape.text,
        color = (255, 0, 0),
        location = (-5, 2, 0),
        text = "Hello World!"
    )




# Buttons for temperature, humidity, and wireless signal strength
button_cube_temperature = arena.Object(
        objName = "button_cube_temperature",
        objType = arena.Shape.cube,
        location= (-1.2,2.6,-8),
        scale = (0.2,0.5,0.5),
        clickable= True,
        callback = button_callback,
        color = (0,0,0)
)

button_cube_humidity = arena.Object(
        objName = "button_cube_humidity",
        objType = arena.Shape.cube,
        location= (-1.2,2.6,-7.5),
        scale = (0.2,0.5,0.5),
        clickable= True,
        callback = button_callback,
        color = (255, 255, 255)
)

button_cube_wireless= arena.Object(
        objName = "button_cube_wireless",
        objType = arena.Shape.cube,
        location= (-1.2,2.6,-7),
        scale = (0.2,0.5,0.5),
        clickable= True,
        callback = button_callback,
        color = (155, 155, 155)
)


# Heat map cubes, default color is red for now, red for temperature
default_map_cube_color = (255, 0 ,0)

# Only for the first floor
heatmap_cube_pos_list = [(-7,2,-2.5), (-5,2,-2.5), (-3,2,-2.5), # Missing (-9,2,-2.5) since it blocks the doorway
                         (-9,2,-4.5), (-7,2,-4.5), (-5,2,-4.5), (-3,2,-4.5),
                         (-9,2,-6.5), (-7,2,-6.5), (-5,2,-6.5), (-3,2,-6.5),
                         (-9,2,-8.5), (-7,2,-8.5), (-5,2,-8.5), (-3,2,-8.5)]

# Initialize all first floor cubes in the space
first_floor_heatmap_cube_list = []
for i, pos in enumerate(heatmap_cube_pos_list):
    first_floor_heatmap_cube_list.append(arena.Object(
                objName = "cube" + str(i),
                objType = arena.Shape.cube,
                location= pos,
                clickable= True,
                color = default_map_cube_color,
                data='{"material": {"opacity": 0.2}}'
        ))


thread = Thread(target = start_serial)

# start_serial() # Contains while loop so it goes here at the end
thread.start()
arena.handle_events()

thread.join()