# PayPalLinkInput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**email** | **str** |  | 
**paypal_merchant_id** | **str** |  | [optional] 

## Example

```python
from payfound_sdk.models.pay_pal_link_input import PayPalLinkInput

# TODO update the JSON string below
json = "{}"
# create an instance of PayPalLinkInput from a JSON string
pay_pal_link_input_instance = PayPalLinkInput.from_json(json)
# print the JSON string representation of the object
print(PayPalLinkInput.to_json())

# convert the object into a dict
pay_pal_link_input_dict = pay_pal_link_input_instance.to_dict()
# create an instance of PayPalLinkInput from a dict
pay_pal_link_input_from_dict = PayPalLinkInput.from_dict(pay_pal_link_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


