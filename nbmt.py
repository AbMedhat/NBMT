from napalm import get_network_driver
import time
import os
import json

cisco_ios = get_network_driver('ios')
cisco_iosxr = get_network_driver('iosxr')
juniper = get_network_driver('junos')

hosts = json.load(open('hosts.json'))

if not os.path.exists('running-config'):
    print('Creating "running-config" Directory')
    os.makedirs('running-config')


for host in hosts.get("routers"):

    hostname = host["name"]

    if host["driver"] == 'cisco_ios':
        device = cisco_ios(host["ip"], host["username"], host["password"])
    elif host["driver"] == 'cisco_iosxr':
        device = cisco_iosxr(host["ip"], host["username"], host["password"])
    elif host["driver"] == 'juniper':
        device = juniper(host["ip"], host["username"], host["password"])
    else:
        raise "Unkown Device type"

    try:
        device.open()
        #facts = device.get_facts()
        #hostname = facts["hostname"]
        print("Fetching running-config for Device %s") %hostname
        config = device.get_config()
        running_config = config["running"]
        if not os.path.exists('running-config/'+hostname):
            print("Creating Directory for %s") % hostname
            os.makedirs('running-config/'+hostname)
        with open('running-config/'+hostname+'/'+hostname+'-'+time.strftime("%Y-%m-%d--%H-%M")+'.log', 'w') as file:
            print("Writing to file %s") %file.name
            file.write('\n')
            run_conf = running_config.split('\n')
            for each_line in run_conf:
                file.write(each_line+'\n')
        device.close()
    except:
        print("Unable to Connect to Device %s") %hostname