class Technician:

    technician_count = 0;

    def __init__(self, fname, lname, channel):
        self.first_name = fname
        self.last_name = lname
        self.channel = channel
        Technician.technician_count = Technician.technician_count + 1

    @property
    def first_name(self):
        return self.first_name
    @first_name.setter
    def first_name(self, value):
        self.first_name = value

    @property
    def last_name(self):
        return self.last_name
    @last_name.setter
    def last_name(self, value):
        self.last_name = value

    @property
    def channel(self):
        return self.channel
    @channel.setter
    def channel(self, value):
        self.channel = value

    def printdetails(self):
        print "First name: " + self.first_name + "Last name: " + self.last_name + "Channel: " + self.channel
