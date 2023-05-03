import os
import boto3

class DynamoManager:
    def __init__(self, table_name):
        self.access_key = os.environ.get("AWS_ACCESS_KEY_ID")
        self.secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
        self.region_name = os.environ.get("AWS_REGION")
        self.session = boto3.Session(
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region_name
        )
        self.dynamodb = self.session.client('dynamodb')
        self.table_name = table_name
        self.table = self.retrieve_or_create_table()

    def retrieve_or_create_table(self):
        try:
            table = self.dynamodb.describe_table(TableName=self.table_name)['Table']
            print(f"Table '{self.table_name}' found")
        except self.dynamodb.exceptions.ResourceNotFoundException:
            print(f"Table '{self.table_name}' does not exist, creating it...")
            table = self.dynamodb.create_table(
                TableName=self.table_name,
                KeySchema=[
                    {
                        'AttributeName': 'id',
                        'KeyType': 'HASH'
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'id',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'page_url',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'page_text',
                        'AttributeType': 'S'
                    }
                ],
                BillingMode='PAY_PER_REQUEST',
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'page_url_index',
                        'KeySchema': [
                            {
                                'AttributeName': 'page_url',
                                'KeyType': 'HASH'
                            }
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'
                        }
                    }
                ]
            )
            waiter = self.dynamodb.get_waiter('table_exists')
            waiter.wait(TableName=self.table_name)
            print(f"Table '{self.table_name}' created")
        return table

    def put_item(self, item):
        # Check that the item has the correct structure
        if 'id' not in item or 'page_url' not in item or 'page_text' not in item:
            print("Error: item is missing one or more required attributes")
            return

        # Check that the table exists
        try:
            self.dynamodb.describe_table(TableName=self.table_name)
        except self.dynamodb.exceptions.ResourceNotFoundException:
            print(f"Error: table '{self.table_name}' does not exist")
            return

        # Add the item to the table
        self.table.put_item(Item=item)
        print(f"Item with ID '{item['id']}' added to table '{self.table_name}'")
        return item
