# Msg


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**role** | **str** |  | 
**content** | **object** |  | [optional] 
**images** | **List[Optional[Dict[str, object]]]** |  | [optional] 

## Example

```python
from payfound_sdk.models.msg import Msg

# TODO update the JSON string below
json = "{}"
# create an instance of Msg from a JSON string
msg_instance = Msg.from_json(json)
# print the JSON string representation of the object
print(Msg.to_json())

# convert the object into a dict
msg_dict = msg_instance.to_dict()
# create an instance of Msg from a dict
msg_from_dict = Msg.from_dict(msg_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


