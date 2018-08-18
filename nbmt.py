from napalm import get_network_driver
import time
import os
import json

hosts = json.load(open('hosts.json'))

def check_main_directories():
    if not os.path.exists('running-config'):
        print('Creating "running-config" Directory')
        os.makedirs('running-config')

def get_credentials(hosts, host):
    if "username" and "password" in hosts["devices"][host].keys():
        username = hosts["devices"][host]["username"]
        password = hosts["devices"][host]["password"]
    elif "username" and "password" in hosts["creds"]:
        username = hosts["creds"]["username"]
        password = hosts["creds"]["password"]
    return username,password

def get_napalm_device(hosts,host):
    if hosts["devices"][host]["driver"] == 'cisco_ios':
        cisco_ios = get_network_driver('ios')
        device = cisco_ios(hosts["devices"][host]["ip"], username, password)
    elif hosts["devices"][host]["driver"] == 'cisco_iosxr':
        cisco_iosxr = get_network_driver('iosxr')
        device = cisco_iosxr(hosts["devices"][host]["ip"], username, password)
    elif hosts["devices"][host]["driver"] == 'juniper':
        juniper = get_network_driver('junos')
        device = juniper(hosts["devices"][host]["ip"], username, password)
    return device

def get_host_state(hosts,host):
    if "state" in hosts["devices"][host].keys():
        return hosts["devices"][host]["state"]
    else:
        return "no-state"

def get_running_config(device):
        device.open()
        print("<<<< Fetching running-config for Device {hn} >>>>".format(hn=hostname))
        config = device.get_config()
        device.close()
        run_conf = config["running"]
        running_config = run_conf.split('\n')
        return running_config

def get_last_running_config(hostname):
    if os.path.exists('running-config/'+hostname):
        files = os.listdir('running-config/'+hostname+'/')
        files.sort(reverse=True)
        last_config_file = open('running-config/'+hostname+'/'+files[0], 'r')
        last_running_config = []
        for config in last_config_file:
            last_running_config.append(config.strip('\n'))
        last_config_file.close()
    else:
        last_running_config = []
        last_config_file = 'File not found!'
    return last_running_config,last_config_file.name

def config_diff_result(last_running_config, running_config):
    return set(last_running_config) == set(running_config)

def write_new_config(hostname, running_config):
    if not os.path.exists('running-config/'+hostname):
        print("<<<< Creating Directory for {hn} \n >>>>".format(hn=hostname))
        os.makedirs('running-config/'+hostname)
    with open('running-config/'+hostname+'/'+hostname+'-'+time.strftime("%Y-%m-%d--%H-%M")+'.log', 'w') as file:
        print(">>> Writing to file {file} \n".format(file=file.name))
        print("="*80,end='\n')
        for each_line in running_config:
            file.write(each_line+'\n')

for host in hosts["devices"].keys():
    hostname = host
    state = get_host_state(hosts,host)
    if state == "up":
        username = get_credentials(hosts,host)[0]
        password = get_credentials(hosts,host)[1]
        device = get_napalm_device(hosts,host)
    elif state == "down":
        print(">>> Skippping Host {hn} \n".format(hn=hostname))
        print("="*80)
        continue
    else:
        print(">>> Undefined State for Host {hn} \n".format(hn=hostname))
        print("="*80)
        continue

    try:
        running_config = get_running_config(device)
        last_running_config = get_last_running_config(hostname)[0]
        last_config_file = get_last_running_config(hostname)[1]
        diff_config_result = config_diff_result(last_running_config, running_config)

        if diff_config_result == False:
            write_new_config(hostname, running_config)
        else:
            print(">>> No Changes Since Last Run")
            print(">>> Last Config File '{lcf}' \n".format(lcf=last_config_file))
            print("="*80,end='\n')

    except Exception as e:
        print("<<<< Unable to Connect to Device {hn} >>>>".format(hn=hostname))
        print(">>> "+str(type(e)))
        print(">>> "+str(e))
        print("="*80,end='\n')