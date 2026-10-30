# SessionInput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**vad** | **str** |  | [optional] [default to 'server']
**voice** | **str** |  | [optional] 
**forwarded_props** | **Dict[str, object]** |  | [optional] 

## Example

```python
from payfound_sdk.models.session_input import SessionInput

# TODO update the JSON string below
json = "{}"
# create an instance of SessionInput from a JSON string
session_input_instance = SessionInput.from_json(json)
# print the JSON string representation of the object
print(SessionInput.to_json())

# convert the object into a dict
session_input_dict = session_input_instance.to_dict()
# create an instance of SessionInput from a dict
session_input_from_dict = SessionInput.from_dict(session_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


