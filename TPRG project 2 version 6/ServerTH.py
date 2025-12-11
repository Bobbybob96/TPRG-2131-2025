#!/usr/bin/env python3
"""
ServerTH.py (VERSION 1)
TPRG 2131 - Project 2 - Server
Author: Thomas Heine (Student ID: 100077741)
Date: December 11th, 2025

This server runs on Raspberry Pi or PC and receives system information from the client.
Data is received as a JSON object and displayed in a GUI with real-time updates.
Features a GUI with connection status LED indicator that toggles as new data arrives.

ServerTH.py version 1 works with ClientTH.py version 6

Requirements:
- Runs on both Raspberry Pi and PC
- Uses main guard clause
- GUI displays 6 current values from JSON object (5 vcgencmd + iteration)
- GUI with connection LED that toggles on new data and Exit button
- Try/except error handling with docstrings
"""

import socket
import json
import sys
import threading
import time
try:
    import FreeSimpleGUI as sg
except ImportError:
    print("Error: FreeSimpleGUI module not found. Please install it first.")
    sys.exit(1)


# ============================================================================
# CONFIGURATION
# ============================================================================
SERVER_HOST = ''  # Listen on all interfaces
SERVER_PORT = 5000


# ============================================================================
# SERVER THREAD
# ============================================================================
class ServerThread(threading.Thread):
    """
    Thread class to handle server socket operations without blocking the GUI.
    """
    
    def __init__(self, window):
        """
        Initialize server thread.
        
        Args:
            window: FreeSimpleGUI window instance
        """
        threading.Thread.__init__(self)
        self.window = window
        self.running = True
        self.daemon = True
        self.socket = None
    
    def run(self):
        """
        Main thread execution - listens for client connections and receives data.
        """
        try:
            # Create socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.settimeout(1.0)  # Timeout to allow checking running flag
            
            # Bind and listen
            self.socket.bind((SERVER_HOST, SERVER_PORT))
            self.socket.listen(5)
            
            # Get server IP
            server_ip = self.get_server_ip()
            self.window.write_event_value('-SERVER_IP-', server_ip)
            self.window.write_event_value('-STATUS-', 'Waiting for connection...')
            
            while self.running:
                try:
                    # Accept client connection (with timeout)
                    client_socket, addr = self.socket.accept()
                    
                    # Update status
                    self.window.write_event_value('-STATUS-', 
                                                 f'Connected to {addr[0]}:{addr[1]}')
                    
                    # Receive data
                    data_received = client_socket.recv(4096)
                    
                    if data_received:
                        try:
                            # Decode and parse JSON
                            json_string = data_received.decode('utf-8')
                            data = json.loads(json_string)
                            
                            # Send data to GUI
                            self.window.write_event_value('-DATA-', data)
                            
                            # Toggle LED
                            self.window.write_event_value('-LED_TOGGLE-', True)
                            
                        except json.JSONDecodeError as e:
                            self.window.write_event_value('-ERROR-', 
                                                         f'JSON parse error: {e}')
                        except Exception as e:
                            self.window.write_event_value('-ERROR-', 
                                                         f'Data processing error: {e}')
                    
                    # Close client connection
                    client_socket.close()
                    
                except socket.timeout:
                    # Timeout is normal, just continue to check running flag
                    continue
                    
                except Exception as e:
                    if self.running:  # Only report error if still running
                        self.window.write_event_value('-ERROR-', 
                                                     f'Connection error: {e}')
        
        except Exception as e:
            self.window.write_event_value('-ERROR-', f'Server error: {e}')
        
        finally:
            # Clean up socket
            if self.socket:
                try:
                    self.socket.close()
                except:
                    pass
    
    def stop(self):
        """Stop the server thread."""
        self.running = False
    
    def get_server_ip(self):
        """
        Get the server's IP address on the local network.
        
        Returns:
            str: IP address or 'localhost'
        """
        try:
            # Create a socket to determine route (doesn't actually connect)
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return '127.0.0.1'


