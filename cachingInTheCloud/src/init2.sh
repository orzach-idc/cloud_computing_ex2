# export environment credentials variables
export AWS_ACCESS_KEY_ID=$(sudo aws configure get aws_access_key_id)
export AWS_SECRET_ACCESS_KEY=$(sudo aws configure get aws_secret_access_key)
export AWS_DEFAULT_REGION=$(sudo aws configure get region)

# run elb file
# sudo python3 elb.py
