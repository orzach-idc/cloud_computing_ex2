import boto3
import sys
from botocore import exceptions
import os

PREFIX="cache-elb"

elb = boto3.client('elbv2')
ec2 = boto3.client('ec2')


def init_security_groups(vpc_id):
    try:
        response = ec2.describe_security_groups(GroupNames=[PREFIX+"elb-access"])
        elb_access = response["SecurityGroups"][0]
        response = ec2.describe_security_groups(GroupNames=[PREFIX+"instance-access"])
        instance_access = response["SecurityGroups"][0]
        return {
            "elb-access": elb_access["GroupId"], 
            "instance-access": instance_access["GroupId"], 
        }
    except exceptions.ClientError as e:
        if e.response['Error']['Code'] != 'InvalidGroup.NotFound':
            raise e

    vpc = ec2.describe_vpcs(VpcIds=[vpc_id])
    cidr_block = vpc["Vpcs"][0]["CidrBlock"]

    elb = ec2.create_security_group(
        Description="ELB External Access",
        GroupName=PREFIX+"elb-access",
        VpcId=vpc_id
    )
    elb_sg = boto3.resource('ec2').SecurityGroup(elb["GroupId"])
    elb_sg.authorize_ingress(
        CidrIp="0.0.0.0/0",
        FromPort=80,
        ToPort=80,
        IpProtocol="TCP",
    )
    
    elb_sg.authorize_ingress(
        CidrIp=cidr_block,
        FromPort=80,
        ToPort=80,
        IpProtocol="TCP",
    )
    
    instances = ec2.create_security_group(
        Description="ELB Access to instances",
        GroupName=PREFIX+"instance-access",
        VpcId=vpc_id
    )
    instance_sg = boto3.resource('ec2').SecurityGroup(instances["GroupId"])
    instance_sg.authorize_ingress(
        CidrIp="0.0.0.0/0",
        FromPort=80,
        ToPort=80,
        IpProtocol="TCP",
    )
    instance_sg.authorize_ingress(
        CidrIp= cidr_block,
        FromPort=80,
        ToPort=80,
        IpProtocol="TCP",
    )
    return {
        "elb-access": elb["GroupId"], 
        "instance-access": instances["GroupId"]
    }
    


def get_default_subnets():
    response = ec2.describe_subnets(
        Filters=[{"Name": "default-for-az", "Values": ["true"]}]
    )
    subnetIds = [s["SubnetId"] for s in response["Subnets"]]
    return subnetIds

# creates the ELB as well as the target group
# that it will distribute the requests to
def ensure_elb_setup_created():
    response = None
    try:
        response = elb.describe_load_balancers(Names=[PREFIX])
    except exceptions.ClientError as e:
        if e.response['Error']['Code'] != 'LoadBalancerNotFound':
            raise e
        subnets = get_default_subnets()
        response= elb.create_load_balancer(
            Name=PREFIX,
            Scheme='internet-facing',
            IpAddressType='ipv4',
            Subnets=subnets,
        )
    elb_arn = response["LoadBalancers"][0]["LoadBalancerArn"]
    vpc_id = response["LoadBalancers"][0]["VpcId"]
    results = init_security_groups(vpc_id)
    elb.set_security_groups(
        LoadBalancerArn=elb_arn,
        SecurityGroups=[results["elb-access"]]
    )
    target_group=None
    try:
         target_group = elb.describe_target_groups(
            Names=[PREFIX +"-tg"],
        )
    except exceptions.ClientError as e:
        if e.response['Error']['Code'] != 'TargetGroupNotFound':
            raise e
        target_group = elb.create_target_group(
            Name=PREFIX +"-tg",
            Protocol="HTTP",
            Port=80,
            VpcId=vpc_id,
            HealthCheckProtocol="HTTP",
            HealthCheckPort="80",
            HealthCheckPath="/healthcheck",
            TargetType="instance",
            HealthCheckIntervalSeconds = 10,
            HealthCheckTimeoutSeconds = 5,
            HealthyThresholdCount = 2,
            UnhealthyThresholdCount = 2
        )
    target_group_arn= target_group["TargetGroups"][0]["TargetGroupArn"]
    listeners = elb.describe_listeners(LoadBalancerArn=elb_arn)
    if len(listeners["Listeners"]) == 0:
        elb.create_listener(
            LoadBalancerArn=elb_arn,
            Protocol="HTTP",
            Port=80,
            DefaultActions=[
                {
                    "Type": "forward",
                    "TargetGroupArn": target_group_arn,
                    "Order": 100
                }
            ]
        )
    return results 

def register_instance_in_elb(instance_id):
    results = ensure_elb_setup_created()
    target_group = elb.describe_target_groups(
        Names=[PREFIX + "-tg"],
    )
    instance = boto3.resource('ec2').Instance(instance_id)
    sgs = [sg["GroupId"] for sg in instance.security_groups]
    sgs.append(results["instance-access"])
    instance.modify_attribute(
        Groups=sgs
    )
    target_group_arn = target_group["TargetGroups"][0]["TargetGroupArn"]
    elb.register_targets(
        TargetGroupArn=target_group_arn,
        Targets=[{
            "Id": instance_id,
            "Port": 80
        }]
    )

def get_targets_status():
    target_group = elb.describe_target_groups(
        Names=[PREFIX+"-tg"],
    )
    target_group_arn= target_group["TargetGroups"][0]["TargetGroupArn"]
    health = elb.describe_target_health(TargetGroupArn=target_group_arn)
    healthy=[]
    sick={}
    for target in health["TargetHealthDescriptions"]:
        if target["TargetHealth"]["State"] == "unhealthy":
            sick[target["Target"]["Id"]] = target["TargetHealth"]["Description"]
        else:
            healthy.append(target["Target"])
    return healthy, sick

def get_instance_public_ip(instance_id):
    filters = [{
        "Name": "instance-id",
        "Values": [instance_id],
    }]
    return ec2.describe_instances(Filters=filters)['Reservations'][0]['Instances'][0]['PublicIpAddress']

def create_ec2_instances(num_instances):
    ec2_user_data = f"""#cloud-config

    runcmd:
    - cd home/ubuntu
    - git clone https://github.com/orzach-idc/cloud_computing_ex2.git
    - cd cloud_computing_ex2/cachingInTheCloud/src
    - chmod 777 *.sh
    - ./ec2_init.sh
    - sudo aws configure set aws_access_key_id {aws_access_key_id}
    - sudo aws configure set aws_secret_access_key {aws_secret_aceess_key} 
    - sudo aws configure set aws_default_region {aws_default_region}
    - sudo python3 elb.py
    - sudo python3 ec2_server.py

    """
    print(ec2_user_data)
    
#     instances = ec2.run_instances(
#           ImageId = 'ami-09e67e426f25ce0d7',
#           MinCount = int(num_instances), 
#           MaxCount = int(num_instances), 
#           InstanceType = "t2.micro",
#           UserData = ec2_user_data)
#     return instances


if __name__=="__main__":  
    if len(argv) == 4:
        aws_access_key_id = sys.argv[1]
        aws_secret_aceess_key = sys.argv[2]
        aws_default_region = sys.argv[3]
#     ensure_elb_setup_created()
#     print(elb.describe_load_balancers()["LoadBalancers"][0]['DNSName'])
