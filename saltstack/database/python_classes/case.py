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
