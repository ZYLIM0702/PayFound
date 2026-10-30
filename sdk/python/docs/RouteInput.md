# RouteInput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**product_id** | **str** |  | 
**origin_latitude** | **float** |  | 
**origin_longitude** | **float** |  | 

## Example

```python
from payfound_sdk.models.route_input import RouteInput

# TODO update the JSON string below
json = "{}"
# create an instance of RouteInput from a JSON string
route_input_instance = RouteInput.from_json(json)
# print the JSON string representation of the object
print(RouteInput.to_json())

# convert the object into a dict
route_input_dict = route_input_instance.to_dict()
# create an instance of RouteInput from a dict
route_input_from_dict = RouteInput.from_dict(route_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


