import boto3

dynamodb = boto3.resource('dynamodb')
table_name = 'BotTable'


def create_item(key, value):
    data = {'item':key,'value':value}
    table = dynamodb.Table(table_name)
    response = table.put_item(Item=data)
    return response

def read_item(key):
    table = dynamodb.Table(table_name)
    response = table.get_item(Key=key)
    item = response.get('Item')
    return item['value']

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

def delete_item(key):
    table = dynamodb.Table(table_name)
    response = table.delete_item(Key=key)
    return response


item = {
    'item': '123',
    'name': 'John Doe',
    'age': 25
}

def get_bottoken():
    key_bottoken= {'item':'BOTTOKEN'}
    return read_item(key_bottoken)

