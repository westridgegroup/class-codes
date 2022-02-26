import os
from azure.data.tables import TableServiceClient
from azure.core.credentials import AzureNamedKeyCredential
from azure.core.exceptions import HttpResponseError

class Token:
    def __init__(self, customer: str, value: str):
        account_name = os.environ["accountName"]
        account_key = os.environ["accountKey"]
        self.key = base64.b64decode(os.environ["key"]) #b64encoded string
        if len(self.key) not in (16, 24, 32):
            raise ValueError("key must be 128, 192, or 256 bits.")

        endpoint = "https://{0}.table.core.windows.net/".format(account_name)
        self.credential = AzureNamedKeyCredential(account_name, account_key)
        self.table_service = TableServiceClient(endpoint=endpoint, credential=self.credential)
        key_table = "Keys"
        token_table = "Tokens"
        self.key_table_client = self.table_service.get_table_client(key_table)
        self.token_table_client = self.table_service.get_table_client(token_table)
        self.customer = customer
        self.raw_value = value

    def write_token_to_store(self, token_value: str):
        key_entity = self.write_key_entity(token_value)
        self.key_table_client.create_entity(key_entity)

    def write_token_entity(self, token_value: str) -> dict:
        token = {
            "PartitionKey": self.customer,
            "RowKey": token_value,
            "Key": self.get_key(),
            "RawValue": self.encrypt_raw_value(self.raw_value),
            "KeyType": 2,
        }
        return token

    def get_token_value_from_store(self) -> str:
        try:
            key_entity = self.key_table_client.get_entity(
                partition_key=self.customer, row_key=self.get_key()
            )
            token_value = key_entity["TokenValue"]
        except HttpResponseError:
            token_value = None
        return token_value
