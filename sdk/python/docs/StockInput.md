# StockInput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**product_id** | **str** |  | 
**quantity** | **int** |  | 

## Example

```python
from payfound_sdk.models.stock_input import StockInput

# TODO update the JSON string below
json = "{}"
# create an instance of StockInput from a JSON string
stock_input_instance = StockInput.from_json(json)
# print the JSON string representation of the object
print(StockInput.to_json())

# convert the object into a dict
stock_input_dict = stock_input_instance.to_dict()
# create an instance of StockInput from a dict
stock_input_from_dict = StockInput.from_dict(stock_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


