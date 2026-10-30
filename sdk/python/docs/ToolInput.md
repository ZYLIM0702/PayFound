# ToolInput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**arguments** | [**Arguments**](Arguments.md) |  | [optional] 
**forwarded_props** | **Dict[str, object]** |  | [optional] 

## Example

```python
from payfound_sdk.models.tool_input import ToolInput

# TODO update the JSON string below
json = "{}"
# create an instance of ToolInput from a JSON string
tool_input_instance = ToolInput.from_json(json)
# print the JSON string representation of the object
print(ToolInput.to_json())

# convert the object into a dict
tool_input_dict = tool_input_instance.to_dict()
# create an instance of ToolInput from a dict
tool_input_from_dict = ToolInput.from_dict(tool_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


