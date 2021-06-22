import boto3
import sys
import elb
import os

if __name__=="__main__":
    print(os.environ.get("AWS_ACCESS_KEY_ID"))
    instances = elb.create_ec2_instances(sys.argv[1])
                                              
    for i in range(len(instances["Instances"])):
        instance_id = instances["Instances"][i]["InstanceId"]
        ec2_resource = boto3.resource('ec2')
        instance = ec2_resource.Instance(instance_id) 
        print("Please wait, instances are being initiated..")
        instance.wait_until_running()
        elb.register_instance_in_elb(instance_id)
        print("Instances are running")
