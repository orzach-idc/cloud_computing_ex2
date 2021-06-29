import boto3
import sys
import elb
import os

images_dict_by_region = {
    'us-east-1': 'ami-09e67e426f25ce0d7',
    'us-east-2': 'ami-00399ec92321828f5',
    'us-west-1': 'ami-0d382e80be7ffdae5',
    'us-west-2': 'ami-03d5c68bab01f3496',
    'ca-central-1': 'ami-0801628222e2e96d6',
    'eu-central-1': 'ami-05f7491af5eef733a',
    'eu-west-1': 'ami-0a8e758f5e873d1c1',
    'eu-west-2': 'ami-0194c3e07668a7e36',
    'eu-west-3': 'ami-0f7cd40eac2214b37',
    'eu-north-1': 'ami-0ff338189efb7ed37',
    'sa-east-1': 'ami-054a31f1b3bf90920'}

if __name__=="__main__":
    if len(sys.argv) < 4:
        print(len(sys.argv))
        print("""problem with aws credentials please run the following commands:
        - sudo aws configure
        - export AWS_ACCESS_KEY_ID=$(sudo aws configure get aws_access_key_id)
        - export AWS_SECRET_ACCESS_KEY=$(sudo aws configure get aws_secret_access_key)
        - export AWS_DEFAULT_REGION=$(sudo aws configure get region)
        - sudo python3 create_ec2.py <num of instances> $AWS_ACCESS_KEY_ID $AWS_SECRET_ACCESS_KEY $AWS_DEFAULT_REGION
        """)

        exit()
        
    ec2_user_data = elb.create_ec2_user_data(sys.argv[2], sys.argv[3], sys.argv[4])    
    instances = elb.create_ec2_instances(sys.argv[1], ec2_user_data, images_dict_by_region[sys.argv[4]])
                                              
    for i in range(len(instances["Instances"])):
        instance_id = instances["Instances"][i]["InstanceId"]
        ec2_resource = boto3.resource('ec2')
        instance = ec2_resource.Instance(instance_id) 
        print(f"Please wait, instance {i + 1} is being initiated..")
        instance.wait_until_running()
        elb.register_instance_in_elb(instance_id)
        print(f"Instance {i + 1} created successfully")
