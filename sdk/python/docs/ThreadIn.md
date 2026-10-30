# ThreadIn


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**title** | **str** |  | [optional] [default to 'New chat']
**surface** | **str** |  | [optional] 

## Example

```python
from payfound_sdk.models.thread_in import ThreadIn

# TODO update the JSON string below
json = "{}"
# create an instance of ThreadIn from a JSON string
thread_in_instance = ThreadIn.from_json(json)
# print the JSON string representation of the object
print(ThreadIn.to_json())

# convert the object into a dict
thread_in_dict = thread_in_instance.to_dict()
# create an instance of ThreadIn from a dict
thread_in_from_dict = ThreadIn.from_dict(thread_in_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


