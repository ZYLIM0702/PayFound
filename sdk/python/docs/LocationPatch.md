# LocationPatch


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**address** | **str** |  | [optional] 
**latitude** | **float** |  | [optional] 
**longitude** | **float** |  | [optional] 
**timezone** | **str** |  | [optional] 
**hours** | **Dict[str, object]** |  | [optional] 
**special_hours** | **Dict[str, object]** |  | [optional] 
**operational_status** | **str** |  | [optional] 
**phone** | **str** |  | [optional] 
**active** | **bool** |  | [optional] 

## Example

```python
from payfound_sdk.models.location_patch import LocationPatch

# TODO update the JSON string below
json = "{}"
# create an instance of LocationPatch from a JSON string
location_patch_instance = LocationPatch.from_json(json)
# print the JSON string representation of the object
print(LocationPatch.to_json())

# convert the object into a dict
location_patch_dict = location_patch_instance.to_dict()
# create an instance of LocationPatch from a dict
location_patch_from_dict = LocationPatch.from_dict(location_patch_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


