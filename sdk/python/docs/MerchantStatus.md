# MerchantStatus


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** |  | 

## Example

```python
from payfound_sdk.models.merchant_status import MerchantStatus

# TODO update the JSON string below
json = "{}"
# create an instance of MerchantStatus from a JSON string
merchant_status_instance = MerchantStatus.from_json(json)
# print the JSON string representation of the object
print(MerchantStatus.to_json())

# convert the object into a dict
merchant_status_dict = merchant_status_instance.to_dict()
# create an instance of MerchantStatus from a dict
merchant_status_from_dict = MerchantStatus.from_dict(merchant_status_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


