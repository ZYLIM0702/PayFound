# OnboardInput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**slug** | **str** |  | 
**category** | **str** |  | [optional] [default to 'Retail']
**address** | **str** |  | 
**latitude** | **float** |  | 
**longitude** | **float** |  | 
**timezone** | **str** |  | [optional] [default to 'UTC']

## Example

```python
from payfound_sdk.models.onboard_input import OnboardInput

# TODO update the JSON string below
json = "{}"
# create an instance of OnboardInput from a JSON string
onboard_input_instance = OnboardInput.from_json(json)
# print the JSON string representation of the object
print(OnboardInput.to_json())

# convert the object into a dict
onboard_input_dict = onboard_input_instance.to_dict()
# create an instance of OnboardInput from a dict
onboard_input_from_dict = OnboardInput.from_dict(onboard_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


