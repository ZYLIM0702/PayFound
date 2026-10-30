# payfound_sdk.MerchantNotificationsApi

All URIs are relative to *http://127.0.0.1:8000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**list_notifications_api_merchant_notifications_get**](MerchantNotificationsApi.md#list_notifications_api_merchant_notifications_get) | **GET** /api/merchant/notifications | List Notifications
[**read_notification_api_merchant_notifications_notification_id_read_post**](MerchantNotificationsApi.md#read_notification_api_merchant_notifications_notification_id_read_post) | **POST** /api/merchant/notifications/{notification_id}/read | Read Notification


# **list_notifications_api_merchant_notifications_get**
> object list_notifications_api_merchant_notifications_get(merchant_id=merchant_id, authorization=authorization, x_demo_role=x_demo_role)

List Notifications

### Example

* Api Key Authentication (demoRole):
* Bearer Authentication (bearerAuth):

```python
import payfound_sdk
from payfound_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://127.0.0.1:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = payfound_sdk.Configuration(
    host = "http://127.0.0.1:8000"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: demoRole
configuration.api_key['demoRole'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['demoRole'] = 'Bearer'

# Configure Bearer authorization: bearerAuth
configuration = payfound_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with payfound_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = payfound_sdk.MerchantNotificationsApi(api_client)
    merchant_id = 'merchant_id_example' # str |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # List Notifications
        api_response = api_instance.list_notifications_api_merchant_notifications_get(merchant_id=merchant_id, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of MerchantNotificationsApi->list_notifications_api_merchant_notifications_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MerchantNotificationsApi->list_notifications_api_merchant_notifications_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **merchant_id** | **str**|  | [optional] 
 **authorization** | **str**|  | [optional] 
 **x_demo_role** | **str**|  | [optional] 

### Return type

**object**

### Authorization

[demoRole](../README.md#demoRole), [bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **read_notification_api_merchant_notifications_notification_id_read_post**
> object read_notification_api_merchant_notifications_notification_id_read_post(notification_id, authorization=authorization, x_demo_role=x_demo_role)

Read Notification

### Example

* Api Key Authentication (demoRole):
* Bearer Authentication (bearerAuth):

```python
import payfound_sdk
from payfound_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://127.0.0.1:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = payfound_sdk.Configuration(
    host = "http://127.0.0.1:8000"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: demoRole
configuration.api_key['demoRole'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['demoRole'] = 'Bearer'

# Configure Bearer authorization: bearerAuth
configuration = payfound_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with payfound_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = payfound_sdk.MerchantNotificationsApi(api_client)
    notification_id = 'notification_id_example' # str | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Read Notification
        api_response = api_instance.read_notification_api_merchant_notifications_notification_id_read_post(notification_id, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of MerchantNotificationsApi->read_notification_api_merchant_notifications_notification_id_read_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MerchantNotificationsApi->read_notification_api_merchant_notifications_notification_id_read_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **notification_id** | **str**|  | 
 **authorization** | **str**|  | [optional] 
 **x_demo_role** | **str**|  | [optional] 

### Return type

**object**

### Authorization

[demoRole](../README.md#demoRole), [bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

