#!/bin/bash
git clone https://github.com/orzach-idc/cloud_computing_ex2.git
cd cloud_computing_ex2/cachingInTheCloud/src
./ec2_init.sh 
sudo python3 test.py
