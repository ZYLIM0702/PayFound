# SlotInput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**merchant_id** | **str** |  | 
**location_id** | **str** |  | 
**start_at** | **datetime** |  | 
**end_at** | **datetime** |  | 
**capacity** | **int** |  | 

## Example

```python
from payfound_sdk.models.slot_input import SlotInput

# TODO update the JSON string below
json = "{}"
# create an instance of SlotInput from a JSON string
slot_input_instance = SlotInput.from_json(json)
# print the JSON string representation of the object
print(SlotInput.to_json())

# convert the object into a dict
slot_input_dict = slot_input_instance.to_dict()
# create an instance of SlotInput from a dict
slot_input_from_dict = SlotInput.from_dict(slot_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


