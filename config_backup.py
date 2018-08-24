import os
import time
from napalm import get_network_driver
from helpers import DeviceInfo

class ConfigBackup(object):
    """ Saves a device running configuration to a file only when there is a configuration change."""
    def __init__(self,inventory):
        self.inventory = inventory

    def check_main_conf_dir(self):
        """ Create the main directory for running configuration backups if it doesnt exist."""
        if not os.path.exists(self.conf_dir):
            print('Creating Running Configuration Directory')
            os.makedirs(self.conf_dir)

    def check_host_conf_dir(self):
        """ Create host directory for host running configuration backup."""
        if not os.path.exists(self.device_conf_dir):
            print("<<<< Creating Directory for {hn} >>>>".format(hn=self.hostname))
            os.makedirs(self.device_conf_dir)

    def get_napalm_device(self):
        """ Returns napalm device driver. """
        napalm_driver = get_network_driver(self.device_type)
        napalm_device = napalm_driver(self.ip,self.username,self.password)
        return napalm_device

    def get_running_config(self):
        """ Return device running configuration. """
        self.napalm_device.open()
        print("<<<< Fetching running-config for Device {hn} >>>>".format(hn=self.hostname))
        config = self.napalm_device.get_config()
        self.napalm_device.close()
        run_conf = config["running"]
        running_config = run_conf.split('\n')
        return running_config

    def get_last_running_config(self):
        """ Returns last saved running configuration."""
        if os.path.exists(self.device_conf_dir):
            files = os.listdir(self.device_conf_dir)
            files.sort(reverse=True)
            last_config_file = open(self.device_conf_dir+files[0], 'r')
            last_running_config = []
            for config in last_config_file:
                last_running_config.append(config.strip('\n'))
            last_config_file.close()
        else:
            last_running_config = []
            last_config_file = 'File not found!'
        return last_running_config,last_config_file

    def config_diff_result(self):
        """ 
            Retrun False if there is a difference between the device running configuration
            and the last saved device configuration.
        """
        return set(self.last_running_config) == set(self.running_config)

    def write_new_config(self):
        """ 
            Writes device configuration to.
            'hostname-YY-MM-DD--HH-MM.log'
        """
        with open(self.device_conf_dir+self.hostname+'-'+time.strftime("%Y-%m-%d--%H-%M")+'.log', 'w') as file:
            print(">>> Writing new configuration to file {file} \n".format(file=file.name))
            print("="*80,end='\n')
            for each_line in self.running_config:
                file.write(each_line+'\n')

    def running_config_backup(self):
        """ Configuration backup function."""
        self.conf_dir = self.inventory['DEFAULT']['running_config_dir']
        self.check_main_conf_dir()
        for host in self.inventory.sections():
            self.hostname = host
            self.device_info = DeviceInfo(self.inventory,host)
            self.state = self.device_info.get_state()
            if self.state == "up":
                self.device_type = self.device_info.get_type()
                self.username = self.device_info.get_creds()[0]
                self.password = self.device_info.get_creds()[1]
                self.ip = self.device_info.get_ip()
                self.napalm_device = self.get_napalm_device()
                self.device_conf_dir = self.conf_dir + self.hostname + '/'
                try:
                    self.running_config = self.get_running_config()
                    self.last_running_config = self.get_last_running_config()[0]
                    self.last_config_file = self.get_last_running_config()[1]
                    self.diff_config_result = self.config_diff_result()
                    if self.diff_config_result == False:
                        self.check_host_conf_dir()
                        self.write_new_config()
                    else:
                        print(">>> No Changes Since Last Run")
                        print(">>> Last Config File '{lcf}' \n".format(lcf=self.last_config_file.name))
                        print("="*80,end='\n')
                except Exception as e:
                    print("<<<< Unable to Connect to Device {hn} >>>>".format(hn=self.hostname))
                    print(">>> "+str(type(e)))
                    print(">>> "+str(e))
                    print("="*80,end='\n')
            elif self.state == "down":
                print(">>> Skippping Host {hn} \n".format(hn=self.hostname))
                print("="*80)
            else:
                print(">>> Undefined State for Host {hn} \n".format(hn=self.hostname))
                print("="*80)