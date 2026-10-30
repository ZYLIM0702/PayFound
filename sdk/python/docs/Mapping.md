# Mapping


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**source_location_id** | **str** |  | 
**location_id** | **str** |  | 

## Example

```python
from payfound_sdk.models.mapping import Mapping

# TODO update the JSON string below
json = "{}"
# create an instance of Mapping from a JSON string
mapping_instance = Mapping.from_json(json)
# print the JSON string representation of the object
print(Mapping.to_json())

# convert the object into a dict
mapping_dict = mapping_instance.to_dict()
# create an instance of Mapping from a dict
mapping_from_dict = Mapping.from_dict(mapping_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


