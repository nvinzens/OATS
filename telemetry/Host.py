

class OATSHost:
    '''
    Data object for the host(s) specified in the oats config file.
    '''

    def __init__(self, hostname, port, username, password):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
