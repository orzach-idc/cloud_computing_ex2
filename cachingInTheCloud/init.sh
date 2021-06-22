# update packages
sudo apt update

# installing pip for python 3
sudo apt install python3-pip

# installing aws cli
sudo pip3 install --upgrade awscli

# installing aws sam 
sudo pip3 install aws-sam-cli

# Configure AWS setup
aws configure

# # setting credentials environment variables 
cd .aws
python3 ../cloud_computing_ex2/cachingInTheCloud/src set_environ_variables.py
 
