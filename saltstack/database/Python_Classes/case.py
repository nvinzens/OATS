class Case:

    manual_case_count = 0

    def __init__(self, event, description, status, event, involved_devices=None, solution_tried=None):
        self.event = event
        self.description = description
        self.status = status
        self.technician = technician
        if involved_devices is None:
            self.involved_devices = []
        else:
            self.involved_devices = involved_devices
        if solution_tried is None:
            self.solution_tried = []
        else:
            self.solution_tried = solution_tried
        Case.manual_case_count = Case.manual_case_count + 1

    @property
    def event(self):
        return self.event
    @event.setter
    def event(self, value):
        self.event = value

    @property
    def description(self):
        return self.description
    @description.setter
    def description(self, value):
        self.description = value

    @property
    def status(self):
        return self.status
    @status.setter
    def status(self, value):
        self.status = value

    @property
    def technician(self):
        return self.technician
    @technician.setter
    def technician(self, value):
        self.technician = value
