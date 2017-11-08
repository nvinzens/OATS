class Device:

    device_count = 0

    def __init__(self, host_name, ip_address, mac_address, netclass, role):
        self.host_name = host_name
        self.ip_address = ip_address
        self.mac_address = mac_address
        self.netclassif = netclass
        Device.device_count = Device.device_count + 1
