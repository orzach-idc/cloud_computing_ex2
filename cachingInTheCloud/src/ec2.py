import boto3
import sys
from src.elb import create_ec2_instances, register_instance_in_elb

if __name__=="__main__":
    instances = create_ec2_instances(sys.argv[1])
                                              
    for i in range(len(instances["Instances"])):
        instance_id = instances["Instances"][i]["InstanceId"]
        ec2_resource = boto3.resource('ec2')
        instance = ec2_resource.Instance(instance_id) 
        instance.wait_until_running()
        register_instance_in_elb(instance_id)
