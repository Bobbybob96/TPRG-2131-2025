#!/usr/bin/env python3
"""
Server_vcgencmds.py
TPRG 2131 - Assignment 2
this server runs on Raspberry Pi and sends system information using vcgencmd commands
data is sent to client as a JSON object containing 5 different system metrics

Name: Thomas Heine
Student ID: 100777741
"""

import socket
import os
import time
import json
import signal
import sys
import subprocess

# Global flag for clean shutdown
running = True

def get_server_ip():
    """
    get all the server's IP address(es) on the local network
    returns: list of IP valid addresses that lead to the server
    """
    ip_addresses = []
    
    try:
        # stratagy 1: Try hostname -I (works on Raspberry Pi)
        result = subprocess.run(['hostname', '-I'], capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            # returns all interface IPs
            ips = result.stdout.strip().split()
            ip_addresses.extend(ips)
    except:
        pass
    
    # other stratagy 2: Use socket method as backup
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # for finding the IP route
        ip = s.getsockname()[0]
        s.close()
        if ip not in ip_addresses:
            ip_addresses.append(ip)
    except:
        pass
    
    return ip_addresses if ip_addresses else ['Unable to determine']

def signal_handler(sig, frame):
    """this handles "Ctrl+C" terminal input for shutdown"""
    global running
    print("\n\nShutting down server gracefully...")
    running = False

# time to register signal handler
signal.signal(signal.SIGINT, signal_handler)

def get_core_temperature():
    """
    made to get the core temperature of the Raspberry Pi
    returns: Float value of temperature in Celsius
    source: https://www.tomshardware.com/how-to/raspberry-pi-benchmark-vcgencmd
    """
    try:
        temp_str = os.popen('vcgencmd measure_temp').readline()
        # convert 'temp=42.8'C' to get the numeric value
        temp_value = float(temp_str.replace("temp=", "").replace("'C", "").strip())
        return round(temp_value, 1)
    except Exception as e:
        print(f"Error getting temperature: {e}")
        return 0.0

def get_core_voltage():
    """
    getting the core voltage of the Raspberry Pi
    returns: Float value of voltage in volts
    source: https://www.nicm.dev/vcgencmd/
    """
    try:
        volt_str = os.popen('vcgencmd measure_volts core').readline()
        # converting 'volt=1.2000V' to get the numeric value
        volt_value = float(volt_str.replace("volt=", "").replace("V", "").strip())
        return round(volt_value, 2)
    except Exception as e:
        print(f"Error getting core voltage: {e}")
        return 0.0

def get_arm_frequency():
    """
    find the ARM CPU frequency in MHz
    returns: Integer value of frequency in MHz
    source: https://forums.raspberrypi.com/viewtopic.php?t=245733
    """
    try:
        freq_str = os.popen('vcgencmd measure_clock arm').readline()
        # Parse 'frequency(48)=600000000' to get the numeric value
        freq_value = int(freq_str.split('=')[1].strip())
        # Convert Hz to MHz
        freq_mhz = freq_value // 1000000
        return freq_mhz
    except Exception as e:
        print(f"Error getting ARM frequency: {e}")
        return 0

def get_gpu_memory():
    """
    get the GPU memory allocation in MB
    returns: Integer value of GPU memory in MB
    source: https://www.nicm.dev/vcgencmd/
    """
    try:
        mem_str = os.popen('vcgencmd get_mem gpu').readline()
        # Parse 'gpu=128M' to get the numeric value
        mem_value = int(mem_str.replace("gpu=", "").replace("M", "").strip())
        return mem_value
    except Exception as e:
        print(f"Error getting GPU memory: {e}")
        return 0

def get_throttled_status():
    """
    can find the throttled status of the Raspberry Pi
    returns: string for futher interpretation
    source: https://www.nicm.dev/vcgencmd/
    """
    try:
        throttle_str = os.popen('vcgencmd get_throttled').readline()
        # Parse 'throttled=0x0' to get the hex value
        throttle_value = throttle_str.replace("throttled=", "").strip()
        
        # Interpret the value (0x0 means no issues)
        if throttle_value == "0x0":
            status = "Normal"
        else:
            status = f"Issues detected: {throttle_value}"
        
        return status
    except Exception as e:
        print(f"Error getting throttled status: {e}")
        return "Unknown"

def main():
    """Main loop"""
    global running
    
    # create a new socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    host = ''  # listen on all interfaces
    port = 5000
    
    try:
        s.bind((host, port))
        s.listen(5)
        s.settimeout(1.0)  # set timeout for accept() to allow checking running flag
        
        # get server IP addresses
        ip_addresses = get_server_ip()
        
        print("\n" + "=" * 60)
        print("RASPBERRY PI VCGENCMD SERVER")
        print("=" * 60)
        print("\nSERVER IP ADDRESS(ES):")
        for ip in ip_addresses:
            print(f"  {ip}")
        print(f"\nPort: {port}")
        print("\nConfigure your client to connect to:")
        if ip_addresses and ip_addresses[0] != 'Unable to determine':
            print(f"  {ip_addresses[0]}:{port}")
        print("\n" + "=" * 60)
        print("Waiting for client connection...")
        print("Press Ctrl+C to stop the server")
        print("=" * 60 + "\n")
        
        while running:
            try:
                # try to accept client connection
                c, addr = s.accept()
                print(f'\nGot connection from {addr[0]}:{addr[1]}')
                
                # collect all the cool system information
                json_data = {
                    "core_temperature_c": get_core_temperature(),
                    "core_voltage_v": get_core_voltage(),
                    "arm_frequency_mhz": get_arm_frequency(),
                    "gpu_memory_mb": get_gpu_memory(),
                    "throttled_status": get_throttled_status(),
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # convert to JSON string and then to bytes
                json_string = json.dumps(json_data, indent=2)
                json_bytes = json_string.encode('utf-8')
                
                # display what is being sent
                print("\nSending data to client:")
                print(json_string)
                print(f"Total bytes: {len(json_bytes)}")
                
                # send data to client
                c.send(json_bytes)
                print("\nData sent successfully!")
                
                # suddenly close client connection
                c.close()
                print(f"Connection to {addr[0]}:{addr[1]} closed")
                
                # wait a bit to aviod spamming
                time.sleep(1)
                
            except socket.timeout:
                # time taken is normal and continue to check running flag
                continue
            except Exception as e:
                if running:  # only print error if this is supposed to be running
                    print(f"Error handling client: {e}")
                continue
    
    except KeyboardInterrupt:
        print("\n\nServer interrupted by user")
    except Exception as e:
        print(f"\nServer error: {e}")
    finally:
        # clean up time
        try:
            s.close()
            print("\nServer socket closed")
        except:
            pass
        print("Server shutdown complete. Goodbye!")

if __name__ == '__main__':
    main()
