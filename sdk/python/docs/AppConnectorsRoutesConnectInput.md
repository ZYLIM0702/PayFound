# AppConnectorsRoutesConnectInput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**merchant_id** | **str** |  | 
**provider** | **str** |  | 
**store_url** | **str** |  | [optional] 
**shop_domain** | **str** |  | [optional] 
**consumer_key** | **str** |  | [optional] 
**consumer_secret** | **str** |  | [optional] 

## Example

```python
from payfound_sdk.models.app_connectors_routes_connect_input import AppConnectorsRoutesConnectInput

# TODO update the JSON string below
json = "{}"
# create an instance of AppConnectorsRoutesConnectInput from a JSON string
app_connectors_routes_connect_input_instance = AppConnectorsRoutesConnectInput.from_json(json)
# print the JSON string representation of the object
print(AppConnectorsRoutesConnectInput.to_json())

# convert the object into a dict
app_connectors_routes_connect_input_dict = app_connectors_routes_connect_input_instance.to_dict()
# create an instance of AppConnectorsRoutesConnectInput from a dict
app_connectors_routes_connect_input_from_dict = AppConnectorsRoutesConnectInput.from_dict(app_connectors_routes_connect_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


