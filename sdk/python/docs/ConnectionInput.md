# ConnectionInput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**online** | **bool** |  | 

## Example

```python
from payfound_sdk.models.connection_input import ConnectionInput

# TODO update the JSON string below
json = "{}"
# create an instance of ConnectionInput from a JSON string
connection_input_instance = ConnectionInput.from_json(json)
# print the JSON string representation of the object
print(ConnectionInput.to_json())

# convert the object into a dict
connection_input_dict = connection_input_instance.to_dict()
# create an instance of ConnectionInput from a dict
connection_input_from_dict = ConnectionInput.from_dict(connection_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


