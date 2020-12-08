import serial
import time
import json
import random
import arena
from threading import Thread
from sense import SensorInput


# Global for keeping track of which sensor to display data from
sensor_to_read = "temperature"
# Heat map cubes, default color is green for now, green for humidity
default_map_cube_color = (255, 0, 0)

'''
Maps a value from one range to another
'''
def map_to_range(value, from_start, from_end, to_start, to_end):
    slope = (to_end - to_start) / (from_end - from_start)
    output = to_start + slope * (value - from_start)
    return output

'''
Should mutate the cubes based on the sensor reading
'''
def start_serial():
    global sensor_to_read
    global reading_text

    # set up the serial line
    ser = serial.Serial('COM6', 9600)
    time.sleep(2)

    while True:
        b = ser.readline()
        string_n = b.decode()
        string = string_n.rstrip()

        if string: # We don't care about blank lines
            if sensor_to_read == "temperature": # Only check for temperature if we've selected it
                if string[0] == "T":
                    reading_text.update(text = string)
                    temperature_val = float(string.split()[2])
                    # Map to opacity range based on estimated input range
                    output = map_to_range(temperature_val, 28.5, 31.0, 0.0, 1.0)
                    for map_cube in first_floor_heatmap_cube_list:  # Update all cube maps
                        # Add some uniform noise to simulate other sensors
                        output += random.uniform(-0.01, 0.01)
                        output = max(min(output, 1.0), 0.0)  # Clamp values for opacity
                        data_str = json.dumps({"material": {"opacity": output}})
                        map_cube.update(data=data_str)


            elif sensor_to_read == "humidity":
                if string[0] == "H":
                    reading_text.update(text = string)
                    humidity_val = float(string.split()[2])
                    # Map to opacity range based on estimated input range
                    output = map_to_range(humidity_val, 20.0, 50.0, 0.0, 1.0)
                    for map_cube in first_floor_heatmap_cube_list: # Update all cube maps
                        # Add some uniform noise to simulate other sensors
                        output += random.uniform(-0.05, 0.05)
                        output = max(min(output, 1.0), 0.0)  # Clamp values for opacity
                        data_str = json.dumps({"material": {"opacity": output}})
                        map_cube.update(data=data_str)

        time.sleep(0.1)

    ser.close()


def scene_callback(msg):
    print("scene_callback: ", msg)

arena.init("arena.andrew.cmu.edu", "realm", "patrick_scene")#, scene_callback)


'''
Turns the fan on and off
'''
fan_status = "off"
def fan_button_callback(event):
    global fan_obj
    global fan_status
    if event.event_type == arena.EventType.mousedown:
        if fan_status == "on":
            fan_status = "off"
            fan_obj.update(data='{"animation": { "property": "rotation", "to": "0 360 0", "loop": false, "dur": 0}}')
        elif fan_status == "off":
            fan_status = "on"
            fan_obj.update(data='{"animation": { "property": "rotation", "to": "0 360 0", "loop": true, "dur": 1000}}')


fan_obj = arena.Object(
        objName = "fan",
        url="store/users/patrickhan/m202a/fan.glb",
        objType=arena.Shape.gltf_model,
        scale=(0.5,0.5,0.5),
        location=(8,2,8),
        clickable=True,
        data='{"animation": { "property": "rotation", "to": "0 360 0", "loop": false, "dur": 0}}',
)

button_fan = arena.Object(
        objName = "button_fan",
        objType = arena.Shape.cube,
        location= (8,.5,8),
        scale = (0.5,0.5,0.5),
        clickable= True,
        callback=fan_button_callback,
        color = (0,0,0)
)

'''
Updates the cube colors (Corresponding to temperature, humidity, wireless)
and thereby the sensor data input source (TODO)
based on the corresponding virtual button pressed.
'''
def button_callback(event):
    global sensor_to_read
    if event.event_type == arena.EventType.mousedown:
        print("Source: ", event.object_id)
        if event.object_id == "button_cube_temperature":
            sensor_to_read = "temperature"
            for map_cube in first_floor_heatmap_cube_list:
                map_cube.update(color=(255, 0, 0))
        elif event.object_id == "button_cube_humidity":
            sensor_to_read = "humidity"
            for map_cube in first_floor_heatmap_cube_list:
                map_cube.update(color=(0, 255, 0))
        elif event.object_id == "button_cube_wireless":
            for map_cube in first_floor_heatmap_cube_list:
                map_cube.update(color=(0, 0, 255))


# For testing the number switching
reading_text = arena.Object(
        objName = "reading_text",
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
                data='{"material": {"opacity": 0.5}}'
        ))

thread = Thread(target = start_serial)
thread.start()
arena.handle_events()

thread.join()