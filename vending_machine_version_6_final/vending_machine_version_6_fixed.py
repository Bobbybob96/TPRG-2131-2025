"""
Thomas Heine
100777741

Vending Machine Simulator - TPRG2131 Project 1
version 6 type B with automatic FreeSimpleGUI.py fix

This program simulates a vending machine
and has two differnt operating modes for either a windows computer or rasberry pi.

This program uses the following pin config:

SERVO_PIN = 17
LED_PIN = 27            
BUTTON_PIN = 22 

(GPIO pin variables are on line 166 to line 173)
"""

# ============================================================================
# IMPORTS AND CONFIGURATION
# ============================================================================

import sys
import os
from time import sleep
import platform

# Enable comprehensive debugging
DEBUG = True
METHOD_TRACE = True

def debug_print(msg, level="INFO"):
    """Enhanced debug printing with levels"""
    if DEBUG:
        print(f"[{level}] {msg}")

def method_confirm(method_name, status, details=""):
    """Track method usage from FreeSimpleGUI"""
    if METHOD_TRACE:
        symbol = "[OK]" if status == "SUCCESS" else "[FAIL]"
        print(f"  {symbol} Method: {method_name} - {status} {details}")

# ============================================================================
# FREESIMPLEGUI IMPORT WITH AUTOMATIC FIX FOR DC CONNECT VERSION
# ============================================================================

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

debug_print(f"Running from: {current_dir}")
debug_print(f"Python version: {sys.version}")
debug_print(f"Platform: {platform.system()} {platform.release()}")

# Check for FreeSimpleGUI.py
freesimplegui_path = os.path.join(current_dir, "FreeSimpleGUI.py")
debug_print(f"Looking for FreeSimpleGUI.py in: {current_dir}")

