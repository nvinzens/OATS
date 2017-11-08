class Technician:

    technician_count = 0;

    def __init__(self, fname, lname, channel):
        self.first_name = fname
        self.last_name = lname
        self.channel = channel
        Technician.technician_count = Technician.technician_count + 1
