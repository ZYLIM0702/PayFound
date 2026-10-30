# LocationInput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] [default to 'Main branch']
**address** | **str** |  | 
**latitude** | **float** |  | 
**longitude** | **float** |  | 
**timezone** | **str** |  | [optional] [default to 'UTC']
**hours** | **Dict[str, object]** |  | [optional] 
**special_hours** | **Dict[str, object]** |  | [optional] 
**operational_status** | **str** |  | [optional] [default to 'auto']
**phone** | **str** |  | [optional] [default to '']
**active** | **bool** |  | [optional] [default to True]

## Example

```python
from payfound_sdk.models.location_input import LocationInput

# TODO update the JSON string below
json = "{}"
# create an instance of LocationInput from a JSON string
location_input_instance = LocationInput.from_json(json)
# print the JSON string representation of the object
print(LocationInput.to_json())

# convert the object into a dict
location_input_dict = location_input_instance.to_dict()
# create an instance of LocationInput from a dict
location_input_from_dict = LocationInput.from_dict(location_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


