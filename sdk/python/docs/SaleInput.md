# SaleInput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items** | [**List[Line]**](Line.md) |  | 
**discount_kind** | **str** |  | [optional] [default to 'percent']
**discount_value** | **int** |  | [optional] [default to 0]
**payment_method** | **str** |  | [optional] [default to 'card']
**outcome** | **str** |  | [optional] [default to 'approved']
**idempotency_key** | **str** |  | 

## Example

```python
from payfound_sdk.models.sale_input import SaleInput

# TODO update the JSON string below
json = "{}"
# create an instance of SaleInput from a JSON string
sale_input_instance = SaleInput.from_json(json)
# print the JSON string representation of the object
print(SaleInput.to_json())

# convert the object into a dict
sale_input_dict = sale_input_instance.to_dict()
# create an instance of SaleInput from a dict
sale_input_from_dict = SaleInput.from_dict(sale_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


