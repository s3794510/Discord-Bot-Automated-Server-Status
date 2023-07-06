import boto3

dynamodb = boto3.resource('dynamodb')
table_name = 'BotTable'


def create_item(key, value):
    data = {'item':key,'value':value}
    table = dynamodb.Table(table_name)
    response = table.put_item(Item=data)
    return response

def read_item(item):
    key = {
        'item': item
    }
    table = dynamodb.Table(table_name)
    response = table.get_item(Key=key)
    data = response.get('Item')
    try:
        return data['value']
    except TypeError:
        return None

def update_item(key, update_expression, expression_attribute_values):
    table = dynamodb.Table(table_name)
    response = table.update_item(
        Key=key,
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_attribute_values,
        ReturnValues='UPDATED_NEW'
    )
    updated_item = response.get('Attributes')
    return updated_item

# def get_items_with_prefix(prefix):
#     table = dynamodb.Table(table_name)
#     response = table.scan(
#         FilterExpression=boto3.dynamodb.conditions.Key('item_key').begins_with(prefix)
#     )
#     items = response['Items']
#     return items


def delete_item(item):
    key = {'item':item}
    table = dynamodb.Table(table_name)
    response = table.delete_item(Key=key)
    return response

def exist(item, value):
    return read_item(item) == value

def exist_item(item):
    table = dynamodb.Table(table_name)
    response = table.get_item(Key={'item': item})
    item = response.get('Item')
    return item is not None

def get_bottoken():
    item_bottoken= 'BOTTOKEN'
    return read_item(item_bottoken)

