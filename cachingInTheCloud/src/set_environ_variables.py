import os
credentials_file = open("credentials", "r")
next(credentials_file)
config_file = open("config", "r")
next(config_file)

aws_access_key_id = credentials_file.readline().split('= ')[1]
aws_secret_access_key_id = credentials_file.readline().split('= ')[1]
aws_default_region = config_file.readline().split('= ')[1]
