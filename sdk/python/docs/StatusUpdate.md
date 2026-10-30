# StatusUpdate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** |  | 
**proof** | **str** |  | [optional] [default to '']

## Example

```python
from payfound_sdk.models.status_update import StatusUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of StatusUpdate from a JSON string
status_update_instance = StatusUpdate.from_json(json)
# print the JSON string representation of the object
print(StatusUpdate.to_json())

# convert the object into a dict
status_update_dict = status_update_instance.to_dict()
# create an instance of StatusUpdate from a dict
status_update_from_dict = StatusUpdate.from_dict(status_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


