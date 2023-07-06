import boto3


    instance_list = []
    for instance in instances:
        instance_id = instance.id
        instance_name = get_instance_name(instance)
        instance_list.append((instance_id, instance_name))
    
    return instance_list