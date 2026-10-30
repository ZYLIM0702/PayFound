# StartInput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**merchant_id** | **str** |  | 
**order_id** | **str** |  | [optional] 
**body** | **str** |  | [optional] 

## Example

```python
from payfound_sdk.models.start_input import StartInput

# TODO update the JSON string below
json = "{}"
# create an instance of StartInput from a JSON string
start_input_instance = StartInput.from_json(json)
# print the JSON string representation of the object
print(StartInput.to_json())

# convert the object into a dict
start_input_dict = start_input_instance.to_dict()
# create an instance of StartInput from a dict
start_input_from_dict = StartInput.from_dict(start_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


