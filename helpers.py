class DeviceInfo(object):
    """
    Returns 'device' information (credentials, state, type, ip)
    """
    def __init__(self,inventory,hostname):
        self.inventory = inventory
        self.hostname = hostname
    def get_creds(self):
        """ returns host username and password """
        return self.inventory[self.hostname]["username"],self.inventory[self.hostname]["password"]
    def get_state(self):
        """ returns host state """
        return self.inventory[self.hostname]["state"]
    def get_type(self):
        """ return host type """
        return self.inventory[self.hostname]['driver']
    def get_ip(self):
        """ return host ip address """
        return self.inventory[self.hostname]['ip']