""" Network Backup and Management Tool"""
import configparser
from config_backup import ConfigBackup

# Load the inventory file
inventory = configparser.ConfigParser()
inventory.read('inventory')

# Call ConfigBackup
backup = ConfigBackup(inventory)
backup.running_config_backup()