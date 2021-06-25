import boto3
import sys
import elb
import os

if __name__=="__main__":
    if len(sys.argv) < 4:
        print("""problem with aws credentials please run the following commands:
        - sudo aws configure
        - ./init2.sh
        - sudo python3 create_ec2.py <num of instances> $AWS_ACCESS_KEY_ID $AWS_SECRET_ACCESS_KEY $AWS_DEFAULT_REGION
        """)

        exit()
        
    ec2_user_data = elb.create_ec2_user_data(sys.argv[2], sys.argv[3], sys.argv[4])    
    instances = elb.create_ec2_instances(sys.argv[1], ec2_user_data)
                                              
    for i in range(len(instances["Instances"])):
        instance_id = instances["Instances"][i]["InstanceId"]
        ec2_resource = boto3.resource('ec2')
        instance = ec2_resource.Instance(instance_id) 
        print("Please wait, instances are being initiated..")
        instance.wait_until_running()
        elb.register_instance_in_elb(instance_id)
        print("Instances are running")
