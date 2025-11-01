"""
File name: Thermometerv2.py
Name: Thomas Heine
Student id: 100777741

This example takes the temperature from the Pico's onboard temperature sensor, and displays it on Pico Display Pack.
It now toggles between Celsius and Fahrenheit when any button is pressed.
"""
import machine
import time
from machine import Pin
from pimoroni import RGBLED
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY

# set up the display and drawing constants
display = PicoGraphics(display=DISPLAY_PICO_DISPLAY, rotate=0)

# set the display backlight to 50%
display.set_backlight(0.5)

WIDTH, HEIGHT = display.get_bounds()

BLACK = display.create_pen(0, 0, 0)
WHITE = display.create_pen(255, 255, 255)

# set up the internal temperature sensor
sensor_temp = machine.ADC(4)

# Set up the RGB LED for Display Pack
led = RGBLED(6, 7, 8)

# Set up buttons
button_a = Pin(12, Pin.IN, Pin.PULL_UP)
button_b = Pin(13, Pin.IN, Pin.PULL_UP)
button_x = Pin(14, Pin.IN, Pin.PULL_UP)
button_y = Pin(15, Pin.IN, Pin.PULL_UP)

# Temp conversion settings
conversion_factor = 3.3 / (65535)

temp_min = 10
temp_max = 30
bar_width = 5

temperatures = []

colors = [(0, 0, 255), (0, 255, 0), (255, 255, 0), (255, 0, 0)]

# Flag to toggle display mode
display_in_celsius = True

# Function to detect any button press
def any_button_pressed():
    return (not button_a.value() or
            not button_b.value() or
            not button_x.value() or
            not button_y.value())

# Function to convert C to F
def c_to_f(temp_c):
    return temp_c * 9 / 5 + 32

def temperature_to_color(temp):
    temp = min(temp, temp_max)
    temp = max(temp, temp_min)

    f_index = float(temp - temp_min) / float(temp_max - temp_min)
    f_index *= len(colors) - 1
    index = int(f_index)

    if index == len(colors) - 1:
        return colors[index]

    blend_b = f_index - index
    blend_a = 1.0 - blend_b

    a = colors[index]
    b = colors[index + 1]

    return [int((a[i] * blend_a) + (b[i] * blend_b)) for i in range(3)]

# Debounce variables
last_button_state = False
last_debounce_time = time.ticks_ms()
debounce_delay = 200  # milliseconds

while True:
    # Read temperature in Celsius
    reading = sensor_temp.read_u16() * conversion_factor
    temperature_c = 27 - (reading - 0.706) / 0.001721

    # Update temperature history
    temperatures.append(temperature_c)
    if len(temperatures) > WIDTH // bar_width:
        temperatures.pop(0)

    # Debounce button press to toggle unit
    current_button_state = any_button_pressed()
    if current_button_state and not last_button_state:
        if time.ticks_diff(time.ticks_ms(), last_debounce_time) > debounce_delay:
            display_in_celsius = not display_in_celsius
            last_debounce_time = time.ticks_ms()

    last_button_state = current_button_state

    # Prepare the display
    display.set_pen(BLACK)
    display.clear()

    i = 0
    for t in temperatures:
        color = temperature_to_color(t)
        display.set_pen(display.create_pen(*color))
        display.rectangle(i, HEIGHT - (round(t) * 4), bar_width, HEIGHT)
        i += bar_width

    led.set_rgb(*temperature_to_color(temperature_c))

    # Draw white background for text
    display.set_pen(WHITE)
    display.rectangle(1, 1, 130, 75)

    # Draw temperature as text
    display.set_pen(BLACK)
    if display_in_celsius:
        display.text("{:.2f} C".format(temperature_c), 3, 3, 0, 5)
    else:
        temp_f = c_to_f(temperature_c)
        display.text("{:.2f} F".format(temp_f), 3, 3, 0, 5)

    display.update()

    time.sleep(0.1)
