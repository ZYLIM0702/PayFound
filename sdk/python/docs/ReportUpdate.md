# ReportUpdate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**state** | **Dict[str, object]** |  | [optional] 
**version** | **int** |  | [optional] 

## Example

```python
from payfound_sdk.models.report_update import ReportUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of ReportUpdate from a JSON string
report_update_instance = ReportUpdate.from_json(json)
# print the JSON string representation of the object
print(ReportUpdate.to_json())

# convert the object into a dict
report_update_dict = report_update_instance.to_dict()
# create an instance of ReportUpdate from a dict
report_update_from_dict = ReportUpdate.from_dict(report_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


