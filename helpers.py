import yaml
from config_backup import ConfigBackup

def loadConfig(file):
    """ Generator that builds and passes device parameters. """
    with open(file, 'r') as f:
        inventory = yaml.load(f)
    for hostname in inventory['routers'].keys():
        device = inventory['routers'][hostname]
        device['hostname'] = hostname
        device['run_dir'] = inventory['routers'][hostname]['run_dir'] + hostname + '/'
        yield device

def deviceBackup(device):
    """ Invoke device running configuration backup"""
    device = ConfigBackup(device['hostname'],device['ip'],device['state'],device['username'],device['password'],device['driver'],device['run_dir'])
    device.running_config_backup()