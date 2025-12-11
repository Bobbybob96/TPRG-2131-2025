#!/usr/bin/env python3
"""
ClientTH.py (VERSION 6)
TPRG 2131 - Project 2 - Client 
Author: Thomas Heine (Student ID: 100077741)
Date: December 11th, 2025

VERSION 6 FIXES:
1. Changed "Connection Established" text color from green to cyan (line 696)
2. Added explicit focus management to fix GUI responsiveness issue
3. Added window.bring_to_front() and window.force_focus() calls
4. Added refresh() calls after modal dialog closures

This client runs on Raspberry Pi ONLY and sends system information using vcgencmd commands.
Data is sent to server as a JSON object containing 5 different system metrics plus iteration count.

ServerTH.py version 1 works with ClientTH.py version 6

Requirements:
- Runs on Raspberry Pi only (exits gracefully on PC)
- Samples vcgen data at 2 second intervals
- Sends 50 iterations of complete data set
- Uses 5 vcgencmd commands (including core temperature)
- GUI with connection LED and Exit button
- Custom functions with at least one returning float
- Float values restricted to 1 decimal place
- Try/except error handling
"""

import socket
import os
import time
import json
import sys
import platform
import threading
try:
    import FreeSimpleGUI as sg
except ImportError:
    print("Error: FreeSimpleGUI module not found. Please install it first.")
    sys.exit(1)


# ============================================================================
# CONFIGURATION
# ============================================================================
DEFAULT_SERVER_IP = '127.0.0.1'  # localhost for testing on same Pi
DEFAULT_PORT = 5000
MAX_ITERATIONS = 50
SAMPLE_INTERVAL = 2  # seconds


# ============================================================================
# PLATFORM CHECK
# ============================================================================
def check_platform():
    """
    Check if running on Raspberry Pi. Exit gracefully if on PC.
    
    Returns:
        bool: True if on Raspberry Pi, False otherwise
    """
    system = platform.system()
    machine = platform.machine()
    
    print(f"[PLATFORM CHECK] System: {system}, Machine: {machine}")
    
    # Check for Raspberry Pi indicators
    is_pi = False
    
    # Method 1: Check /proc/cpuinfo for Raspberry Pi
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
            if 'Raspberry Pi' in cpuinfo or 'BCM' in cpuinfo:
                is_pi = True
                print("[PLATFORM CHECK] Raspberry Pi detected via /proc/cpuinfo")
    except FileNotFoundError:
        print("[PLATFORM CHECK] /proc/cpuinfo not found")
    
    # Method 2: Check if vcgencmd exists (Pi-specific command)
    try:
        result = os.popen('which vcgencmd').read()
        if result.strip():
            is_pi = True
            print("[PLATFORM CHECK] vcgencmd command found")
    except Exception as e:
        print(f"[PLATFORM CHECK] vcgencmd check failed: {e}")
    
    # Method 3: Check architecture (ARM typically indicates Pi)
    if machine.startswith('arm') or machine.startswith('aarch'):
        is_pi = True
        print("[PLATFORM CHECK] ARM architecture detected")
    
    if is_pi:
        print("[PLATFORM CHECK] ✓ Running on Raspberry Pi")
    else:
        print("[PLATFORM CHECK] ✗ Not running on Raspberry Pi")
    
    return is_pi


# ============================================================================
# VCGENCMD DATA COLLECTION FUNCTIONS
# ============================================================================
def get_core_temperature():
    """
    Get the core temperature of the Raspberry Pi.
    
    Returns:
        float: Temperature in Celsius (1 decimal place)
        
    Source: https://www.tomshardware.com/how-to/raspberry-pi-benchmark-vcgencmd
    """
    try:
        temp_str = os.popen('vcgencmd measure_temp').readline()
        # Parse 'temp=42.8'C' to get the numeric value
        temp_value = float(temp_str.replace("temp=", "").replace("'C", "").strip())
        return round(temp_value, 1)
    except Exception as e:
        print(f"[ERROR] Getting temperature: {e}")
        return 0.0


def get_core_voltage():
    """
    Get the core voltage of the Raspberry Pi.
    
    Returns:
        float: Voltage in volts (1 decimal place)
        
    Source: https://www.nicm.dev/vcgencmd/
    """
    try:
        volt_str = os.popen('vcgencmd measure_volts core').readline()
        # Parse 'volt=1.2000V' to get the numeric value
        volt_value = float(volt_str.replace("volt=", "").replace("V", "").strip())
        return round(volt_value, 1)
    except Exception as e:
        print(f"[ERROR] Getting core voltage: {e}")
        return 0.0


