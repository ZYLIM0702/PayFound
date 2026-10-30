# AddressInput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] [default to '']
**label** | **str** |  | [optional] [default to 'Home']
**line1** | **str** |  | 
**city** | **str** |  | [optional] [default to '']
**postal** | **str** |  | [optional] [default to '']

## Example

```python
from payfound_sdk.models.address_input import AddressInput

# TODO update the JSON string below
json = "{}"
# create an instance of AddressInput from a JSON string
address_input_instance = AddressInput.from_json(json)
# print the JSON string representation of the object
print(AddressInput.to_json())

# convert the object into a dict
address_input_dict = address_input_instance.to_dict()
# create an instance of AddressInput from a dict
address_input_from_dict = AddressInput.from_dict(address_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


