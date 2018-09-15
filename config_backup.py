import os
import time
from device import Device
class ConfigBackup(Device):
    """ Saves a device running configuration to a file only when there is a configuration change."""
    def check_host_conf_dir(self):
        """ Create host directory for host running configuration backup."""
        if not os.path.exists(self.run_dir):
            print("<<<< Creating Directory for {hn} >>>>".format(hn=self.hostname))
            os.makedirs(self.run_dir)

    def get_running_config(self):
        """ Returns device running configuration. """
        self.napalm_device.open()
        print("<<<< Fetching running-config for Device {hn} >>>>".format(hn=self.hostname))
        config = self.napalm_device.get_config()
        self.napalm_device.close()
        run_conf = config["running"]
        running_config = run_conf.split('\n')
        return running_config

    def get_last_running_config(self):
        """ Returns last saved running configuration."""
        if os.path.exists(self.run_dir):
            files = os.listdir(self.run_dir)
            files.sort(reverse=True)
            last_config_file = open(self.run_dir+files[0], 'r')
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
            Retruns False if there is a difference between the device running configuration
            and the last saved device configuration.
        """
        return set(self.last_running_config) == set(self.running_config)

    def write_new_config(self):
        """ 
            Writes device configuration to.
            'hostname-YY-MM-DD--HH-MM.log'
        """
        with open(self.run_dir+self.hostname+'-'+time.strftime("%Y-%m-%d--%H-%M")+'.log', 'w') as file:
            print(">>> Writing new configuration to file {file} \n".format(file=file.name))
            print("="*80,end='\n')
            for each_line in self.running_config:
                file.write(each_line+'\n')

    def running_config_backup(self):
        """ Configuration backup function."""
        if self.state == "up":
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