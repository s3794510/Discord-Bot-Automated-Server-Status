import boto3
from botocore.exceptions import ClientError

def check_instance_exists(instance_id):
    try:
        ec2 = boto3.client('ec2')
        response = ec2.describe_instances(InstanceIds=[instance_id])
        reservations = response['Reservations']
        return len(reservations) > 0
    except ClientError as e:
        if e.response['Error']['Code'] == 'InvalidInstanceID.NotFound':
            return False
        else:
            # Handle other exceptions if needed
            print(f"An error occurred while checking instance existence: {e.response['Error']['Message']}")
            return False

def start_instance(instance_id):
    ec2 = boto3.client('ec2')
    response = ec2.start_instances(InstanceIds=[instance_id])
    print(f"Starting instance {instance_id}")
    return(response)

def stop_instance(instance_id):
    ec2 = boto3.client('ec2')
    response = ec2.stop_instances(InstanceIds=[instance_id])
    print(f"Stopping instance {instance_id}")
    return(response)

def get_instance_name(instance):
    for tag in instance.tags:
        if tag['Key'] == 'Name':
            return tag['Value']
    return ''

def list_instances():
    ec2 = boto3.resource('ec2')
    instances = ec2.instances.all()
    
    instance_list = []
    for instance in instances:
        instance_id = instance.id
        instance_name = get_instance_name(instance)
        instance_list.append((instance_id, instance_name))
    
    return instance_list