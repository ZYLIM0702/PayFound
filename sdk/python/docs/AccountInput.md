# AccountInput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**client_id** | **str** |  | 
**client_secret** | **str** |  | [optional] 
**receiving_email** | **str** |  | 
**paypal_merchant_id** | **str** |  | [optional] 

## Example

```python
from payfound_sdk.models.account_input import AccountInput

# TODO update the JSON string below
json = "{}"
# create an instance of AccountInput from a JSON string
account_input_instance = AccountInput.from_json(json)
# print the JSON string representation of the object
print(AccountInput.to_json())

# convert the object into a dict
account_input_dict = account_input_instance.to_dict()
# create an instance of AccountInput from a dict
account_input_from_dict = AccountInput.from_dict(account_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