def get_arm_frequency():
    """
    Get the ARM CPU frequency in MHz.
    
    Returns:
        int: Frequency in MHz
        
    Source: https://forums.raspberrypi.com/viewtopic.php?t=245733
    """
    try:
        freq_str = os.popen('vcgencmd measure_clock arm').readline()
        # Parse 'frequency(48)=600000000' to get the numeric value
        freq_value = int(freq_str.split('=')[1].strip())
        # Convert Hz to MHz
        freq_mhz = freq_value // 1000000
        return freq_mhz
    except Exception as e:
        print(f"[ERROR] Getting ARM frequency: {e}")
        return 0


def get_gpu_memory():
    """
    Get the GPU memory allocation in MB.
    
    Returns:
        int: GPU memory in MB
        
    Source: https://www.nicm.dev/vcgencmd/
    """
    try:
        mem_str = os.popen('vcgencmd get_mem gpu').readline()
        # Parse 'gpu=128M' to get the numeric value
        mem_value = int(mem_str.replace("gpu=", "").replace("M", "").strip())
        return mem_value
    except Exception as e:
        print(f"[ERROR] Getting GPU memory: {e}")
        return 0


def get_throttled_status():
    """
    Get the throttled status of the Raspberry Pi (indicates undervoltage/throttling).
    
    Returns:
        str: Status string
        
    Source: https://www.nicm.dev/vcgencmd/
    """
    try:
        throttle_str = os.popen('vcgencmd get_throttled').readline()
        # Parse 'throttled=0x0' to get the hex value
        throttle_value = throttle_str.replace("throttled=", "").strip()
        
        # Interpret the value (0x0 means no issues)
        if throttle_value == "0x0":
            status = "Normal"
        else:
            status = f"Issues: {throttle_value}"
        
        return status
    except Exception as e:
        print(f"[ERROR] Getting throttled status: {e}")
        return "Unknown"


