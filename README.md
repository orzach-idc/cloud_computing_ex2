# **Caching in the cloud app by Hila Mizrahi and Or Zachchinsky**

**Please follow the following steps to start your app:**
- 

**Step 1** - clone the cloud_computing_ex2 repository - "https://github.com/orzach-idc/cloud_computing_ex2.git"

**Step 2** - go to the src folder inside the cloned repository in your terminal (cd cloud_computing_ex2/cachingInTheCloud/src)

**Step 3** - run the init1.sh script - "./init1.sh" 

**Step 4** - enter your AWS credntials to finish the AWS configure command 

**Step 5** - run the following commands:
   *  export AWS_ACCESS_KEY_ID=$(sudo aws configure get aws_access_key_id)
   *  export AWS_SECRET_ACCESS_KEY=$(sudo aws configure get aws_secret_access_key)
   *  export AWS_DEFAULT_REGION=$(sudo aws configure get region)

**Step 6** - create the app infrastructure(ELB, securtiy groupt, etc..) by running this command  - "sudo python3 elb.py"
**Step 7** - create instances by running this command - "sudo python3 create_ec2.py <number of instances to create - minimum 2> $AWS_ACCESS_KEY_ID $AWS_SECRET_ACCESS_KEY $AWS_DEFAULT_REGION"

**Step 8** - wait until all your instances are healthy (you have two ways to check it):

   *  go to the "cache-elb-tg" target group in your AWS console and check the healthy status under the "Targets" tab
   *  use the "get_targets_status" function from the "elb.py" API

**Step 9** - start using the app by sending the following http requests:

   *  POST request - <ELB public DNS name>/put?str_key=<your_key_value>&data=<your_data>&expiration_date=<your_date in the format dd-mm-yyyy>
   *  GET request - <ELB public DNS name>/get?str_key=<your_key_value>
