# ReserveInput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**product_id** | **str** |  | [optional] 
**quantity** | **int** |  | [optional] [default to 1]
**items** | [**List[BasketItem]**](BasketItem.md) |  | [optional] 
**location_id** | **str** |  | [optional] 
**idempotency_key** | **str** |  | 
**buyer_name** | **str** |  | [optional] [default to 'Local shopper']

## Example

```python
from payfound_sdk.models.reserve_input import ReserveInput

# TODO update the JSON string below
json = "{}"
# create an instance of ReserveInput from a JSON string
reserve_input_instance = ReserveInput.from_json(json)
# print the JSON string representation of the object
print(ReserveInput.to_json())

# convert the object into a dict
reserve_input_dict = reserve_input_instance.to_dict()
# create an instance of ReserveInput from a dict
reserve_input_from_dict = ReserveInput.from_dict(reserve_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


