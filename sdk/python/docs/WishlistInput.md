# WishlistInput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**product_id** | **str** |  | 

## Example

```python
from payfound_sdk.models.wishlist_input import WishlistInput

# TODO update the JSON string below
json = "{}"
# create an instance of WishlistInput from a JSON string
wishlist_input_instance = WishlistInput.from_json(json)
# print the JSON string representation of the object
print(WishlistInput.to_json())

# convert the object into a dict
wishlist_input_dict = wishlist_input_instance.to_dict()
# create an instance of WishlistInput from a dict
wishlist_input_from_dict = WishlistInput.from_dict(wishlist_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


