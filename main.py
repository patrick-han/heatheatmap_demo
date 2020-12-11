import serial
import time
import json
import random
import arena
from threading import Thread
from utils import distance_3d
from utils import send_alert

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

    # For fan control affecting the output
    global fan_obj
    global fan_status

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
                    output = map_to_range(temperature_val, 28.5, 31.0, 0.0, 0.90)
                    for map_cube in first_floor_heatmap_cube_list:  # Update all cube maps
                        # Add some uniform noise to simulate other sensors
                        output += random.uniform(-0.01, 0.01)
                        # If close enough to the fan, and if the fan is on, minus some number
                        if distance_3d(fan_obj.location, map_cube.location) < 4.0 and fan_status:
                            output -= 0.1

                        # Opacity (More Opaque = More hot)
                        output = max(min(output, 1.0), 0.1)  # Clamp values for opacity
                        data_str = json.dumps({"material": {"opacity": output}})
                        map_cube.update(data=data_str)

                        # Color (Red for Hot, Blue for Cold)
                        r_value = output * 255
                        b_value = 255 - r_value
                        map_cube.update(color=(r_value, 0, b_value))

                        # Size Update (Larger = Warmer)
                        size_output = 1.0 + output
                        size_output = max(min(size_output, 1.5), 1.0)
                        map_cube.update(scale = (size_output,size_output,size_output))

            elif sensor_to_read == "humidity":
                if string[0] == "H":
                    reading_text.update(text = string)
                    humidity_val = float(string.split()[2])
                    # Map to opacity range based on estimated input range
                    output = map_to_range(humidity_val, 20.0, 50.0, 0.0, 0.9)
                    for map_cube in first_floor_heatmap_cube_list: # Update all cube maps
                        # Add some uniform noise to simulate other sensors
                        output += random.uniform(-0.05, 0.05)
                        # If close enough to the fan, and if the fan is on, minus some number
                        if distance_3d(fan_obj.location, map_cube.location) < 4.0 and fan_status:
                            output -= 0.1

                        # Opacity (More Opaque = More humid)
                        output = max(min(output, 1.0), 0.1)  # Clamp values for opacity
                        data_str = json.dumps({"material": {"opacity": output}})
                        map_cube.update(data=data_str)

                        # Color (Blue for Moist, Green for Dry)
                        b_value = output * 255
                        g_value = 255 - b_value
                        map_cube.update(color=(0, g_value, b_value))

                        # Size Update (Larger = More moist)
                        size_output = 1.0 + output
                        size_output = max(min(size_output, 1.5), 1.0)
                        map_cube.update(scale=(size_output, size_output, size_output))

        time.sleep(0.1)

    ser.close()


def scene_callback(msg):
    print("scene_callback: ", msg)

arena.init("arena.andrew.cmu.edu", "realm", "patrick_scene")#, scene_callback)



'''
Stove
'''

'''
Turns the stove on and off
'''
stove_status = False
def stove_button_callback(event):
    global stove_status
    global stove_cube
    global stove_light
    global stove_text
    if event.event_type == arena.EventType.mousedown:
        if stove_status:
            stove_status = False
            stove_light.update(color = (0,0,0))
            stove_cube.update(data='{"material": {"opacity": 0.25}}')
            stove_cube.update(data='{"animation": { "property": "scale", "to": "1 1 1", "loop": false, "dur": 0}}')
        else:
            stove_status = True
            stove_light.update(color = (100,0,0))
            stove_cube.update(data='{"material": {"opacity": 0.80}}')
            stove_cube.update(data='{"animation": { "property": "scale", "to": "3 3 3", "loop": true, "dur": 1000}}')
            send_alert() # Comment this out when testing so you don't get spammed by emails

stove_obj = arena.Object(
        objName = "stove",
        url="store/users/patrickhan/m202a/stove.glb",
        objType=arena.Shape.gltf_model,
        scale=(0.45,0.45,0.45),
        location=(-10.7,.33,-10.0),
        rotation=(0, 0.7071068, 0, 0.7071068), # Quaternions
        callback=stove_button_callback,
        clickable=True,
)
stove_cube = arena.Object(
        objName = "cube_stove",
        objType = arena.Shape.cube,
        location= (-10.7,2,-10.0),
        scale = (0.8,0.8,0.8),
        color = (255,0,255),
        data='{"material": {"opacity": 0.25}}'
)
stove_light = arena.Object(
        objName = "light_stove",
        objType = arena.Shape.light,
        location= (-10.7,2,-10.0),
        scale = (0.8,0.8,0.8),
        color = (0 ,0, 0),
        data='{"light": {"type": "point"}}'
)
stove_text = arena.Object(
        objName = "stove_text",
        objType = arena.Shape.text,
        color = (255,0,255),
        location= (-11.32, 2.6,-10.0),
        scale = (0.7, 0.7, 0.7),
        rotation=(0, 0.7071068, 0, 0.7071068), # Quaternions
        text = "Gas Stove Sensor"
)


