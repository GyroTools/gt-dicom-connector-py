class gtDicomConnection():
    def __init__(self, host, port, user=None, password=None, calling_aet='GETSCU', called_aet='ANY-SCP'):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.calling_aet = calling_aet
        self.called_aet = called_aet