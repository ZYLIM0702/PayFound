# StockUpBody


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**days** | **int** |  | [optional] [default to 7]

## Example

```python
from payfound_sdk.models.stock_up_body import StockUpBody

# TODO update the JSON string below
json = "{}"
# create an instance of StockUpBody from a JSON string
stock_up_body_instance = StockUpBody.from_json(json)
# print the JSON string representation of the object
print(StockUpBody.to_json())

# convert the object into a dict
stock_up_body_dict = stock_up_body_instance.to_dict()
# create an instance of StockUpBody from a dict
stock_up_body_from_dict = StockUpBody.from_dict(stock_up_body_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


