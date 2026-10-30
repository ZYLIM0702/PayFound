# ProfileInput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**display_name** | **str** |  | [optional] [default to '']
**addresses** | [**List[AddressInput]**](AddressInput.md) |  | [optional] 
**notifications** | **Dict[str, bool]** |  | [optional] 

## Example

```python
from payfound_sdk.models.profile_input import ProfileInput

# TODO update the JSON string below
json = "{}"
# create an instance of ProfileInput from a JSON string
profile_input_instance = ProfileInput.from_json(json)
# print the JSON string representation of the object
print(ProfileInput.to_json())

# convert the object into a dict
profile_input_dict = profile_input_instance.to_dict()
# create an instance of ProfileInput from a dict
profile_input_from_dict = ProfileInput.from_dict(profile_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


