# ReviewInput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**order_id** | **str** |  | 
**rating** | **int** |  | 
**body** | **str** |  | [optional] [default to '']

## Example

```python
from payfound_sdk.models.review_input import ReviewInput

# TODO update the JSON string below
json = "{}"
# create an instance of ReviewInput from a JSON string
review_input_instance = ReviewInput.from_json(json)
# print the JSON string representation of the object
print(ReviewInput.to_json())

# convert the object into a dict
review_input_dict = review_input_instance.to_dict()
# create an instance of ReviewInput from a dict
review_input_from_dict = ReviewInput.from_dict(review_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


