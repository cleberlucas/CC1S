import subprocess

def scan_network():
    active_devices = {}
    try:
        arp_table = subprocess.check_output(['arp', '-a']).decode('utf-8')
        for line in arp_table.splitlines():
            parts = line.split()
            if len(parts) >= 2:
                ip_address = parts[0]
                mac_address = parts[1].replace("-", ":").lower()
                active_devices[mac_address] = ip_address
    except Exception as e:
        print(f"Error executing arp command: {e}")
    return active_devices

def get_ip_from_mac(mac_address):
    active_devices = scan_network()
    mac_address = mac_address.replace("-", ":").lower()
    return active_devices.get(mac_address)