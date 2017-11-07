class Device:

    device_count = 0

    def __init__(self, host_name, ip_address, mac_address, netclass, role):
        self.host_name = host_name
        self.ip_address = ip_address
        self.mac_address = mac_address
        self.netclassif = netclass
        Device.device_count = Device.device_count + 1

    @property
    def host_name(self):
        return self.host_name
    @host_name.setter
    def host_name(self, value):
        self.host_name = value

    @property
    def ip_address(self):
        return self.ip_address
    @ip_address.setter
    def ip_address(self, value):
        self.ip_address = value

    @property
    def mac_address(self):
        return self.mac_address
    @mac_address.setter
    def mac_address(self, value):
        self.mac_address = value

    @property
    def netclass(self):
        return self.netclass
    @netclass.setter
    def netclass(self, value):
        self.netclass = value

    @property
    def role(self):
        return self.role
    @role.setter
    def role(self, value):
        self.role = value
