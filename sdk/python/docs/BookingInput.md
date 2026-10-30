# BookingInput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**slot_id** | **str** |  | 

## Example

```python
from payfound_sdk.models.booking_input import BookingInput

# TODO update the JSON string below
json = "{}"
# create an instance of BookingInput from a JSON string
booking_input_instance = BookingInput.from_json(json)
# print the JSON string representation of the object
print(BookingInput.to_json())

# convert the object into a dict
booking_input_dict = booking_input_instance.to_dict()
# create an instance of BookingInput from a dict
booking_input_from_dict = BookingInput.from_dict(booking_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


