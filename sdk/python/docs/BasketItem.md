# BasketItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**product_id** | **str** |  | 
**quantity** | **int** |  | [optional] [default to 1]

## Example

```python
from payfound_sdk.models.basket_item import BasketItem

# TODO update the JSON string below
json = "{}"
# create an instance of BasketItem from a JSON string
basket_item_instance = BasketItem.from_json(json)
# print the JSON string representation of the object
print(BasketItem.to_json())

# convert the object into a dict
basket_item_dict = basket_item_instance.to_dict()
# create an instance of BasketItem from a dict
basket_item_from_dict = BasketItem.from_dict(basket_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