def collate_vcgen_data(iteration):
    """
    Collate all vcgencmd data into a dictionary.
    
    Args:
        iteration (int): Current iteration number
        
    Returns:
        dict: Dictionary containing all sensor data and iteration count
    """
    data = {
        "iteration": iteration,
        "core_temperature_c": get_core_temperature(),
        "core_voltage_v": get_core_voltage(),
        "arm_frequency_mhz": get_arm_frequency(),
        "gpu_memory_mb": get_gpu_memory(),
        "throttled_status": get_throttled_status(),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    return data


# ============================================================================
# CONNECTION MANAGEMENT
# ============================================================================
def validate_ip(ip):
    """
    Validate if string is a valid IPv4 address.
    
    Args:
        ip (str): IP address to validate
        
    Returns:
        bool: True if valid IPv4 address, False otherwise
    """
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    try:
        return all(0 <= int(part) <= 255 for part in parts)
    except ValueError:
        return False


def test_server_connection(ip, port, timeout=3):
    """
    Test connection to server without sending data.
    
    Args:
        ip (str): Server IP address
        port (int): Server port
        timeout (int): Connection timeout in seconds
        
    Returns:
        tuple: (success: bool, message: str)
    """
    print(f"\n[CONNECTION TEST] Attempting to connect to {ip}:{port}")
    print(f"[CONNECTION TEST] Timeout: {timeout} seconds")
    
    try:
        # Create test socket
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.settimeout(timeout)
        
        # Attempt connection
        test_socket.connect((ip, port))
        test_socket.close()
        
        print(f"[CONNECTION TEST] ✓ Successfully connected to {ip}:{port}")
        return True, f"Connection successful to {ip}:{port}"
        
    except ConnectionRefusedError:
        error_msg = f"Connection refused by {ip}:{port}"
        print(f"[CONNECTION TEST] ✗ {error_msg}")
        print("[CONNECTION TEST] Server may not be running")
        return False, error_msg
        
    except socket.timeout:
        error_msg = f"Connection timeout to {ip}:{port}"
        print(f"[CONNECTION TEST] ✗ {error_msg}")
        print("[CONNECTION TEST] Server did not respond in time")
        return False, error_msg
        
    except socket.gaierror as e:
        error_msg = f"Cannot resolve address {ip}"
        print(f"[CONNECTION TEST] ✗ {error_msg}: {e}")
        return False, error_msg
        
    except Exception as e:
        error_msg = f"Connection error: {str(e)}"
        print(f"[CONNECTION TEST] ✗ {error_msg}")
        return False, error_msg


def show_connection_dialog(default_ip, port):
    """
    Show initial connection dialog to get IP address from user.
    
    Args:
        default_ip (str): Default IP address to suggest
        port (int): Server port
        
    Returns:
        tuple: (should_connect: bool, ip_address: str)
    """
    print("\n[CONNECTION DIALOG] Showing initial connection prompt")
    
    sg.theme('DarkBlue3')
    
    layout = [
        [sg.Text('SERVER CONNECTION SETUP', font=('Helvetica', 14, 'bold'))],
        [sg.HorizontalSeparator()],
        [sg.Text('Choose how to connect to the server:', pad=(0, 10))],
        [sg.Radio('Use default IP address', 'CONNECTION', key='-USE_DEFAULT-', 
                  default=True, enable_events=True)],
        [sg.Text(f'    {default_ip}:{port}', key='-DEFAULT_TEXT-', 
                 text_color='cyan', pad=(20, 0))],
        [sg.Radio('Enter custom IP address', 'CONNECTION', key='-USE_CUSTOM-',
                  enable_events=True)],
        [sg.Text('    IP Address:', pad=(20, 5)), 
         sg.Input(default_ip, key='-CUSTOM_IP-', size=(20, 1), disabled=True)],
        [sg.HorizontalSeparator()],
        [sg.Button('Connect', size=(15, 1), bind_return_key=True, key='-CONNECT-'),
         sg.Button('Cancel', size=(15, 1), key='-CANCEL-')]
    ]
    
    window = sg.Window('Connection Setup', layout, modal=True, finalize=True)
    
    selected_ip = None
    should_connect = False
    
    try:
        while True:
            event, values = window.read()
            
            if event in (sg.WIN_CLOSED, '-CANCEL-'):
                print("[CONNECTION DIALOG] User cancelled connection")
                break
            
            # Enable/disable custom IP input based on radio selection
            if event == '-USE_DEFAULT-':
                window['-CUSTOM_IP-'].update(disabled=True)
                print("[CONNECTION DIALOG] Using default IP")
            elif event == '-USE_CUSTOM-':
                window['-CUSTOM_IP-'].update(disabled=False)
                window['-CUSTOM_IP-'].set_focus()
                print("[CONNECTION DIALOG] Using custom IP")
            
            if event == '-CONNECT-':
                if values['-USE_DEFAULT-']:
                    selected_ip = default_ip
                    print(f"[CONNECTION DIALOG] Selected default IP: {selected_ip}")
                else:
                    custom_ip = values['-CUSTOM_IP-'].strip()
                    if not validate_ip(custom_ip):
                        print(f"[CONNECTION DIALOG] ✗ Invalid IP format: {custom_ip}")
                        sg.popup_error('Invalid IP Address',
                                     f'"{custom_ip}" is not a valid IPv4 address.',
                                     'Please enter a valid IP (e.g., 192.168.1.100)',
                                     title='Invalid Input')
                        continue
                    selected_ip = custom_ip
                    print(f"[CONNECTION DIALOG] Selected custom IP: {selected_ip}")
                
                should_connect = True
                break
    
    finally:
        window.close()
        # FIX: Allow GUI to process close event
        time.sleep(0.1)
    
    return should_connect, selected_ip


def show_connection_failed_dialog(ip, port, error_message):
    """
    Show dialog when connection fails, offering retry options.
    
    Args:
        ip (str): IP address that failed
        port (int): Port number
        error_message (str): Error message to display
        
    Returns:
        str: User choice - 'retry', 'change', or 'quit'
    """
    print(f"\n[CONNECTION FAILED] Showing failure dialog for {ip}:{port}")
    print(f"[CONNECTION FAILED] Error: {error_message}")
    
    sg.theme('DarkBlue3')
    
    layout = [
        [sg.Text('CONNECTION FAILED', font=('Helvetica', 14, 'bold'), 
                 text_color='red')],
        [sg.HorizontalSeparator()],
        [sg.Text('Failed to connect to server:', pad=(0, 10))],
        [sg.Text(f'{ip}:{port}', font=('Courier', 11), text_color='cyan', 
                 pad=(20, 5))],
        [sg.Text('Error:', pad=(20, 5))],
        [sg.Multiline(error_message, size=(50, 3), disabled=True, 
                     pad=(20, 5), background_color='#1a1a1a', text_color='white')],
        [sg.HorizontalSeparator()],
        [sg.Text('What would you like to do?', font=('Helvetica', 10, 'bold'), 
                 pad=(0, 10))],
        [sg.Button('Retry Same IP', size=(20, 1), key='-RETRY-')],
        [sg.Button('Enter Different IP', size=(20, 1), key='-CHANGE-')],
        [sg.Button('Quit Program', size=(20, 1), key='-QUIT-', 
                  button_color=('white', 'red'))]
    ]
    
    window = sg.Window('Connection Failed', layout, modal=True, finalize=True)
    
    choice = 'quit'
    
    try:
        event, values = window.read()
        
        if event in (sg.WIN_CLOSED, '-QUIT-'):
            choice = 'quit'
            print("[CONNECTION FAILED] User chose to quit")
        elif event == '-RETRY-':
            choice = 'retry'
            print("[CONNECTION FAILED] User chose to retry same IP")
        elif event == '-CHANGE-':
            choice = 'change'
            print("[CONNECTION FAILED] User chose to enter different IP")
    
    finally:
        window.close()
        # FIX: Allow GUI to process close event
        time.sleep(0.1)
    
    return choice


def show_ip_input_dialog(current_ip, port):
    """
    Show dialog for entering a new IP address.
    
    Args:
        current_ip (str): Current/previous IP address
        port (int): Server port
        
    Returns:
        tuple: (should_continue: bool, new_ip: str)
    """
    print(f"\n[IP INPUT DIALOG] Prompting for new IP (current: {current_ip})")
    
    sg.theme('DarkBlue3')
    
    layout = [
        [sg.Text('ENTER SERVER IP ADDRESS', font=('Helvetica', 14, 'bold'))],
        [sg.HorizontalSeparator()],
        [sg.Text(f'Port: {port}', pad=(0, 10))],
        [sg.Text('Current IP:', pad=(0, 5))],
        [sg.Text(current_ip, text_color='yellow', pad=(20, 5))],
        [sg.HorizontalSeparator()],
        [sg.Text('Enter new IP address:', pad=(0, 10))],
        [sg.Input(current_ip, key='-NEW_IP-', size=(25, 1), focus=True)],
        [sg.Text('Example: 192.168.1.100', font=('Helvetica', 9), 
                 text_color='white', pad=(0, 5))],
        [sg.HorizontalSeparator()],
        [sg.Button('Connect', size=(15, 1), bind_return_key=True, key='-CONNECT-'),
         sg.Button('Cancel', size=(15, 1), key='-CANCEL-')]
    ]
    
    window = sg.Window('Enter IP Address', layout, modal=True, finalize=True)
    
    new_ip = None
    should_continue = False
    
    try:
        while True:
            event, values = window.read()
            
            if event in (sg.WIN_CLOSED, '-CANCEL-'):
                print("[IP INPUT DIALOG] User cancelled")
                break
            
            if event == '-CONNECT-':
                new_ip = values['-NEW_IP-'].strip()
                if not validate_ip(new_ip):
                    print(f"[IP INPUT DIALOG] ✗ Invalid IP format: {new_ip}")
                    sg.popup_error('Invalid IP Address',
                                 f'"{new_ip}" is not a valid IPv4 address.',
                                 'Please enter a valid IP (e.g., 192.168.1.100)',
                                 title='Invalid Input')
                    continue
                
                print(f"[IP INPUT DIALOG] Valid IP entered: {new_ip}")
                should_continue = True
                break
    
    finally:
        window.close()
        # FIX: Allow GUI to process close event
        time.sleep(0.1)
    
    return should_continue, new_ip


def establish_connection(default_ip, port):
    """
    Handle the complete connection establishment workflow with user interaction.
    
    Args:
        default_ip (str): Default IP address
        port (int): Server port
        
    Returns:
        tuple: (success: bool, final_ip: str or None)
    """
    print("\n" + "="*60)
    print("[CONNECTION WORKFLOW] Starting connection establishment")
    print("="*60)
    
    # Step 1: Initial connection dialog
    should_connect, current_ip = show_connection_dialog(default_ip, port)
    
    if not should_connect:
        print("[CONNECTION WORKFLOW] User cancelled initial connection")
        return False, None
    
    # Connection retry loop
    while True:
        # Test connection
        success, message = test_server_connection(current_ip, port)
        
        if success:
            print(f"[CONNECTION WORKFLOW] ✓ Successfully connected to {current_ip}:{port}")
            return True, current_ip
        
        # Connection failed - show options
        print(f"[CONNECTION WORKFLOW] ✗ Connection failed to {current_ip}:{port}")
        choice = show_connection_failed_dialog(current_ip, port, message)
        
        if choice == 'quit':
            print("[CONNECTION WORKFLOW] User chose to quit")
            return False, None
            
        elif choice == 'retry':
            print(f"[CONNECTION WORKFLOW] Retrying connection to {current_ip}:{port}")
            continue
            
        elif choice == 'change':
            # Get new IP from user
            should_continue, new_ip = show_ip_input_dialog(current_ip, port)
            
            if not should_continue:
                print("[CONNECTION WORKFLOW] User cancelled IP input")
                # Return to failed dialog
                continue
            
            current_ip = new_ip
            print(f"[CONNECTION WORKFLOW] Attempting new IP: {current_ip}")
            continue


# ============================================================================
# CLIENT COMMUNICATION THREAD
# ============================================================================
class ClientThread(threading.Thread):
    """
    Thread class to handle client communication without blocking the GUI.
    """
    
    def __init__(self, server_ip, port, window):
        """
        Initialize client thread.
        
        Args:
            server_ip (str): Server IP address
            port (int): Server port
            window: FreeSimpleGUI window instance
        """
        threading.Thread.__init__(self)
        self.server_ip = server_ip
        self.port = port
        self.window = window
        self.running = True
        self.daemon = True
        self.completed_iterations = 0
        
        print(f"\n[CLIENT THREAD] Initialized for {server_ip}:{port}")
    
    def run(self):
        """
        Main thread execution - sends data to server.
        """
        print("[CLIENT THREAD] Starting data transmission")
        print(f"[CLIENT THREAD] Target: {self.server_ip}:{self.port}")
        print(f"[CLIENT THREAD] Iterations: {MAX_ITERATIONS}")
        print(f"[CLIENT THREAD] Interval: {SAMPLE_INTERVAL} seconds\n")
        
        iteration = 0
        
        while self.running and iteration < MAX_ITERATIONS:
            try:
                iteration += 1
                
                print(f"[ITERATION {iteration}/{MAX_ITERATIONS}] Starting...")
                
                # Update status in GUI
                self.window.write_event_value('-STATUS-', 
                                            f'Iteration {iteration}/{MAX_ITERATIONS}')
                
                # Collate data
                json_data = collate_vcgen_data(iteration)
                print(f"[ITERATION {iteration}] Data collected:")
                print(f"  - Temperature: {json_data['core_temperature_c']}°C")
                print(f"  - Voltage: {json_data['core_voltage_v']}V")
                print(f"  - Frequency: {json_data['arm_frequency_mhz']} MHz")
                print(f"  - GPU Memory: {json_data['gpu_memory_mb']} MB")
                print(f"  - Status: {json_data['throttled_status']}")
                
                # Convert to JSON string and bytes
                json_string = json.dumps(json_data, indent=2)
                json_bytes = json_string.encode('utf-8')
                
                # Create socket and connect to server
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(5)
                
                try:
                    # Connect to server
                    print(f"[ITERATION {iteration}] Connecting to server...")
                    s.connect((self.server_ip, self.port))
                    
                    # Update LED to show connection
                    self.window.write_event_value('-LED-', 'ON')
                    print(f"[ITERATION {iteration}] ✓ Connected")
                    
                    # Send data
                    print(f"[ITERATION {iteration}] Sending {len(json_bytes)} bytes...")
                    s.send(json_bytes)
                    print(f"[ITERATION {iteration}] ✓ Data sent successfully")
                    
                    # Close connection
                    s.close()
                    
                    # Update LED to show disconnection
                    time.sleep(0.1)  # Brief pause so LED toggle is visible
                    self.window.write_event_value('-LED-', 'OFF')
                    print(f"[ITERATION {iteration}] Connection closed\n")
                    
                    # Mark this iteration as successfully completed
                    self.completed_iterations = iteration
                    
                except (ConnectionRefusedError, socket.timeout) as e:
                    error_msg = f'Connection error: {str(e)}'
                    print(f"[ITERATION {iteration}] ✗ {error_msg}\n")
                    self.window.write_event_value('-ERROR-', error_msg)
                    self.window.write_event_value('-LED-', 'OFF')
                
                # Wait for next interval (unless this is the last iteration)
                if iteration < MAX_ITERATIONS and self.running:
                    print(f"[ITERATION {iteration}] Waiting {SAMPLE_INTERVAL} seconds...")
                    time.sleep(SAMPLE_INTERVAL)
                
            except Exception as e:
                error_msg = f'Error in iteration {iteration}: {str(e)}'
                print(f"[ITERATION {iteration}] ✗ EXCEPTION: {error_msg}\n")
                self.window.write_event_value('-ERROR-', error_msg)
        
        # Send completion event with actual iterations completed
        if self.running and iteration >= MAX_ITERATIONS:
            # All iterations completed successfully
            print(f"\n[CLIENT THREAD] ✓ Completed all {MAX_ITERATIONS} iterations")
            self.window.write_event_value('-COMPLETE-', self.completed_iterations)
        else:
            # Stopped early by user
            print(f"\n[CLIENT THREAD] Stopped after {self.completed_iterations} iterations")
            self.window.write_event_value('-STOPPED-', self.completed_iterations)
    
    def stop(self):
        """Stop the thread."""
        print("[CLIENT THREAD] Stop requested")
        self.running = False


# ============================================================================
# GUI CREATION
# ============================================================================
def create_gui(server_ip, port):
    """
    Create the client GUI with connection LED and exit button.
    
    Args:
        server_ip (str): Server IP address to display
        port (int): Server port to display
        
    Returns:
        sg.Window: FreeSimpleGUI window object
    """
    # Define theme
    sg.theme('DarkBlue3')
    
    # Unicode LED symbols
    LED_OFF = '⚫'  # Black circle
    
    # Layout definition
    layout = [
        [sg.Text('RASPBERRY PI VCGENCMD CLIENT', font=('Helvetica', 16, 'bold'), 
                 justification='center', expand_x=True)],
        [sg.HorizontalSeparator()],
        # FIX 1: Changed text_color from 'green' to 'cyan' for consistency
        [sg.Text('Connection Established', font=('Helvetica', 11, 'bold'),
                 text_color='cyan', pad=(0, 10))],
        [sg.Text('Server:', size=(10, 1)), 
         sg.Text(f'{server_ip}:{port}', key='-SERVER-', size=(30, 1),
                 text_color='cyan')],
        [sg.Text('Status:', size=(10, 1)), 
         sg.Text('Ready to start...', key='-STATUS-', size=(30, 1))],
        [sg.Text('Connection:', size=(10, 1)), 
         sg.Text(LED_OFF, key='-LED-', font=('Helvetica', 20), text_color='white')],
        [sg.HorizontalSeparator()],
        [sg.Text('', key='-ERROR-', size=(50, 2), text_color='red')],
        [sg.Button('Start', size=(15, 1), key='-START-', button_color=('white', 'green')),
         sg.Button('Stop', size=(15, 1), key='-STOP-', button_color=('white', 'orange'), disabled=True),
         sg.Button('Exit', size=(15, 1), key='-EXIT-', button_color=('white', 'red'))]
    ]
    
    # Create window with finalize=True
    window = sg.Window('Client - TPRG 2131 Project 2', 
                       layout, 
                       finalize=True,
                       enable_close_attempted_event=True,
                       return_keyboard_events=False,
                       use_default_focus=False)
    
    # FIX 2: Explicitly force window to front and give it focus
    print("[GUI] Bringing window to front and forcing focus...")
    try:
        window.bring_to_front()
        window.force_focus()
        # Give the GUI time to fully render and gain focus
        window.refresh()
    except Exception as e:
        print(f"[GUI] Warning: Could not force focus: {e}")
    
    return window


# ============================================================================
# MAIN FUNCTION
# ============================================================================
def main():
    """
    Main function to run the client application.
    """
    print("\n" + "="*60)
    print("  RASPBERRY PI VCGENCMD CLIENT - TPRG 2131 Project 2")
    print("  Author: Thomas Heine (Student ID: 100077741)")
    print("  Version 6 client")
    print("="*60)
    print(f"  Platform: {platform.system()} {platform.machine()}")
    print(f"  Python: {sys.version.split()[0]}")
    print("="*60)
    
    # Check if running on Raspberry Pi
    if not check_platform():
        print("\n[PLATFORM ERROR] This application must run on a Raspberry Pi")
        sg.popup_error('Platform Error',
                      'This application must run on a Raspberry Pi.',
                      f'Detected platform: {platform.system()} {platform.machine()}',
                      'Exiting gracefully...',
                      title='Platform Check Failed')
        print("[EXIT] Exiting gracefully due to platform mismatch\n")
        sys.exit(0)
    
    # Establish connection with interactive workflow
    connection_success, server_ip = establish_connection(DEFAULT_SERVER_IP, DEFAULT_PORT)
    
    if not connection_success:
        print("\n[EXIT] Connection establishment cancelled or failed")
        print("[EXIT] Exiting gracefully\n")
        return
    
    print(f"\n[MAIN] Connection established to {server_ip}:{DEFAULT_PORT}")
    print("[MAIN] Creating GUI...")
    
    # FIX 3: Add small delay to ensure all modal dialogs are fully closed
    time.sleep(0.2)
    
    # Create GUI
    window = create_gui(server_ip, DEFAULT_PORT)
    client_thread = None
    
    # FIX 4: Force focus again after a brief moment
    print("[MAIN] Ensuring window focus...")
    time.sleep(0.1)
    try:
        window.bring_to_front()
        window.force_focus()
    except:
        pass
    
    # Unicode LED symbols
    LED_OFF = '⚫'
    LED_ON = '🟢'
    
    try:
        print("[MAIN] Entering event loop\n")
        
        # Event loop
        while True:
            event, values = window.read(timeout=100)
            
            # Handle window close
            if event in (sg.WIN_CLOSED, sg.WIN_CLOSE_ATTEMPTED_EVENT, '-EXIT-'):
                print("\n[MAIN] Exit requested")
                if client_thread and client_thread.is_alive():
                    print("[MAIN] Stopping client thread...")
                    client_thread.stop()
                    client_thread.join(timeout=1)
                    print("[MAIN] Client thread stopped")
                break
            
            # Handle start button
            if event == '-START-':
                if client_thread is None or not client_thread.is_alive():
                    print("\n[MAIN] Start button clicked")
                    # Disable start button, enable stop button
                    window['-START-'].update(disabled=True)
                    window['-STOP-'].update(disabled=False)
                    window['-ERROR-'].update('')
                    
                    # FIX 5: Refresh window after button state change
                    window.refresh()
                    
                    # Start client thread
                    client_thread = ClientThread(server_ip, DEFAULT_PORT, window)
                    client_thread.start()
                    print("[MAIN] Client thread started\n")
            
            # Handle stop button
            if event == '-STOP-':
                if client_thread and client_thread.is_alive():
                    print("\n[MAIN] Stop button clicked")
                    # Stop the client thread
                    client_thread.stop()
                    client_thread.join(timeout=1)
                    print("[MAIN] Client thread stopped")
                    
                    # Close current window
                    window.close()
                    
                    # Reconnection loop - keeps trying until success or user quits
                    reconnected = False
                    current_ip = server_ip  # Start with current IP
                    
                    while not reconnected:
                        # Show IP input dialog with current/last IP pre-filled
                        print(f"[MAIN] Showing IP input dialog for reconnection (current: {current_ip})")
                        should_continue, new_ip = show_ip_input_dialog(current_ip, DEFAULT_PORT)
                        
                        if not should_continue:
                            # User cancelled IP dialog, exit program
                            print("[MAIN] User cancelled reconnection after stop")
                            print("[MAIN] Exiting program...")
                            return  # Exit main() function
                        
                        # User provided an IP, test connection
                        current_ip = new_ip  # Update for next retry if needed
                        print(f"[MAIN] Testing connection to {new_ip}:{DEFAULT_PORT}")
                        success, message = test_server_connection(new_ip, DEFAULT_PORT)
                        
                        if success:
                            # Connection successful - update server IP and recreate GUI
                            server_ip = new_ip
                            print(f"[MAIN] ✓ Reconnection successful to {server_ip}:{DEFAULT_PORT}")
                            time.sleep(0.2)
                            window = create_gui(server_ip, DEFAULT_PORT)
                            client_thread = None
                            reconnected = True
                            
                            # Reset focus
                            time.sleep(0.1)
                            try:
                                window.bring_to_front()
                                window.force_focus()
                            except:
                                pass
                            
                            print("[MAIN] GUI recreated, ready for new session\n")
                        else:
                            # Connection failed - show failure dialog
                            print(f"[MAIN] ✗ Connection test failed for {new_ip}: {message}")
                            choice = show_connection_failed_dialog(new_ip, DEFAULT_PORT, message)
                            
                            if choice == 'quit':
                                # User chose to quit
                                print("[MAIN] User chose to quit after connection failure")
                                print("[MAIN] Exiting program...")
                                return  # Exit main() function
                            elif choice == 'retry':
                                # Retry with same IP - loop continues with current_ip unchanged
                                print(f"[MAIN] Retrying connection to {current_ip}")
                                # Loop will show IP dialog again with same IP
                                continue
                            elif choice == 'change':
                                # Change IP - loop continues and will show IP dialog
                                print("[MAIN] User chose to change IP")
                                # current_ip already updated, loop will show dialog
                                continue

            
            # Handle LED toggle events from thread
            if event == '-LED-':
                led_state = values['-LED-']
                if led_state == 'ON':
                    window['-LED-'].update(LED_ON)
                else:
                    window['-LED-'].update(LED_OFF)
            
            # Handle status updates from thread
            if event == '-STATUS-':
                status_text = values['-STATUS-']
                window['-STATUS-'].update(status_text)
            
            # Handle error messages from thread
            if event == '-ERROR-':
                error_text = values['-ERROR-']
                window['-ERROR-'].update(error_text)
            
            # Handle early stop by user
            if event == '-STOPPED-':
                iterations_completed = values['-STOPPED-']
                print(f"\n[MAIN] Stopped after {iterations_completed} iterations")
                window['-STATUS-'].update(f'Stopped at {iterations_completed}/{MAX_ITERATIONS} iterations')
                window['-START-'].update(disabled=False)
                window['-STOP-'].update(disabled=True)
                
                # Show accurate stopped message
                if iterations_completed > 0:
                    sg.popup('Stopped', 
                            f'Session stopped by user.\n'
                            f'Completed {iterations_completed} of {MAX_ITERATIONS} data samples.',
                            title='Client Stopped')
                else:
                    sg.popup('Stopped', 
                            'Session stopped before any data was sent.',
                            title='Client Stopped')
                print(f"[MAIN] Stop notification shown ({iterations_completed} iterations)\n")
                
                # Restore focus after stopped dialog
                try:
                    window.bring_to_front()
                    window.force_focus()
                except:
                    pass
            
            # Handle completion
            if event == '-COMPLETE-':
                iterations_completed = values['-COMPLETE-']
                print(f"\n[MAIN] All {MAX_ITERATIONS} iterations completed successfully!")
                window['-STATUS-'].update(f'Completed {MAX_ITERATIONS} iterations!')
                window['-START-'].update(disabled=False)
                window['-STOP-'].update(disabled=True)
                sg.popup('Complete', 
                        f'Successfully sent all {iterations_completed} data samples to server.',
                        title='Client Complete')
                print("[MAIN] Completion popup shown\n")
                
                # FIX 6: Restore focus after completion dialog
                try:
                    window.bring_to_front()
                    window.force_focus()
                except:
                    pass
    
    except KeyboardInterrupt:
        print("\n[MAIN] Client interrupted by user (Ctrl+C)")
    
    except Exception as e:
        print(f"\n[MAIN] ✗ Unexpected error: {e}")
        sg.popup_error('Error', f'Unexpected error: {e}', title='Client Error')
    
    finally:
        # Clean up
        print("\n[MAIN] Starting cleanup...")
        if client_thread and client_thread.is_alive():
            print("[MAIN] Stopping client thread...")
            client_thread.stop()
            client_thread.join(timeout=1)
        
        try:
            window.close()
            print("[MAIN] Window closed")
        except:
            print("[MAIN] Window already closed")
        
        print("[MAIN] Client shutdown complete\n")


# ============================================================================
# ENTRY POINT
# ============================================================================
if __name__ == '__main__':
    main()
