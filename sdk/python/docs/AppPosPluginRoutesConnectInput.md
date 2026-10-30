# AppPosPluginRoutesConnectInput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**merchant_id** | **str** |  | 
**mode** | **str** |  | 
**name** | **str** |  | 
**base_url** | **str** |  | [optional] 
**token** | **str** |  | [optional] 
**auth_scheme** | **str** |  | [optional] [default to 'bearer']
**products_path** | **str** |  | [optional] [default to '/products']
**branches_path** | **str** |  | [optional] 
**health_path** | **str** |  | [optional] [default to '/health']
**schedule** | **str** |  | [optional] [default to 'manual']

## Example

```python
from payfound_sdk.models.app_pos_plugin_routes_connect_input import AppPosPluginRoutesConnectInput

# TODO update the JSON string below
json = "{}"
# create an instance of AppPosPluginRoutesConnectInput from a JSON string
app_pos_plugin_routes_connect_input_instance = AppPosPluginRoutesConnectInput.from_json(json)
# print the JSON string representation of the object
print(AppPosPluginRoutesConnectInput.to_json())

# convert the object into a dict
app_pos_plugin_routes_connect_input_dict = app_pos_plugin_routes_connect_input_instance.to_dict()
# create an instance of AppPosPluginRoutesConnectInput from a dict
app_pos_plugin_routes_connect_input_from_dict = AppPosPluginRoutesConnectInput.from_dict(app_pos_plugin_routes_connect_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


