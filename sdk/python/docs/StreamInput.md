# StreamInput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**thread_id** | **str** |  | [optional] 
**run_id** | **str** |  | [optional] 
**messages** | [**List[Msg]**](Msg.md) |  | [optional] 
**forwarded_props** | **Dict[str, object]** |  | [optional] 

## Example

```python
from payfound_sdk.models.stream_input import StreamInput

# TODO update the JSON string below
json = "{}"
# create an instance of StreamInput from a JSON string
stream_input_instance = StreamInput.from_json(json)
# print the JSON string representation of the object
print(StreamInput.to_json())

# convert the object into a dict
stream_input_dict = stream_input_instance.to_dict()
# create an instance of StreamInput from a dict
stream_input_from_dict = StreamInput.from_dict(stream_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


