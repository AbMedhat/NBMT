from napalm import get_network_driver

class Device(object):
    """ Device base Class """
    def __init__(self, hostname, ip, state, username, password, driver,run_dir):
        self.hostname = hostname
        self.ip = ip
        self.state = state
        self.username = username
        self.password = password
        self.driver = driver
        self.run_dir = run_dir
        self.napalm_driver = get_network_driver(self.driver)
        self.napalm_device = self.napalm_driver(self.ip,self.username,self.password)
    
    def __repr__(self):
        """ 
            Returns:
            hostname, ip, state, username, password, driver, run_dir 
        """
        return "hostname: {}, ip: {}, state: {}, username: {}, password: {}, driver: {}, run_dir {}"\
        .format(self.hostname,self.ip,self.state,self.username,self.password,self.driver,self.run_dir)