# UpdateInput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**schedule** | **str** |  | [optional] 
**paused** | **bool** |  | [optional] 

## Example

```python
from payfound_sdk.models.update_input import UpdateInput

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateInput from a JSON string
update_input_instance = UpdateInput.from_json(json)
# print the JSON string representation of the object
print(UpdateInput.to_json())

# convert the object into a dict
update_input_dict = update_input_instance.to_dict()
# create an instance of UpdateInput from a dict
update_input_from_dict = UpdateInput.from_dict(update_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


