from napalm import get_network_driver
import time
import os
import configparser

hosts = configparser.ConfigParser()
hosts.read('inventory')

def check_main_directories(hosts):
    if not os.path.exists(hosts['DEFAULT']['running_config_dir']):
        print('Creating Running Configuration Directory')
        os.makedirs(hosts['DEFAULT']['running_config_dir'])

def get_credentials(hosts, host):
    if "username" and "password" in hosts.options(host):
        return hosts[host]["username"],hosts[host]["password"]

def get_napalm_device(hosts,host,username,password):
    driver = get_network_driver(hosts[host]["driver"])
    device = driver(hosts[host]["ip"],username,password)
    return device

def get_host_state(hosts,host):
    return hosts[host]["state"]

def get_running_config(device,hostname):
        device.open()
        print("<<<< Fetching running-config for Device {hn} >>>>".format(hn=hostname))
        config = device.get_config()
        device.close()
        run_conf = config["running"]
        running_config = run_conf.split('\n')
        return running_config

def get_last_running_config(hostname):
    if os.path.exists(hosts['DEFAULT']['running_config_dir']+hostname):
        files = os.listdir(hosts['DEFAULT']['running_config_dir']+hostname+'/')
        files.sort(reverse=True)
        last_config_file = open(hosts['DEFAULT']['running_config_dir']+hostname+'/'+files[0], 'r')
        last_running_config = []
        for config in last_config_file:
            last_running_config.append(config.strip('\n'))
        last_config_file.close()
    else:
        last_running_config = []
        last_config_file = 'File not found!'
    return last_running_config,last_config_file

def config_diff_result(last_running_config, running_config):
    return set(last_running_config) == set(running_config)

def write_new_config(hosts,hostname, running_config):
    if not os.path.exists(hosts['DEFAULT']['running_config_dir']+hostname):
        print("<<<< Creating Directory for {hn} \n >>>>".format(hn=hostname))
        os.makedirs(hosts['DEFAULT']['running_config_dir']+hostname)
    with open(hosts['DEFAULT']['running_config_dir']+hostname+'/'+hostname+'-'+time.strftime("%Y-%m-%d--%H-%M")+'.log', 'w') as file:
        print(">>> Writing to file {file} \n".format(file=file.name))
        print("="*80,end='\n')
        for each_line in running_config:
            file.write(each_line+'\n')

def running_config_backup(hosts):
    for host in hosts.sections():
        hostname = host
        state = get_host_state(hosts,host)
        if state == "up":
            username = get_credentials(hosts,host)[0]
            password = get_credentials(hosts,host)[1]
            device = get_napalm_device(hosts,host,username,password)
        elif state == "down":
            print(">>> Skippping Host {hn} \n".format(hn=hostname))
            print("="*80)
            continue
        else:
            print(">>> Undefined State for Host {hn} \n".format(hn=hostname))
            print("="*80)
            continue

        try:
            running_config = get_running_config(device,hostname)
            last_running_config = get_last_running_config(hostname)[0]
            last_config_file = get_last_running_config(hostname)[1]
            diff_config_result = config_diff_result(last_running_config, running_config)

            if diff_config_result == False:
                write_new_config(hosts,hostname, running_config)
            else:
                print(">>> No Changes Since Last Run")
                print(">>> Last Config File '{lcf}' \n".format(lcf=last_config_file.name))
                print("="*80,end='\n')

        except Exception as e:
            print("<<<< Unable to Connect to Device {hn} >>>>".format(hn=hostname))
            print(">>> "+str(type(e)))
            print(">>> "+str(e))
            print("="*80,end='\n')

check_main_directories(hosts)
running_config_backup(hosts)