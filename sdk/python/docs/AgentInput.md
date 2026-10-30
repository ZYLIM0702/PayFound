# AgentInput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message** | **str** |  | 
**latitude** | **float** |  | [optional] 
**longitude** | **float** |  | [optional] 
**radius_km** | **float** |  | [optional] 
**merchant_id** | **str** |  | [optional] 

## Example

```python
from payfound_sdk.models.agent_input import AgentInput

# TODO update the JSON string below
json = "{}"
# create an instance of AgentInput from a JSON string
agent_input_instance = AgentInput.from_json(json)
# print the JSON string representation of the object
print(AgentInput.to_json())

# convert the object into a dict
agent_input_dict = agent_input_instance.to_dict()
# create an instance of AgentInput from a dict
agent_input_from_dict = AgentInput.from_dict(agent_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


