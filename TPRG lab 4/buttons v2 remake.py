"""
File name: buttons v2 remake.py
Name: Thomas Heine
Student number: 100777741

I accedently saved over the original buttons v2.py file so i re-made it.
buttons v2 is ment to display use a pico diplay modlue to diplay differnt colors
when the dffrent buttons are pressed on the pico display module.


"""
import time
from machine import Pin
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY, PEN_P4
from pimoroni import RGBLED

# Global configuration
TEXT_SIZE = 5  # Configurable text size 

# Defines the pen colors for the display module.
# Note: cyan and magenta go unused.
display = PicoGraphics(display=DISPLAY_PICO_DISPLAY, pen_type=PEN_P4, rotate=0)
display.set_backlight(0.5)
display.set_font("bitmap8")
WHITE = display.create_pen(255, 255, 255)
BLACK = display.create_pen(0, 0, 0)
CYAN = display.create_pen(0, 255, 255)
MAGENTA = display.create_pen(255, 0, 255)
YELLOW = display.create_pen(255, 255, 0)
GREEN = display.create_pen(0, 255, 0)
RED = display.create_pen(255, 0, 0)
BLUE = display.create_pen(0, 0, 255)

# Pins for the display module that i got in the lab kit
led = RGBLED(6, 7, 8)

# Pins for alternate display module version
# led = RGBLED(26, 27, 28)

# sets RGB LED to off to prevent the POST from randomly turing it on
led.set_rgb(0, 0, 0)

button_a = Pin(12, Pin.IN, Pin.PULL_UP)
button_b = Pin(13, Pin.IN, Pin.PULL_UP)
button_x = Pin(14, Pin.IN, Pin.PULL_UP)
button_y = Pin(15, Pin.IN, Pin.PULL_UP)

def change_display_color(color_name, color_pen, led_r, led_g, led_b):
    """
    Changes the display to show a solid color with the color name as text,
    and sets the RGB LED to match the color.
    
    Arguments:
        color_name: String name of the color (e.g., "RED", "BLUE")
        color_pen: The pen color to fill the display with
        led_r: Red component for LED (0-255)
        led_g: Green component for LED (0-255)
        led_b: Blue component for LED (0-255)
    """
    # Set the RGB LED color
    led.set_rgb(led_r, led_g, led_b)
    
    # Fill the display with the color
    display.set_pen(color_pen)
    display.clear()
    
    # Set text color to contrast with background
    # Use white text for dark colors, black for light colors
    if color_name in ["RED", "BLUE", "GREEN"]:
        display.set_pen(WHITE)
    else:
        display.set_pen(BLACK)
    
    # Calculate text position (center of screen)
    # Pico Display is 240x135 pixels
    text_width = len(color_name) * 8 * TEXT_SIZE
    text_x = (280 - text_width) // 2
    text_y = (135 - 8 * TEXT_SIZE) // 2
    
    # Draw the text
    display.text(color_name, text_x, text_y, scale=TEXT_SIZE)
    display.update()

while True:
    # Check button A for RED
    if button_a.value() == 0:
        change_display_color("RED", RED, 255, 0, 0)
        time.sleep(0.2)  # Debounce delay
    
    # Check button B for BLUE
    if button_b.value() == 0:
        change_display_color("BLUE", BLUE, 0, 0, 255)
        time.sleep(0.2)  # Debounce delay
    
    # Check button X for GREEN
    if button_x.value() == 0:
        change_display_color("GREEN", GREEN, 0, 255, 0)
        time.sleep(0.2)  # Debounce delay
    
    # Check button Y for YELLOW
    if button_y.value() == 0:
        change_display_color("YELLOW", YELLOW, 255, 255, 0)
        time.sleep(0.2)  # Debounce delay
    
    time.sleep(0.01)  # Small delay to stop spam writes