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
        print("<<<< Fetching running-config for Device %s >>>>") %hostname
        config = device.get_config()
        device.close()
        run_conf = config["running"]
        running_config = run_conf.split('\n')
        
        files = os.listdir('running-config/'+hostname+'/')
        files.sort(reverse=True)
        last_config_file = open('running-config/'+hostname+'/'+files[0], 'r')
        last_running_config = []
        for config in last_config_file:
            last_running_config.append(config.strip('\n'))
        last_running_config = map(unicode, last_running_config)
        diff_config_result = set(last_running_config) == set(running_config)

        if diff_config_result == False:
            if not os.path.exists('running-config/'+hostname):
                print("<<<< Creating Directory for %s \n >>>>") % hostname
                os.makedirs('running-config/'+hostname)
            with open('running-config/'+hostname+'/'+hostname+'-'+time.strftime("%Y-%m-%d--%H-%M")+'.log', 'w') as file:
                print(">>> Writing to file %s \n") %file.name
                print("=============================================================================== \n")
                for each_line in run_conf:
                    file.write(each_line+'\n')
        else:
            print(">>> No Changes Since Last Run")
            print(">>> Last Config File '%s' \n") %files[0]
            print("=============================================================================== \n")

    except Exception, e:
        print("<<<< Unable to Connect to Device %s >>>>") %hostname
        print("  "+str(type(e)))
        print("  "+str(e))
        print("================================================================================ \n")