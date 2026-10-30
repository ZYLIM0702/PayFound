# DeliveryInput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**provider_id** | **str** |  | 
**address** | **str** |  | 
**notes** | **str** |  | [optional] [default to '']

## Example

```python
from payfound_sdk.models.delivery_input import DeliveryInput

# TODO update the JSON string below
json = "{}"
# create an instance of DeliveryInput from a JSON string
delivery_input_instance = DeliveryInput.from_json(json)
# print the JSON string representation of the object
print(DeliveryInput.to_json())

# convert the object into a dict
delivery_input_dict = delivery_input_instance.to_dict()
# create an instance of DeliveryInput from a dict
delivery_input_from_dict = DeliveryInput.from_dict(delivery_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


