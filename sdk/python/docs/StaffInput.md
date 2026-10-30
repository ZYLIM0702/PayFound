# StaffInput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**subject** | **str** |  | [optional] 
**email** | **str** |  | [optional] 
**role** | **str** |  | [optional] [default to 'staff']

## Example

```python
from payfound_sdk.models.staff_input import StaffInput

# TODO update the JSON string below
json = "{}"
# create an instance of StaffInput from a JSON string
staff_input_instance = StaffInput.from_json(json)
# print the JSON string representation of the object
print(StaffInput.to_json())

# convert the object into a dict
staff_input_dict = staff_input_instance.to_dict()
# create an instance of StaffInput from a dict
staff_input_from_dict = StaffInput.from_dict(staff_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


