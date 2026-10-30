# SubscribeBody


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**plan_id** | **str** |  | 

## Example

```python
from payfound_sdk.models.subscribe_body import SubscribeBody

# TODO update the JSON string below
json = "{}"
# create an instance of SubscribeBody from a JSON string
subscribe_body_instance = SubscribeBody.from_json(json)
# print the JSON string representation of the object
print(SubscribeBody.to_json())

# convert the object into a dict
subscribe_body_dict = subscribe_body_instance.to_dict()
# create an instance of SubscribeBody from a dict
subscribe_body_from_dict = SubscribeBody.from_dict(subscribe_body_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