if os.path.exists(freesimplegui_path):
    debug_print(f"Found FreeSimpleGUI.py at: {freesimplegui_path}", "SUCCESS")
    
    # READ AND FIX THE FILE BEFORE IMPORTING
    debug_print("Attempting to auto-fix FreeSimpleGUI.py syntax error...")
    
    try:
        # Read the original file
        with open(freesimplegui_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Check line 19 (index 18)
        if len(lines) > 18:
            line_19 = lines[18]
            debug_print(f"Line 19 content: {line_19.strip()}")
            
            if "import random=" in line_19:
                debug_print("Found syntax error 'import random=' on line 19", "WARNING")
                
                # Create a temporary fixed version
                fixed_path = os.path.join(current_dir, "FreeSimpleGUI_temp_fixed.py")
                debug_print(f"Creating temporary fixed version: {fixed_path}")
                
                # Fix the line
                lines[18] = "import random\n"
                
                # Write the fixed version
                with open(fixed_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                
                debug_print("Temporary fixed file created successfully", "SUCCESS")
                
                # Import from the fixed file
                sys.path.insert(0, current_dir)
                import FreeSimpleGUI_temp_fixed as sg
                debug_print("FreeSimpleGUI imported from fixed version", "SUCCESS")
                
                # Clean up the import name
                sys.modules['FreeSimpleGUI'] = sg
                
            else:
                debug_print("Line 19 appears to be correct, importing directly")
                import FreeSimpleGUI as sg
                debug_print("FreeSimpleGUI imported successfully", "SUCCESS")
        else:
            debug_print("File has less than 19 lines - unexpected!", "ERROR")
            sys.exit(1)
            
    except Exception as e:
        debug_print(f"Failed to read/fix FreeSimpleGUI.py: {e}", "ERROR")
        sys.exit(1)
else:
    debug_print(f"FreeSimpleGUI.py NOT FOUND at: {freesimplegui_path}", "ERROR")
    sys.exit(1)

# ============================================================================
# VERIFY FREESIMPLEGUI IMPORT AND TEST METHODS
# ============================================================================

debug_print("\n=== Testing FreeSimpleGUI Methods ===")

# Test basic attributes
try:
    version = sg.version if hasattr(sg, 'version') else "Unknown"
    method_confirm("sg.version", "SUCCESS", f"Version: {version}")
except Exception as e:
    method_confirm("sg.version", "FAILED", str(e))

# Test theme method
try:
    sg.theme('BluePurple')
    method_confirm("sg.theme()", "SUCCESS", "Theme set to BluePurple")
except Exception as e:
    method_confirm("sg.theme()", "FAILED", str(e))

# Test Text element
try:
    test_text = sg.Text("Test")
    method_confirm("sg.Text()", "SUCCESS", "Text element created")
except Exception as e:
    method_confirm("sg.Text()", "FAILED", str(e))

# Test Button element
try:
    test_button = sg.Button("Test")
    method_confirm("sg.Button()", "SUCCESS", "Button element created")
except Exception as e:
    method_confirm("sg.Button()", "FAILED", str(e))

# Test Column element
try:
    test_column = sg.Column([[]])
    method_confirm("sg.Column()", "SUCCESS", "Column element created")
except Exception as e:
    method_confirm("sg.Column()", "FAILED", str(e))

# Test Window class
try:
    test_window = sg.Window
    method_confirm("sg.Window", "SUCCESS", "Window class available")
except Exception as e:
    method_confirm("sg.Window", "FAILED", str(e))

debug_print("=== FreeSimpleGUI Testing Complete ===\n")

# ============================================================================
# GPIO PIN CONFIGURATION (Raspberry Pi only)
# ============================================================================

# GPIO pin assignments (BCM numbering)
SERVO_PIN = 17          # GPIO pin for servo motor (product dispenser)
LED_PIN = 27            # GPIO pin for LED (change indicator)
BUTTON_PIN = 22         # GPIO pin for physical coin return button

# ============================================================================
# PLATFORM DETECTION
# ============================================================================

def detect_platform():
    """Detect if running on Raspberry Pi"""
    system = platform.system()
    machine = platform.machine()
    
    is_pi = (system == "Linux" and ("arm" in machine or "aarch64" in machine))
    
    if is_pi:
        debug_print("Detected: Raspberry Pi", "INFO")
    else:
        debug_print(f"Detected: {system} on {machine} (GPIO disabled)", "INFO")
    
    return is_pi

# Determine platform and set hardware flag
hardware_present = detect_platform()

# Try to import Raspberry Pi hardware modules only if on Pi
servo = None
led = None
return_button = None

if hardware_present:
    try:
        from gpiozero.pins.pigpio import PiGPIOFactory
        from gpiozero import Servo, LED, Button
        debug_print("GPIO libraries loaded successfully", "SUCCESS")
    except ModuleNotFoundError:
        debug_print("GPIO libraries not found. Running in simulation mode.", "WARNING")
        hardware_present = False

# Enable debug logging
TESTING = True

def log(message):
    """Print debug messages when TESTING mode is enabled"""
    if TESTING:
        print(f"  LOG: {message}")

# ============================================================================
# MONEY CLASS
# ============================================================================

class Money(object):
    """Manages money tracking for the vending machine"""
    
    def __init__(self):
        self.amount = 0
        debug_print("Money class initialized", "SUCCESS")
    
    def add(self, value):
        self.amount += value
        log(f"Added {value} cents. Total: {self.amount} cents")
    
    def subtract(self, value):
        if value <= self.amount:
            self.amount -= value
            log(f"Subtracted {value} cents. Remaining: {self.amount} cents")
            return True
        else:
            log(f"Cannot subtract {value} cents. Only {self.amount} cents available")
            return False
    
    def get_amount(self):
        return self.amount
    
    def clear(self):
        log(f"Clearing {self.amount} cents")
        self.amount = 0
    
    def get_formatted(self):
        return f"${self.amount / 100:.2f}"

# ============================================================================
# COINS CLASS
# ============================================================================

class Coins(object):
    """Manages coin denominations accepted by the vending machine"""
    
    def __init__(self):
        self.denominations = {}
        debug_print("Coins class initialized", "SUCCESS")
    
    def add_coin(self, key, name, value):
        self.denominations[key] = (name, value)
        log(f"Added coin: {key} - {name} worth {value} cents")
    
    def get_coin(self, key):
        return self.denominations.get(key)
    
    def get_all_coins(self):
        return self.denominations
    
    def coin_exists(self, key):
        return key in self.denominations
    
    def get_keys(self):
        return self.denominations.keys()
    
    def get_values(self):
        values = [coin[1] for coin in self.denominations.values()]
        return sorted(values, reverse=True)

# ============================================================================
# PRODUCTS CLASS
# ============================================================================

class Products(object):
    """Manages products available in the vending machine"""
    
    def __init__(self):
        self.items = {}
        debug_print("Products class initialized", "SUCCESS")
    
    def add_product(self, key, name, price):
        self.items[key] = (name, price)
        log(f"Added product: {key} - {name} at {price} cents")
    
    def get_product(self, key):
        return self.items.get(key)
    
    def get_all_products(self):
        return self.items
    
    def product_exists(self, key):
        return key in self.items
    
    def get_keys(self):
        return self.items.keys()

# ============================================================================
# VENDING MACHINE CLASS
# ============================================================================

class VendingMachine(object):
    """Main vending machine controller implementing state machine pattern"""

    def __init__(self, window, products, coins):
        self.state = None
        self.states = {}
        self.event = ""
        self.money = Money()
        self.products = products
        self.coins = coins
        self.change_due = 0
        self.window = window
        self.coin_values = self.coins.get_values()
        self.last_update_message_shown = False  # Track if update message was just shown
        
        debug_print(f"VendingMachine initialized with {len(self.coin_values)} coin types", "SUCCESS")
        log(f"Coin values for change: {self.coin_values}")

    def add_state(self, state):
        self.states[state.name] = state
        debug_print(f"Added state: {state.name}", "SUCCESS")

    def go_to_state(self, state_name):
        if self.state:
            log(f'Exiting {self.state.name}')
            self.state.on_exit(self)
        
        self.state = self.states[state_name]
        log(f'Entering {self.state.name}')
        self.state.on_entry(self)

    def update(self):
        if self.state:
            self.state.update(self)
        self.update_display()

    def add_coin(self, coin_key):
        coin_info = self.coins.get_coin(coin_key)
        if coin_info:
            coin_value = coin_info[1]
            self.money.add(coin_value)
            self.last_update_message_shown = False  # Reset flag on significant events

    def update_display(self):
        if self.window:
            try:
                self.window['amount_display'].update(
                    f"Current Amount: {self.money.get_formatted()}"
                )
                # Only show the success message if it wasn't shown last time
                if not self.last_update_message_shown:
                    method_confirm("window[].update()", "SUCCESS", "Display updated")
                    self.last_update_message_shown = True
            except Exception as e:
                method_confirm("window[].update()", "FAILED", str(e))
                self.last_update_message_shown = False

    def button_action(self):
        print("Physical RETURN button pressed")
        self.event = 'RETURN'
        self.update()
    
    def dispense_product(self):
        if hardware_present and servo:
            log("Activating servo motor to dispense product")
            try:
                servo.min()
                sleep(0.5)
                servo.mid()
                sleep(0.5)
                servo.max()
                sleep(0.5)
                servo.mid()
                print("Product dispensed via servo motor")
            except Exception as e:
                print(f"Servo error: {e}")
        else:
            log("Servo not available - simulating product dispense")
    
    def blink_change_led(self, blink_count=3):
        CIRCLE = '⚫'  # ASCII for LED on
        CIRCLE_OUTLINE = '⚪'  # ASCII for LED off
        
        if hardware_present and led:
            log(f"Blinking hardware LED {blink_count} times")
            try:
                for i in range(blink_count):
                    led.on()
                    sleep(0.2)
                    led.off()
                    sleep(0.2)
                print("Hardware LED blink complete")
            except Exception as e:
                print(f"Hardware LED error: {e}")
        else:
            log("Hardware LED not available - using simulated LED")
        
        # GUI LED blinking
        if self.window:
            log(f"Blinking GUI LED {blink_count} times")
            try:
                for i in range(blink_count):
                    self.window['-CHANGE_LED-'].update(CIRCLE)
                    self.window.refresh()
                    sleep(0.2)
                    self.window['-CHANGE_LED-'].update(CIRCLE_OUTLINE)
                    self.window.refresh()
                    sleep(0.2)
                method_confirm("LED blink", "SUCCESS", f"{blink_count} blinks")
            except Exception as e:
                method_confirm("LED blink", "FAILED", str(e))

# ============================================================================
# STATE CLASSES
# ============================================================================

class State(object):
    """Base class for all states"""
    _NAME = ""
    
    def __init__(self):
        pass
    
    @property
    def name(self):
        return self._NAME
    
    def on_entry(self, machine):
        pass
    
    def on_exit(self, machine):
        pass
    
    def update(self, machine):
        pass

class WaitingState(State):
    """Initial state: waiting for first coin"""
    _NAME = "waiting"
    
    def update(self, machine):
        if machine.coins.coin_exists(machine.event):
            machine.add_coin(machine.event)
            machine.go_to_state('add_coins')
        elif machine.products.product_exists(machine.event):
            print("Please insert coins first")
        elif machine.event == "RETURN":
            print("No money to return")

class AddCoinsState(State):
    """Active transaction state"""
    _NAME = "add_coins"
    
    def update(self, machine):
        if machine.event == "RETURN":
            machine.change_due = machine.money.get_amount()
            machine.money.clear()
            machine.go_to_state('count_change')
        elif machine.coins.coin_exists(machine.event):
            machine.add_coin(machine.event)
        elif machine.products.product_exists(machine.event):
            product = machine.products.get_product(machine.event)
            product_price = product[1]
            current_balance = machine.money.get_amount()
            
            if current_balance >= product_price:
                machine.go_to_state('deliver_product')
            else:
                print(f"Insufficient funds. Need {product_price} cents, "
                      f"have {current_balance} cents")

class DeliverProductState(State):
    """Product delivery state"""
    _NAME = "deliver_product"
    
    def on_entry(self, machine):
        product = machine.products.get_product(machine.event)
        product_name = product[0]
        product_price = product[1]
        
        machine.money.subtract(product_price)
        print(f"Buzz... Whir... Click... {product_name}")
        machine.dispense_product()
        print(f"Remaining balance: {machine.money.get_formatted()}")
        
        machine.go_to_state('add_coins')

class CountChangeState(State):
    """Change return state"""
    _NAME = "count_change"
    
    def on_entry(self, machine):
        change_dollars = machine.change_due / 100
        print(f"Change due: ${change_dollars:.2f}")
        log(f"Returning change: {machine.change_due} cents")
        machine.blink_change_led(blink_count=3)
    
    def update(self, machine):
        CIRCLE = '⚫'  # ASCII for LED on
        CIRCLE_OUTLINE = '⚪'  # ASCII lowercase for LED off
        
        for coin_value in machine.coin_values:
            while machine.change_due >= coin_value:
                print(f"Returning {coin_value} cents")
                machine.change_due -= coin_value
                
                if hardware_present and led:
                    led.on()
                    sleep(0.15)
                    led.off()
                    sleep(0.15)
                
                if machine.window:
                    try:
                        machine.window['-CHANGE_LED-'].update(CIRCLE)
                        machine.window.refresh()
                        sleep(0.15)
                        machine.window['-CHANGE_LED-'].update(CIRCLE_OUTLINE)
                        machine.window.refresh()
                        sleep(0.15)
                    except Exception as e:
                        log(f"GUI LED error: {e}")
        
        if machine.change_due == 0:
            machine.go_to_state('waiting')

# ============================================================================
# SETUP FUNCTIONS
# ============================================================================

def setup_coins():
    """Create and populate the Coins object"""
    coins = Coins()
    coins.add_coin("5", "5¢", 5)
    coins.add_coin("10", "10¢", 10)
    coins.add_coin("25", "25¢", 25)
    coins.add_coin("100", "$1", 100)
    coins.add_coin("200", "$2", 200)
    
    debug_print(f"Coins setup complete - {len(coins.denominations)} types", "SUCCESS")
    return coins

def setup_products():
    """Create and populate the Products object"""
    products = Products()
    products.add_product("surprise", "SURPRISE", 5)
    products.add_product("chips", "CHIPS", 50)
    products.add_product("candy", "CANDY", 75)
    products.add_product("soda", "SODA", 100)
    products.add_product("gum", "GUM", 25)
    products.add_product("cookies", "COOKIES", 85)
    products.add_product("water", "WATER", 95)
    products.add_product("juice", "JUICE", 125)
    products.add_product("crackers", "CRACKERS", 60)
    products.add_product("nuts", "NUTS", 150)
    
    debug_print(f"Products setup complete - {len(products.items)} items", "SUCCESS")
    return products

# ============================================================================
# MAIN PROGRAM
# ============================================================================

if __name__ == "__main__":
    
    debug_print("\n=== VENDING MACHINE STARTUP ===")
    
    # Set theme
    try:
        sg.theme('BluePurple')
        method_confirm("Set theme", "SUCCESS", "BluePurple")
    except Exception as e:
        method_confirm("Set theme", "FAILED", str(e))
    
    # Initialize data structures
    coins = setup_coins()
    products = setup_products()

    debug_print("\n=== BUILDING GUI LAYOUT ===")
    
    # Build GUI layout
    coin_col = []
    try:
        coin_col.append([sg.Text("ENTER COINS", font=("Helvetica", 24))])
        method_confirm("Create coin header", "SUCCESS")
    except Exception as e:
        method_confirm("Create coin header", "FAILED", str(e))
    
    # Create coin buttons
    for coin_key in coins.get_keys():
        try:
            coin_info = coins.get_coin(coin_key)
            button = sg.Button(coin_key, font=("Helvetica", 18))
            coin_col.append([button])
            method_confirm(f"Create coin button {coin_key}", "SUCCESS")
        except Exception as e:
            method_confirm(f"Create coin button {coin_key}", "FAILED", str(e))

    # Product column
    select_col = []
    try:
        select_col.append([sg.Text("SELECT ITEM", font=("Helvetica", 24))])
        method_confirm("Create product header", "SUCCESS")
    except Exception as e:
        method_confirm("Create product header", "FAILED", str(e))
    
    # Create product buttons
    product_buttons = []
    for product_key in products.get_keys():
        try:
            product_info = products.get_product(product_key)
            product_name = product_info[0]
            product_price = product_info[1]
            
            button_text = f"{product_key}\n${product_price/100:.2f}"
            button = sg.Button(button_text, key=product_key, 
                              font=("Helvetica", 14), size=(12, 3))
            product_buttons.append([button])
            method_confirm(f"Create product button {product_key}", "SUCCESS")
        except Exception as e:
            method_confirm(f"Create product button {product_key}", "FAILED", str(e))
    
    # Scrollable product column
    try:
        select_col.append([
            sg.Column(product_buttons, scrollable=True, 
                     vertical_scroll_only=True, size=(200, 300))
        ])
        method_confirm("Create scrollable column", "SUCCESS")
    except Exception as e:
        method_confirm("Create scrollable column", "FAILED", str(e))

    # Main layout
    try:
        layout = [
            [sg.Column(coin_col, vertical_alignment="TOP"),
             sg.VSeparator(),
             sg.Column(select_col, vertical_alignment="TOP")]
        ]
        method_confirm("Create main layout", "SUCCESS")
    except Exception as e:
        method_confirm("Create main layout", "FAILED", str(e))
    
    # Add display
    try:
        layout.append([
            sg.Text("Current Amount: $0.00", key='amount_display', 
                   font=("Helvetica", 16), size=(30, 1))
        ])
        method_confirm("Add amount display", "SUCCESS")
    except Exception as e:
        method_confirm("Add amount display", "FAILED", str(e))
    
    # Add return button with LED
    CIRCLE = '⚫'  # ASCII for LED on  
    CIRCLE_OUTLINE = '⚪'  # ASCII for LED off
    
    def LED(color, key):
        """Simulated LED using Text element"""
        return sg.Text(CIRCLE_OUTLINE, text_color=color, key=key, font=("Helvetica", 16))
    
    try:
        layout.append([
            sg.Button("RETURN", font=("Helvetica", 12)),
            sg.Text("  Change LED: ", font=("Helvetica", 12)),
            LED('red', '-CHANGE_LED-')
        ])
        method_confirm("Add RETURN button with LED", "SUCCESS")
    except Exception as e:
        method_confirm("Add RETURN button with LED", "FAILED", str(e))
    
    # Create window
    debug_print("\n=== CREATING WINDOW ===")
    try:
        window = sg.Window('Vending Machine', layout)
        method_confirm("Create Window", "SUCCESS")
    except Exception as e:
        method_confirm("Create Window", "FAILED", str(e))
        sys.exit(1)

    # Initialize vending machine
    debug_print("\n=== INITIALIZING STATE MACHINE ===")
    vending = VendingMachine(window, products, coins)

    # Register states
    vending.add_state(WaitingState())
    vending.add_state(AddCoinsState())
    vending.add_state(DeliverProductState())
    vending.add_state(CountChangeState())

    # Set initial state
    vending.go_to_state('waiting')

    # Initialize GPIO if on Pi
    if hardware_present:
        debug_print("\n=== INITIALIZING GPIO ===")
        

    # Initialize GPIO if on Pi
    if hardware_present:
        debug_print("\n=== INITIALIZING GPIO ===")

        # If PiGPIOFactory is available, ensure pigpiod daemon is running so we can use hardware PWM.
        try:
            if 'PiGPIOFactory' in globals() or 'PiGPIOFactory' in locals():
                debug_print("Attempting to start pigpiod daemon (if not already running)...", "INFO")
                # start pigpiod if available; ignore failures to avoid crashing
                try:
                    os.system("sudo pigpiod >/dev/null 2>&1 || true")
                    sleep(0.5)
                    debug_print("pigpiod start command issued", "SUCCESS")
                except Exception as e:
                    debug_print(f"Failed to start pigpiod: {e}", "WARNING")
            else:
                debug_print("PiGPIOFactory not imported; will attempt GPIO without pigpiod", "WARNING")
        except Exception as e:
            debug_print(f"pigpiod start step failed: {e}", "WARNING")

        # Initialize servo using PiGPIOFactory when possible (provides reliable hardware PWM)
        try:
            if 'PiGPIOFactory' in globals() or 'PiGPIOFactory' in locals():
                factory = PiGPIOFactory()
                servo = Servo(SERVO_PIN, pin_factory=factory)
                debug_print("Using PiGPIOFactory for servo", "INFO")
            else:
                servo = Servo(SERVO_PIN)
            servo.mid()
            debug_print(f"Servo initialized on GPIO {SERVO_PIN}", "SUCCESS")
        except Exception as e:
            debug_print(f"Servo initialization failed: {e}", "ERROR")
            servo = None

        try:
            led = LED(LED_PIN)
            led.off()
            debug_print(f"LED initialized on GPIO {LED_PIN}", "SUCCESS")
        except Exception as e:
            debug_print(f"LED initialization failed: {e}", "ERROR")
            led = None

        try:
            return_button = Button(BUTTON_PIN, pull_up=True)
            return_button.when_pressed = vending.button_action
            debug_print(f"Button initialized on GPIO {BUTTON_PIN}", "SUCCESS")
        except Exception as e:
            debug_print(f"Button initialization failed: {e}", "ERROR")
            return_button = None
        
        try:
            led = LED(LED_PIN)
            led.off()
            debug_print(f"LED initialized on GPIO {LED_PIN}", "SUCCESS")
        except Exception as e:
            debug_print(f"LED initialization failed: {e}", "ERROR")
            led = None
        
        try:
            return_button = Button(BUTTON_PIN, pull_up=True)
            return_button.when_pressed = vending.button_action
            debug_print(f"Button initialized on GPIO {BUTTON_PIN}", "SUCCESS")
        except Exception as e:
            debug_print(f"Button initialization failed: {e}", "ERROR")
            return_button = None
    
    debug_print("\n=== VENDING MACHINE READY ===")
    debug_print("Entering main event loop...\n")
    
    # Main event loop
    event_count = 0
    while True:
        event, values = window.read(timeout=10)
        
        if event != '__TIMEOUT__':
            event_count += 1
            log(f"Event #{event_count}: {event}")
        
        if event in (sg.WIN_CLOSED, 'Exit'):
            debug_print("Window closed by user", "INFO")
            break
        
        vending.event = event
        vending.update()

    # Cleanup
    debug_print("\n=== CLEANUP ===")
    
    if hardware_present:
        try:
            if servo:
                servo.mid()
                servo.close()
                debug_print("Servo cleaned up", "SUCCESS")
        except:
            pass
        
        try:
            if led:
                led.off()
                led.close()
                debug_print("LED cleaned up", "SUCCESS")
        except:
            pass
        
        try:
            if return_button:
                return_button.close()
                debug_print("Button cleaned up", "SUCCESS")
        except:
            pass
    
    window.close()
    debug_print("Window closed", "SUCCESS")
    debug_print("=== VENDING MACHINE SHUTDOWN COMPLETE ===")
    print("Normal exit")
