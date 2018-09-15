""" Network Backup and Management Tool"""
from helpers import loadConfig, deviceBackup

for device in loadConfig('inventory.yaml'):
    deviceBackup(device)