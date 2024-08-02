# Hercules SFTP Setup
This script is intended to first copy files from a local server. It then starts Hercules jobs tho send each file to a remote destination.


### Config
The setup can be configured via a json config file. For this just add a `config.json` file to the main directory with the following contents:
```
{
    "target_ip": "", 
    "username": "",
    "ssh_key_file": "",
    "temp_dir": "",
    "target_dir": "",
    "hercules_path": "",
    "hercules_interface": "",
    "hercules_local_address": "",
    "hercules_destination_address": ""
}
```