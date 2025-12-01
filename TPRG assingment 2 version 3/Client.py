#!/usr/bin/env python3
"""
Client.py
TPRG 2131 - Assignment 2
this client runs on a PC and receives system information from Raspberry Pi server
displays each vcgencmd value on a separate line
features automatic retry with user-provided IP addresses

Name: Thomas Heine
Student ID: 100777741
"""

import socket
import json
import sys

# default server configuration
DEFAULT_SERVER_IP = '192.168.18.111'  # change this to the Raspberry Pi server's IP
DEFAULT_PORT = 5000

def validate_ip(ip):
    """
    Validate if string is a valid IPv4 address
    Returns: True if valid, False otherwise
    """
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    try:
        return all(0 <= int(part) <= 255 for part in parts)
    except ValueError:
        return False

def attempt_connection(host, port):
    """
    Attempt to connect to server and retrieve data
    Returns: (success, data_dict or error_message)
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)  # 5 second varable timeout
    
    print(f"\nAttempting to connect to server")
    print(f"Target IPv4: {host}")
    print(f"Port: {port}")
    
    try:
        # connect to PI server
        s.connect((host, port))
        print(f"Connected successfully to {host}:{port}")
        print("=" * 60)
        
        # receive data from server
        print("\nReceiving data from server...")
        data_received = s.recv(1024)
        
        # check if received any data
        if not data_received:
            return False, "No data received from server"
        
        # read JSON
        try:
            json_string = data_received.decode('utf-8')
            data = json.loads(json_string)
            return True, data
            
        except json.JSONDecodeError as e:
            return False, f"Failed to parse JSON data: {e}"
        except KeyError as e:
            return False, f"Missing expected data field: {e}"
        
    except ConnectionRefusedError:
        return False, f"Connection refused by {host}:{port} - Server may not be running"
    except socket.timeout:
        return False, f"Connection timeout - Server at {host}:{port} did not respond"
    except socket.gaierror:
        return False, f"Cannot resolve server address: {host}"
    except Exception as e:
        return False, f"Unexpected error: {e}"
    finally:
        # clean up time now
        try:
            s.close()
        except:
            pass

def display_data(data):
    """display received sensor data in good formatted way"""
    print("\n" + "=" * 60)
    print("RASPBERRY PI SYSTEM INFORMATION")
    print("=" * 60)
    
    # core temp
    if "core_temperature_c" in data:
        temp = data["core_temperature_c"]
        print(f"Core Temperature:     {temp} C")
    
    # core volts
    if "core_voltage_v" in data:
        voltage = data["core_voltage_v"]
        print(f"Core Voltage:         {voltage} V")
    
    # ARM clock
    if "arm_frequency_mhz" in data:
        freq = data["arm_frequency_mhz"]
        print(f"ARM CPU Frequency:    {freq} MHz")
    
    # GPU memory
    if "gpu_memory_mb" in data:
        gpu_mem = data["gpu_memory_mb"]
        print(f"GPU Memory:           {gpu_mem} MB")
    
    # throttled status number thing
    if "throttled_status" in data:
        throttle = data["throttled_status"]
        print(f"Throttled Status:     {throttle}")
    
    # current time
    if "timestamp" in data:
        timestamp = data["timestamp"]
        print(f"Timestamp:            {timestamp}")
    
    print("=" * 60)
    print("\nData received and displayed successfully")

def main():
    """Main client function with retry logic"""
    
    print("\n" + "=" * 60)
    print("RASPBERRY PI VCGENCMD CLIENT")
    print("=" * 60)
    
    # try with preset IP first
    host = DEFAULT_SERVER_IP
    port = DEFAULT_PORT
    
    print(f"\nDefault server IP configured: {DEFAULT_SERVER_IP}")
    print(f"(You can change DEFAULT_SERVER_IP at the top of this file)")
    
    while True:
        # attempt a connection
        success, result = attempt_connection(host, port)
        
        if success:
            # connection probably successful
            # display data time
            display_data(result)
            break
        else:
            # connection failed
            print(f"\nConnection failed")
            print(f"Reason: {result}")
            print("\n" + "-" * 60)
            
            # ask user for help
            print("\nOptions:")
            print("  1. Try again with same IP address ({})".format(host))
            print("  2. Try with a different IP address")
            print("  3. Quit")
            
            try:
                choice = input("\nEnter your choice (1, 2, or 3): ").strip()
                
                if choice == '3':
                    print("\nExiting client")
                    return
                elif choice == '1':
                    # retry with same IP
                    print(f"\nRetrying connection to {host}:{port}")
                    continue
                elif choice == '2':
                    # get new IP from user
                    while True:
                        new_ip = input("\nEnter Raspberry Pi IPv4 address: ").strip()
                        
                        if validate_ip(new_ip):
                            host = new_ip
                            print(f"Will try connecting to: {host}:{port}")
                            break
                        else:
                            print(f"Invalid IPv4 address format: {new_ip}")
                            print("Example valid format: 192.168.1.100")
                            retry = input("Try again? (y/n): ").strip().lower()
                            if retry != 'y':
                                print("\nExiting client")
                                return
                else:
                    print("Invalid choice. Please enter 1, 2, or 3")
                    
            except KeyboardInterrupt:
                print("\n\nClient cancelled by user")
                return
            except EOFError:
                print("\n\nInput stream closed")
                return

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("CONFIGURATION")
    print("=" * 60)
    print(f"Default Server IP: {DEFAULT_SERVER_IP}")
    print(f"Default Port:      {DEFAULT_PORT}")
    print("\nIf connection fails, you can:")
    print("  - Retry with same IP")
    print("  - Try a different IP")
    print("  - Quit")
    print("=" * 60)
    
    try:
        input("\nPress Enter to start connection attempt...")
    except KeyboardInterrupt:
        print("\n\nClient cancelled by user")
        sys.exit(0)
    
    main()
    
    print("\n" + "=" * 60)
    print("Client session completed")
    print("=" * 60)
    print()
