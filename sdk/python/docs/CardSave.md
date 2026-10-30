# CardSave


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**merchant_id** | **str** |  | [optional] 
**name** | **str** |  | 
**kind** | **str** |  | [optional] [default to 'full']
**days** | **int** |  | [optional] [default to 30]
**focus** | **str** |  | [optional] 

## Example

```python
from payfound_sdk.models.card_save import CardSave

# TODO update the JSON string below
json = "{}"
# create an instance of CardSave from a JSON string
card_save_instance = CardSave.from_json(json)
# print the JSON string representation of the object
print(CardSave.to_json())

# convert the object into a dict
card_save_dict = card_save_instance.to_dict()
# create an instance of CardSave from a dict
card_save_from_dict = CardSave.from_dict(card_save_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


