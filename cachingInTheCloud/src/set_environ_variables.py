import os
credentials_file = open("credentials", "r")
next(credentials_file)
config_file = open("config", "r")
next(config_file)

# extracting from config and credentials file
aws_access_key_id = credentials_file.readline().split('= ')[1]
aws_secret_access_key_id = credentials_file.readline().split('= ')[1]
aws_default_region = config_file.readline().split('= ')[1]

# setting environments variables
os.environ["AWS_ACCESS_KEY_ID"] = aws_access_key_id
os.environ["AWS_SECRET_ACCESS_KEY_ID"] = aws_secret_access_key_id
os.environ["AWS_DEFAULT_REGION"] = aws_default_region

print(os.environ.get("AWS_ACCESS_KEY_ID""))
