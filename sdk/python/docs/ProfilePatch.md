# ProfilePatch


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**category** | **str** |  | [optional] 
**address** | **str** |  | [optional] 
**phone** | **str** |  | [optional] 
**hours** | **str** |  | [optional] 
**fulfillment_minutes** | **int** |  | [optional] 

## Example

```python
from payfound_sdk.models.profile_patch import ProfilePatch

# TODO update the JSON string below
json = "{}"
# create an instance of ProfilePatch from a JSON string
profile_patch_instance = ProfilePatch.from_json(json)
# print the JSON string representation of the object
print(ProfilePatch.to_json())

# convert the object into a dict
profile_patch_dict = profile_patch_instance.to_dict()
# create an instance of ProfilePatch from a dict
profile_patch_from_dict = ProfilePatch.from_dict(profile_patch_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