# ============================================================================
# GUI CREATION
# ============================================================================
def create_gui():
    """
    Create the server GUI with data display and connection LED.
    
    Returns:
        sg.Window: FreeSimpleGUI window object
    """
    # Define theme
    sg.theme('DarkBlue3')
    
    # Unicode LED symbols
    LED_OFF = '⚫'  # Black circle
    
    # Layout definition
    layout = [
        [sg.Text('RASPBERRY PI VCGENCMD SERVER', font=('Helvetica', 16, 'bold'), 
                 justification='center', expand_x=True)],
        [sg.HorizontalSeparator()],
        
        # Server info
        [sg.Text('Server IP:', size=(15, 1)), 
         sg.Text('Starting...', key='-SERVER_IP-', size=(30, 1))],
        [sg.Text('Port:', size=(15, 1)), 
         sg.Text(f'{SERVER_PORT}', size=(30, 1))],
        [sg.Text('Status:', size=(15, 1)), 
         sg.Text('Starting server...', key='-STATUS-', size=(30, 1))],
        [sg.Text('Connection:', size=(15, 1)), 
         sg.Text(LED_OFF, key='-LED-', font=('Helvetica', 20), text_color='white')],
        
        [sg.HorizontalSeparator()],
        [sg.Text('RECEIVED DATA', font=('Helvetica', 14, 'bold'))],
        [sg.HorizontalSeparator()],
        
        # Data display - 6 values (5 vcgencmd + iteration)
        [sg.Text('Iteration:', size=(20, 1)), 
         sg.Text('---', key='-ITERATION-', size=(25, 1))],
        [sg.Text('Core Temperature:', size=(20, 1)), 
         sg.Text('---', key='-TEMP-', size=(25, 1))],
        [sg.Text('Core Voltage:', size=(20, 1)), 
         sg.Text('---', key='-VOLTAGE-', size=(25, 1))],
        [sg.Text('ARM Frequency:', size=(20, 1)), 
         sg.Text('---', key='-FREQ-', size=(25, 1))],
        [sg.Text('GPU Memory:', size=(20, 1)), 
         sg.Text('---', key='-GPU-', size=(25, 1))],
        [sg.Text('Throttled Status:', size=(20, 1)), 
         sg.Text('---', key='-THROTTLE-', size=(25, 1))],
        [sg.Text('Timestamp:', size=(20, 1)), 
         sg.Text('---', key='-TIMESTAMP-', size=(25, 1))],
        
        [sg.HorizontalSeparator()],
        [sg.Text('', key='-ERROR-', size=(50, 2), text_color='red')],
        [sg.Button('Exit', size=(20, 1), key='-EXIT-', button_color=('white', 'red'))]
    ]
    
    # Create window
    window = sg.Window('Server - TPRG 2131 Project 2', 
                       layout, 
                       finalize=True,
                       enable_close_attempted_event=True)
    
    return window


# ============================================================================
# DATA DISPLAY FUNCTION
# ============================================================================
def update_data_display(window, data):
    """
    Update the GUI with received data.
    
    Args:
        window: FreeSimpleGUI window instance
        data (dict): Dictionary containing sensor data
    """
    try:
        # Update iteration count
        if 'iteration' in data:
            window['-ITERATION-'].update(f"{data['iteration']}")
        
        # Update temperature
        if 'core_temperature_c' in data:
            temp = data['core_temperature_c']
            window['-TEMP-'].update(f"{temp}°C")
        
        # Update voltage
        if 'core_voltage_v' in data:
            voltage = data['core_voltage_v']
            window['-VOLTAGE-'].update(f"{voltage}V")
        
        # Update frequency
        if 'arm_frequency_mhz' in data:
            freq = data['arm_frequency_mhz']
            window['-FREQ-'].update(f"{freq} MHz")
        
        # Update GPU memory
        if 'gpu_memory_mb' in data:
            gpu_mem = data['gpu_memory_mb']
            window['-GPU-'].update(f"{gpu_mem} MB")
        
        # Update throttled status
        if 'throttled_status' in data:
            throttle = data['throttled_status']
            window['-THROTTLE-'].update(throttle)
        
        # Update timestamp
        if 'timestamp' in data:
            timestamp = data['timestamp']
            window['-TIMESTAMP-'].update(timestamp)
            
    except Exception as e:
        window['-ERROR-'].update(f"Display error: {e}")


# ============================================================================
# MAIN FUNCTION
# ============================================================================
def main():
    """
    Main function to run the server application.
    """
    print("\n" + "=" * 60)
    print("  RASPBERRY PI VCGENCMD SERVER - TPRG 2131 Project 2")
    print("  Author: Thomas Heine (Student ID: 100077741)")
    print("  Version 1 server")
    print("=" * 60)
    print(f"  Starting server on port {SERVER_PORT}...")
    print("=" * 60 + "\n")
    
    # Create GUI
    window = create_gui()
    
    # Start server thread
    server_thread = ServerThread(window)
    server_thread.start()
    
    # Unicode LED symbols
    LED_OFF = '⚫'
    LED_ON = '🟢'
    led_state = False  # False = OFF, True = ON
    
    try:
        # Event loop
        while True:
            event, values = window.read(timeout=100)
            
            # Handle window close
            if event in (sg.WIN_CLOSED, sg.WIN_CLOSE_ATTEMPTED_EVENT, '-EXIT-'):
                break
            
            # Handle server IP update
            if event == '-SERVER_IP-':
                server_ip = values['-SERVER_IP-']
                window['-SERVER_IP-'].update(server_ip)
                print(f"Server listening on: {server_ip}:{SERVER_PORT}")
            
            # Handle status updates
            if event == '-STATUS-':
                status_text = values['-STATUS-']
                window['-STATUS-'].update(status_text)
            
            # Handle data received
            if event == '-DATA-':
                data = values['-DATA-']
                update_data_display(window, data)
            
            # Handle LED toggle
            if event == '-LED_TOGGLE-':
                # Toggle LED state
                led_state = not led_state
                if led_state:
                    window['-LED-'].update(LED_ON)
                else:
                    window['-LED-'].update(LED_OFF)
            
            # Handle error messages
            if event == '-ERROR-':
                error_text = values['-ERROR-']
                window['-ERROR-'].update(error_text)
                print(f"Error: {error_text}")
    
    except KeyboardInterrupt:
        print("\nServer interrupted by user")
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        sg.popup_error('Error', f'Unexpected error: {e}', title='Server Error')
    
    finally:
        # Stop server thread
        if server_thread.is_alive():
            server_thread.stop()
            server_thread.join(timeout=2)
        
        # Close window
        window.close()
        print("\nServer shutdown complete")


# ============================================================================
# ENTRY POINT WITH MAIN GUARD
# ============================================================================
if __name__ == '__main__':
    main()
