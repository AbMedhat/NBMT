""" Network Backup and Management Tool"""
from helpers import loadConfig, deviceBackup

for device in loadConfig('inventory.yml'):
    deviceBackup(device)