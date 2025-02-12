import subprocess
import json
import socket
import asyncio
import websockets

def get_local_ip():
    """Get the local IP address of the machine on the LAN."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))  # Connect to an external server
    local_ip = s.getsockname()[0]
    s.close()
    return local_ip

def get_network_range():
    """Calculate the /24 subnet based on the local IP address."""
    local_ip = get_local_ip()
    network_base = ".".join(local_ip.split(".")[:3]) + ".0/24"
    return network_base

def run_nmap_scan():
    """Runs nmap to discover devices on the local network."""
    network_range = get_network_range()
    nmap_path = r"C:\Program Files (x86)\Nmap\nmap.exe"  # Update this if your path is different
    try:
        result = subprocess.run([nmap_path, "-sn", network_range], capture_output=True, text=True)
        return parse_nmap_output(result.stdout)
    except Exception as e:
        print(f"Error running nmap: {e}")
        return []


def parse_nmap_output(output):
    """Parses nmap output to extract discovered devices."""
    devices = []
    lines = output.split("\n")
    current_ip = None
    for line in lines:
        if "Nmap scan report for" in line:
            current_ip = line.split(" ")[-1]
        elif "MAC Address:" in line:
            mac_address = line.split(" ")[2]
            devices.append({"ip": current_ip, "mac": mac_address})
    return devices

async def send_discovery_results(websocket):
    """Continuously scan and send results to frontend."""
    while True:
        devices = run_nmap_scan()
        await websocket.send(json.dumps(devices))
        await asyncio.sleep(5)  # Scan every 5 seconds

async def main():
    async with websockets.serve(send_discovery_results, "0.0.0.0", 8765):
        await asyncio.Future()  # Keeps the server running


print("Starting WebSocket server on ws://0.0.0.0:8765")
asyncio.run(main())