'''
Turns the fan on and off
'''
fan_status = False
def fan_button_callback(event):
    global fan_obj
    global fan_status
    if event.event_type == arena.EventType.mousedown:
        if fan_status:
            fan_status = False
            fan_obj.update(data='{"animation": { "property": "rotation", "to": "0 360 0", "loop": false, "dur": 0}}')
        else:
            fan_status = True
            fan_obj.update(data='{"animation": { "property": "rotation", "to": "0 360 0", "loop": true, "dur": 1000}}')


fan_obj = arena.Object(
        objName = "fan",
        url="store/users/patrickhan/m202a/fan.glb",
        objType=arena.Shape.gltf_model,
        scale=(0.3,0.3,0.3),
        location=(-3.4,2.4,-8.5),
        clickable=True,
        data='{"animation": { "property": "rotation", "to": "0 360 0", "loop": false, "dur": 0}}',
)
button_fan = arena.Object(
        objName = "button_fan",
        objType = arena.Shape.cube,
        scale=(0.3,0.5,0.3),
        location=(-5,2,-10),
        clickable= True,
        callback=fan_button_callback,
        color = (255,0, 255)
)

'''
Updates the cube colors (Corresponding to temperature, humidity, wireless)
and thereby the sensor data input source (TODO)
based on the corresponding virtual button pressed.
'''
def button_callback(event):
    global sensor_to_read
    global reading_text
    if event.event_type == arena.EventType.mousedown:
        print("Source: ", event.object_id)
        if event.object_id == "button_cube_temperature":
            sensor_to_read = "temperature"
            reading_text.update(color=(255, 0, 0))
            for map_cube in first_floor_heatmap_cube_list:
                map_cube.update(color=(255, 0, 0))
        elif event.object_id == "button_cube_humidity":
            sensor_to_read = "humidity"
            reading_text.update(color=(0, 255, 0))
            for map_cube in first_floor_heatmap_cube_list:
                map_cube.update(color=(0, 255, 0))
        elif event.object_id == "button_cube_wireless":
            for map_cube in first_floor_heatmap_cube_list:
                map_cube.update(color=(0, 0, 255))


# For testing the number switching
reading_text = arena.Object(
        objName = "reading_text",
        objType = arena.Shape.text,
        color = default_map_cube_color,
        location= (-1.3,3.2,-7.4),
        rotation=(0, 0.7071068, 0, -0.7071068), # Quaternions
        text = "Hello World!"
)

temperature_button_text = arena.Object(
        objName = "temperature_button_text",
        objType = arena.Shape.text,
        color = (255,0,0),
        location= (-1.3,2.6,-8),
        scale = (0.3, 0.3, 0.3),
        rotation=(0, 0.7071068, 0, -0.7071068), # Quaternions
        text = "Temperature"
)
humidity_button_text = arena.Object(
        objName = "humidity_button_text",
        objType = arena.Shape.text,
        color = (0,255,0),
        location= (-1.3,2.6,-7.5),
        scale = (0.3, 0.3, 0.3),
        rotation=(0, 0.7071068, 0, -0.7071068), # Quaternions
        text = "Humidity"
)
wireless_button_text = arena.Object(
        objName = "wireless_button_text",
        objType = arena.Shape.text,
        color = (0,0,255),
        location= (-1.3,2.6,-7),
        scale = (0.3, 0.3, 0.3),
        rotation=(0, 0.7071068, 0, -0.7071068), # Quaternions
        text = "Wireless"
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
heatmap_cube_pos_list = [(-7,1.6,-2.5), (-5,1.6,-2.5), (-3,1.6,-2.5), # Missing (-9,1.6,-2.5) since it blocks the doorway
                         (-9,1.6,-4.5), (-7,1.6,-4.5), (-5,1.6,-4.5), (-3,1.6,-4.5),
                         (-9,1.6,-6.5), (-7,1.6,-6.5), (-5,1.6,-6.5), (-3,1.6,-6.5),
                         (-9,1.6,-8.5), (-7,1.6,-8.5), (-5,1.6,-8.5), (-3,1.6,-8.5)]

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