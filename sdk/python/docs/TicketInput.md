# TicketInput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**topic** | **str** |  | [optional] [default to 'other']
**subject** | **str** |  | 
**message** | **str** |  | 
**order_id** | **str** |  | [optional] 

## Example

```python
from payfound_sdk.models.ticket_input import TicketInput

# TODO update the JSON string below
json = "{}"
# create an instance of TicketInput from a JSON string
ticket_input_instance = TicketInput.from_json(json)
# print the JSON string representation of the object
print(TicketInput.to_json())

# convert the object into a dict
ticket_input_dict = ticket_input_instance.to_dict()
# create an instance of TicketInput from a dict
ticket_input_from_dict = TicketInput.from_dict(ticket_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


