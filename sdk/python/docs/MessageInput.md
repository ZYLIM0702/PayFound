# MessageInput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**body** | **str** |  | 

## Example

```python
from payfound_sdk.models.message_input import MessageInput

# TODO update the JSON string below
json = "{}"
# create an instance of MessageInput from a JSON string
message_input_instance = MessageInput.from_json(json)
# print the JSON string representation of the object
print(MessageInput.to_json())

# convert the object into a dict
message_input_dict = message_input_instance.to_dict()
# create an instance of MessageInput from a dict
message_input_from_dict = MessageInput.from_dict(message_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


