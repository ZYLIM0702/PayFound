# ConsentInput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**granted** | **bool** |  | 

## Example

```python
from payfound_sdk.models.consent_input import ConsentInput

# TODO update the JSON string below
json = "{}"
# create an instance of ConsentInput from a JSON string
consent_input_instance = ConsentInput.from_json(json)
# print the JSON string representation of the object
print(ConsentInput.to_json())

# convert the object into a dict
consent_input_dict = consent_input_instance.to_dict()
# create an instance of ConsentInput from a dict
consent_input_from_dict = ConsentInput.from_dict(consent_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


