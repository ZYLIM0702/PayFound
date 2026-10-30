# PublishInput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**consent** | **bool** |  | [optional] [default to False]
**mappings** | [**List[Mapping]**](Mapping.md) |  | [optional] 

## Example

```python
from payfound_sdk.models.publish_input import PublishInput

# TODO update the JSON string below
json = "{}"
# create an instance of PublishInput from a JSON string
publish_input_instance = PublishInput.from_json(json)
# print the JSON string representation of the object
print(PublishInput.to_json())

# convert the object into a dict
publish_input_dict = publish_input_instance.to_dict()
# create an instance of PublishInput from a dict
publish_input_from_dict = PublishInput.from_dict(publish_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


