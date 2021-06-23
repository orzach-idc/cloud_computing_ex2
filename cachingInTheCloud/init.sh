# update packages
sudo apt update

# installing pip for python 3
sudo apt install python3-pip

# installing aws cli
sudo pip3 install --upgrade awscli

# installing aws sam 
sudo pip3 install aws-sam-cli

# Configure AWS setup
sudo aws configure

# setting credentials environment variables
export AWS_ACCESS_KEY_ID=$(sudo aws configure get aws_access_key_id)
export AWS_SECRET_ACCESS_KEY=$(sudo aws configure get aws_secret_access_key)
export AWS_DEFAULT_REGION=$(sudo aws configure get aws_default_region)
