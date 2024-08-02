# Hercules SFTP Setup
This script is intended to first copy files from a local server. It then starts a Hercules jobs to send each file to a remote destination.
Make sure hercules is also started on the destination.

## Config
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

## Open issues
- does hercules somehow send the filename to the destination?
- does hercules handle small files? (Had issues with test files that are just a few bytes in size.)