# payfound_sdk.MerchantApi

All URIs are relative to *http://127.0.0.1:8000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**accept_staff_api_merchant_staff_invitations_invitation_id_accept_post**](MerchantApi.md#accept_staff_api_merchant_staff_invitations_invitation_id_accept_post) | **POST** /api/merchant/staff/invitations/{invitation_id}/accept | Accept Staff
[**connect_api_merchant_connections_post**](MerchantApi.md#connect_api_merchant_connections_post) | **POST** /api/merchant/connections | Connect
[**connections_api_merchant_connections_get**](MerchantApi.md#connections_api_merchant_connections_get) | **GET** /api/merchant/connections | Connections
[**create_location_api_merchant_locations_post**](MerchantApi.md#create_location_api_merchant_locations_post) | **POST** /api/merchant/locations | Create Location
[**create_pickup_slot_api_merchant_pickup_slots_post**](MerchantApi.md#create_pickup_slot_api_merchant_pickup_slots_post) | **POST** /api/merchant/pickup-slots | Create Pickup Slot
[**create_product_api_merchant_products_post**](MerchantApi.md#create_product_api_merchant_products_post) | **POST** /api/merchant/products | Create Product
[**create_report_api_merchant_reports_post**](MerchantApi.md#create_report_api_merchant_reports_post) | **POST** /api/merchant/reports | Create Report
[**dashboard_api_merchant_dashboard_get**](MerchantApi.md#dashboard_api_merchant_dashboard_get) | **GET** /api/merchant/dashboard | Dashboard
[**delete_report_api_merchant_reports_report_id_delete**](MerchantApi.md#delete_report_api_merchant_reports_report_id_delete) | **DELETE** /api/merchant/reports/{report_id} | Delete Report
[**disconnect_api_merchant_connections_connection_id_delete**](MerchantApi.md#disconnect_api_merchant_connections_connection_id_delete) | **DELETE** /api/merchant/connections/{connection_id} | Disconnect
[**edit_stock_api_merchant_products_product_id_stock_patch**](MerchantApi.md#edit_stock_api_merchant_products_product_id_stock_patch) | **PATCH** /api/merchant/products/{product_id}/stock | Edit Stock
[**edit_store_status_api_merchant_status_patch**](MerchantApi.md#edit_store_status_api_merchant_status_patch) | **PATCH** /api/merchant/status | Edit Store Status
[**get_consent_api_merchant_ai_consent_get**](MerchantApi.md#get_consent_api_merchant_ai_consent_get) | **GET** /api/merchant/ai-consent | Get Consent
[**invite_staff_api_merchant_staff_post**](MerchantApi.md#invite_staff_api_merchant_staff_post) | **POST** /api/merchant/staff | Invite Staff
[**list_reports_api_merchant_reports_get**](MerchantApi.md#list_reports_api_merchant_reports_get) | **GET** /api/merchant/reports | List Reports
[**list_staff_api_merchant_staff_get**](MerchantApi.md#list_staff_api_merchant_staff_get) | **GET** /api/merchant/staff | List Staff
[**merchant_locations_api_merchant_locations_get**](MerchantApi.md#merchant_locations_api_merchant_locations_get) | **GET** /api/merchant/locations | Merchant Locations
[**merchant_profile_api_merchant_profile_get**](MerchantApi.md#merchant_profile_api_merchant_profile_get) | **GET** /api/merchant/profile | Merchant Profile
[**onboard_api_merchant_onboard_post**](MerchantApi.md#onboard_api_merchant_onboard_post) | **POST** /api/merchant/onboard | Onboard
[**patch_location_api_merchant_locations_location_id_patch**](MerchantApi.md#patch_location_api_merchant_locations_location_id_patch) | **PATCH** /api/merchant/locations/{location_id} | Patch Location
[**patch_profile_api_merchant_profile_patch**](MerchantApi.md#patch_profile_api_merchant_profile_patch) | **PATCH** /api/merchant/profile | Patch Profile
[**pickup_calendar_api_merchant_pickup_slots_get**](MerchantApi.md#pickup_calendar_api_merchant_pickup_slots_get) | **GET** /api/merchant/pickup-slots | Pickup Calendar
[**publish_api_merchant_connections_connection_id_publish_post**](MerchantApi.md#publish_api_merchant_connections_connection_id_publish_post) | **POST** /api/merchant/connections/{connection_id}/publish | Publish
[**reauthorize_api_merchant_connections_connection_id_authorize_post**](MerchantApi.md#reauthorize_api_merchant_connections_connection_id_authorize_post) | **POST** /api/merchant/connections/{connection_id}/authorize | Reauthorize
[**register_hooks_api_merchant_connections_connection_id_webhooks_post**](MerchantApi.md#register_hooks_api_merchant_connections_connection_id_webhooks_post) | **POST** /api/merchant/connections/{connection_id}/webhooks | Register Hooks
[**revoke_staff_api_merchant_staff_membership_id_delete**](MerchantApi.md#revoke_staff_api_merchant_staff_membership_id_delete) | **DELETE** /api/merchant/staff/{membership_id} | Revoke Staff
[**runs_api_merchant_connections_connection_id_runs_get**](MerchantApi.md#runs_api_merchant_connections_connection_id_runs_get) | **GET** /api/merchant/connections/{connection_id}/runs | Runs
[**set_consent_api_merchant_ai_consent_post**](MerchantApi.md#set_consent_api_merchant_ai_consent_post) | **POST** /api/merchant/ai-consent | Set Consent
[**source_locations_api_merchant_connections_connection_id_locations_get**](MerchantApi.md#source_locations_api_merchant_connections_connection_id_locations_get) | **GET** /api/merchant/connections/{connection_id}/locations | Source Locations
[**sync_api_merchant_connections_connection_id_sync_post**](MerchantApi.md#sync_api_merchant_connections_connection_id_sync_post) | **POST** /api/merchant/connections/{connection_id}/sync | Sync
[**update_report_api_merchant_reports_report_id_put**](MerchantApi.md#update_report_api_merchant_reports_report_id_put) | **PUT** /api/merchant/reports/{report_id} | Update Report


# **accept_staff_api_merchant_staff_invitations_invitation_id_accept_post**
> object accept_staff_api_merchant_staff_invitations_invitation_id_accept_post(invitation_id, authorization=authorization, x_demo_role=x_demo_role)

Accept Staff

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
    api_instance = payfound_sdk.MerchantApi(api_client)
    invitation_id = 'invitation_id_example' # str | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Accept Staff
        api_response = api_instance.accept_staff_api_merchant_staff_invitations_invitation_id_accept_post(invitation_id, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of MerchantApi->accept_staff_api_merchant_staff_invitations_invitation_id_accept_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MerchantApi->accept_staff_api_merchant_staff_invitations_invitation_id_accept_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **invitation_id** | **str**|  | 
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

# **connect_api_merchant_connections_post**
> object connect_api_merchant_connections_post(app_connectors_routes_connect_input, authorization=authorization, x_demo_role=x_demo_role)

Connect

### Example

* Api Key Authentication (demoRole):
* Bearer Authentication (bearerAuth):

```python
import payfound_sdk
from payfound_sdk.models.app_connectors_routes_connect_input import AppConnectorsRoutesConnectInput
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
    api_instance = payfound_sdk.MerchantApi(api_client)
    app_connectors_routes_connect_input = payfound_sdk.AppConnectorsRoutesConnectInput() # AppConnectorsRoutesConnectInput | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Connect
        api_response = api_instance.connect_api_merchant_connections_post(app_connectors_routes_connect_input, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of MerchantApi->connect_api_merchant_connections_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MerchantApi->connect_api_merchant_connections_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **app_connectors_routes_connect_input** | [**AppConnectorsRoutesConnectInput**](AppConnectorsRoutesConnectInput.md)|  | 
 **authorization** | **str**|  | [optional] 
 **x_demo_role** | **str**|  | [optional] 

### Return type

**object**

### Authorization

[demoRole](../README.md#demoRole), [bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **connections_api_merchant_connections_get**
> object connections_api_merchant_connections_get(merchant_id, authorization=authorization, x_demo_role=x_demo_role)

Connections

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
    api_instance = payfound_sdk.MerchantApi(api_client)
    merchant_id = 'merchant_id_example' # str | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Connections
        api_response = api_instance.connections_api_merchant_connections_get(merchant_id, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of MerchantApi->connections_api_merchant_connections_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MerchantApi->connections_api_merchant_connections_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **merchant_id** | **str**|  | 
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

# **create_location_api_merchant_locations_post**
> object create_location_api_merchant_locations_post(location_input, merchant_id=merchant_id, authorization=authorization, x_demo_role=x_demo_role)

Create Location

### Example

* Api Key Authentication (demoRole):
* Bearer Authentication (bearerAuth):

```python
import payfound_sdk
from payfound_sdk.models.location_input import LocationInput
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
    api_instance = payfound_sdk.MerchantApi(api_client)
    location_input = payfound_sdk.LocationInput() # LocationInput | 
    merchant_id = 'merchant_id_example' # str |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Create Location
        api_response = api_instance.create_location_api_merchant_locations_post(location_input, merchant_id=merchant_id, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of MerchantApi->create_location_api_merchant_locations_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MerchantApi->create_location_api_merchant_locations_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **location_input** | [**LocationInput**](LocationInput.md)|  | 
 **merchant_id** | **str**|  | [optional] 
 **authorization** | **str**|  | [optional] 
 **x_demo_role** | **str**|  | [optional] 

### Return type

**object**

### Authorization

[demoRole](../README.md#demoRole), [bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_pickup_slot_api_merchant_pickup_slots_post**
> object create_pickup_slot_api_merchant_pickup_slots_post(slot_input, authorization=authorization, x_demo_role=x_demo_role)

Create Pickup Slot

### Example

* Api Key Authentication (demoRole):
* Bearer Authentication (bearerAuth):

```python
import payfound_sdk
from payfound_sdk.models.slot_input import SlotInput
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
    api_instance = payfound_sdk.MerchantApi(api_client)
    slot_input = payfound_sdk.SlotInput() # SlotInput | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Create Pickup Slot
        api_response = api_instance.create_pickup_slot_api_merchant_pickup_slots_post(slot_input, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of MerchantApi->create_pickup_slot_api_merchant_pickup_slots_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MerchantApi->create_pickup_slot_api_merchant_pickup_slots_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **slot_input** | [**SlotInput**](SlotInput.md)|  | 
 **authorization** | **str**|  | [optional] 
 **x_demo_role** | **str**|  | [optional] 

### Return type

**object**

### Authorization

[demoRole](../README.md#demoRole), [bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_product_api_merchant_products_post**
> object create_product_api_merchant_products_post(merchant_id, product_input, authorization=authorization, x_demo_role=x_demo_role)

Create Product

### Example

* Api Key Authentication (demoRole):
* Bearer Authentication (bearerAuth):

```python
import payfound_sdk
from payfound_sdk.models.product_input import ProductInput
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
    api_instance = payfound_sdk.MerchantApi(api_client)
    merchant_id = 'merchant_id_example' # str | 
    product_input = payfound_sdk.ProductInput() # ProductInput | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Create Product
        api_response = api_instance.create_product_api_merchant_products_post(merchant_id, product_input, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of MerchantApi->create_product_api_merchant_products_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MerchantApi->create_product_api_merchant_products_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **merchant_id** | **str**|  | 
 **product_input** | [**ProductInput**](ProductInput.md)|  | 
 **authorization** | **str**|  | [optional] 
 **x_demo_role** | **str**|  | [optional] 

### Return type

**object**

### Authorization

[demoRole](../README.md#demoRole), [bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_report_api_merchant_reports_post**
> object create_report_api_merchant_reports_post(report_create, authorization=authorization, x_demo_role=x_demo_role)

Create Report

### Example

* Api Key Authentication (demoRole):
* Bearer Authentication (bearerAuth):

```python
import payfound_sdk
from payfound_sdk.models.report_create import ReportCreate
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
    api_instance = payfound_sdk.MerchantApi(api_client)
    report_create = payfound_sdk.ReportCreate() # ReportCreate | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Create Report
        api_response = api_instance.create_report_api_merchant_reports_post(report_create, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of MerchantApi->create_report_api_merchant_reports_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MerchantApi->create_report_api_merchant_reports_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **report_create** | [**ReportCreate**](ReportCreate.md)|  | 
 **authorization** | **str**|  | [optional] 
 **x_demo_role** | **str**|  | [optional] 

### Return type

**object**

### Authorization

[demoRole](../README.md#demoRole), [bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **dashboard_api_merchant_dashboard_get**
> object dashboard_api_merchant_dashboard_get(merchant_id=merchant_id, authorization=authorization, x_demo_role=x_demo_role)

Dashboard

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
    api_instance = payfound_sdk.MerchantApi(api_client)
    merchant_id = 'merchant_id_example' # str |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Dashboard
        api_response = api_instance.dashboard_api_merchant_dashboard_get(merchant_id=merchant_id, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of MerchantApi->dashboard_api_merchant_dashboard_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MerchantApi->dashboard_api_merchant_dashboard_get: %s\n" % e)
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

# **delete_report_api_merchant_reports_report_id_delete**
> delete_report_api_merchant_reports_report_id_delete(report_id, version=version, authorization=authorization, x_demo_role=x_demo_role)

Delete Report

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
    api_instance = payfound_sdk.MerchantApi(api_client)
    report_id = 'report_id_example' # str | 
    version = 56 # int |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Delete Report
        api_instance.delete_report_api_merchant_reports_report_id_delete(report_id, version=version, authorization=authorization, x_demo_role=x_demo_role)
    except Exception as e:
        print("Exception when calling MerchantApi->delete_report_api_merchant_reports_report_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **report_id** | **str**|  | 
 **version** | **int**|  | [optional] 
 **authorization** | **str**|  | [optional] 
 **x_demo_role** | **str**|  | [optional] 

### Return type

void (empty response body)

### Authorization

[demoRole](../README.md#demoRole), [bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **disconnect_api_merchant_connections_connection_id_delete**
> object disconnect_api_merchant_connections_connection_id_delete(connection_id, authorization=authorization, x_demo_role=x_demo_role)

Disconnect

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
    api_instance = payfound_sdk.MerchantApi(api_client)
    connection_id = 'connection_id_example' # str | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Disconnect
        api_response = api_instance.disconnect_api_merchant_connections_connection_id_delete(connection_id, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of MerchantApi->disconnect_api_merchant_connections_connection_id_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MerchantApi->disconnect_api_merchant_connections_connection_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **connection_id** | **str**|  | 
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

# **edit_stock_api_merchant_products_product_id_stock_patch**
> object edit_stock_api_merchant_products_product_id_stock_patch(product_id, stock_update, authorization=authorization, x_demo_role=x_demo_role)

Edit Stock

### Example

* Api Key Authentication (demoRole):
* Bearer Authentication (bearerAuth):

```python
import payfound_sdk
from payfound_sdk.models.stock_update import StockUpdate
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
    api_instance = payfound_sdk.MerchantApi(api_client)
    product_id = 'product_id_example' # str | 
    stock_update = payfound_sdk.StockUpdate() # StockUpdate | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Edit Stock
        api_response = api_instance.edit_stock_api_merchant_products_product_id_stock_patch(product_id, stock_update, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of MerchantApi->edit_stock_api_merchant_products_product_id_stock_patch:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MerchantApi->edit_stock_api_merchant_products_product_id_stock_patch: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **product_id** | **str**|  | 
 **stock_update** | [**StockUpdate**](StockUpdate.md)|  | 
 **authorization** | **str**|  | [optional] 
 **x_demo_role** | **str**|  | [optional] 

### Return type

**object**

### Authorization

[demoRole](../README.md#demoRole), [bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **edit_store_status_api_merchant_status_patch**
> object edit_store_status_api_merchant_status_patch(merchant_status, merchant_id=merchant_id, authorization=authorization, x_demo_role=x_demo_role)

Edit Store Status

### Example

* Api Key Authentication (demoRole):
* Bearer Authentication (bearerAuth):

```python
import payfound_sdk
from payfound_sdk.models.merchant_status import MerchantStatus
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
    api_instance = payfound_sdk.MerchantApi(api_client)
    merchant_status = payfound_sdk.MerchantStatus() # MerchantStatus | 
    merchant_id = 'merchant_id_example' # str |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Edit Store Status
        api_response = api_instance.edit_store_status_api_merchant_status_patch(merchant_status, merchant_id=merchant_id, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of MerchantApi->edit_store_status_api_merchant_status_patch:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MerchantApi->edit_store_status_api_merchant_status_patch: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **merchant_status** | [**MerchantStatus**](MerchantStatus.md)|  | 
 **merchant_id** | **str**|  | [optional] 
 **authorization** | **str**|  | [optional] 
 **x_demo_role** | **str**|  | [optional] 

### Return type

**object**

### Authorization

[demoRole](../README.md#demoRole), [bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_consent_api_merchant_ai_consent_get**
> object get_consent_api_merchant_ai_consent_get(merchant_id=merchant_id, authorization=authorization, x_demo_role=x_demo_role)

Get Consent

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
    api_instance = payfound_sdk.MerchantApi(api_client)
    merchant_id = 'merchant_id_example' # str |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Get Consent
        api_response = api_instance.get_consent_api_merchant_ai_consent_get(merchant_id=merchant_id, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of MerchantApi->get_consent_api_merchant_ai_consent_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MerchantApi->get_consent_api_merchant_ai_consent_get: %s\n" % e)
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

# **invite_staff_api_merchant_staff_post**
> object invite_staff_api_merchant_staff_post(staff_input, merchant_id=merchant_id, authorization=authorization, x_demo_role=x_demo_role)

Invite Staff

### Example

* Api Key Authentication (demoRole):
* Bearer Authentication (bearerAuth):

```python
import payfound_sdk
from payfound_sdk.models.staff_input import StaffInput
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
    api_instance = payfound_sdk.MerchantApi(api_client)
    staff_input = payfound_sdk.StaffInput() # StaffInput | 
    merchant_id = 'merchant_id_example' # str |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Invite Staff
        api_response = api_instance.invite_staff_api_merchant_staff_post(staff_input, merchant_id=merchant_id, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of MerchantApi->invite_staff_api_merchant_staff_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MerchantApi->invite_staff_api_merchant_staff_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **staff_input** | [**StaffInput**](StaffInput.md)|  | 
 **merchant_id** | **str**|  | [optional] 
 **authorization** | **str**|  | [optional] 
 **x_demo_role** | **str**|  | [optional] 

### Return type

**object**

### Authorization

[demoRole](../README.md#demoRole), [bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_reports_api_merchant_reports_get**
> object list_reports_api_merchant_reports_get(merchant_id=merchant_id, authorization=authorization, x_demo_role=x_demo_role)

List Reports

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
    api_instance = payfound_sdk.MerchantApi(api_client)
    merchant_id = 'merchant_id_example' # str |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # List Reports
        api_response = api_instance.list_reports_api_merchant_reports_get(merchant_id=merchant_id, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of MerchantApi->list_reports_api_merchant_reports_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MerchantApi->list_reports_api_merchant_reports_get: %s\n" % e)
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

# **list_staff_api_merchant_staff_get**
> object list_staff_api_merchant_staff_get(merchant_id=merchant_id, authorization=authorization, x_demo_role=x_demo_role)

List Staff

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
    api_instance = payfound_sdk.MerchantApi(api_client)
    merchant_id = 'merchant_id_example' # str |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # List Staff
        api_response = api_instance.list_staff_api_merchant_staff_get(merchant_id=merchant_id, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of MerchantApi->list_staff_api_merchant_staff_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MerchantApi->list_staff_api_merchant_staff_get: %s\n" % e)
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

# **merchant_locations_api_merchant_locations_get**
> object merchant_locations_api_merchant_locations_get(merchant_id=merchant_id, authorization=authorization, x_demo_role=x_demo_role)

Merchant Locations

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
    api_instance = payfound_sdk.MerchantApi(api_client)
    merchant_id = 'merchant_id_example' # str |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Merchant Locations
        api_response = api_instance.merchant_locations_api_merchant_locations_get(merchant_id=merchant_id, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of MerchantApi->merchant_locations_api_merchant_locations_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MerchantApi->merchant_locations_api_merchant_locations_get: %s\n" % e)
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

# **merchant_profile_api_merchant_profile_get**
> object merchant_profile_api_merchant_profile_get(merchant_id=merchant_id, authorization=authorization, x_demo_role=x_demo_role)

Merchant Profile

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
    api_instance = payfound_sdk.MerchantApi(api_client)
    merchant_id = 'merchant_id_example' # str |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Merchant Profile
        api_response = api_instance.merchant_profile_api_merchant_profile_get(merchant_id=merchant_id, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of MerchantApi->merchant_profile_api_merchant_profile_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MerchantApi->merchant_profile_api_merchant_profile_get: %s\n" % e)
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

# **onboard_api_merchant_onboard_post**
> object onboard_api_merchant_onboard_post(onboard_input, authorization=authorization, x_demo_role=x_demo_role)

Onboard

### Example

* Api Key Authentication (demoRole):
* Bearer Authentication (bearerAuth):

```python
import payfound_sdk
from payfound_sdk.models.onboard_input import OnboardInput
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
    api_instance = payfound_sdk.MerchantApi(api_client)
    onboard_input = payfound_sdk.OnboardInput() # OnboardInput | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Onboard
        api_response = api_instance.onboard_api_merchant_onboard_post(onboard_input, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of MerchantApi->onboard_api_merchant_onboard_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MerchantApi->onboard_api_merchant_onboard_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **onboard_input** | [**OnboardInput**](OnboardInput.md)|  | 
 **authorization** | **str**|  | [optional] 
 **x_demo_role** | **str**|  | [optional] 

### Return type

**object**

### Authorization

[demoRole](../README.md#demoRole), [bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **patch_location_api_merchant_locations_location_id_patch**
> object patch_location_api_merchant_locations_location_id_patch(location_id, location_patch, authorization=authorization, x_demo_role=x_demo_role)

Patch Location

### Example

* Api Key Authentication (demoRole):
* Bearer Authentication (bearerAuth):

```python
import payfound_sdk
from payfound_sdk.models.location_patch import LocationPatch
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
    api_instance = payfound_sdk.MerchantApi(api_client)
    location_id = 'location_id_example' # str | 
    location_patch = payfound_sdk.LocationPatch() # LocationPatch | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Patch Location
        api_response = api_instance.patch_location_api_merchant_locations_location_id_patch(location_id, location_patch, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of MerchantApi->patch_location_api_merchant_locations_location_id_patch:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MerchantApi->patch_location_api_merchant_locations_location_id_patch: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **location_id** | **str**|  | 
 **location_patch** | [**LocationPatch**](LocationPatch.md)|  | 
 **authorization** | **str**|  | [optional] 
 **x_demo_role** | **str**|  | [optional] 

### Return type

**object**

### Authorization

[demoRole](../README.md#demoRole), [bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **patch_profile_api_merchant_profile_patch**
> object patch_profile_api_merchant_profile_patch(profile_patch, merchant_id=merchant_id, authorization=authorization, x_demo_role=x_demo_role)

Patch Profile

### Example

* Api Key Authentication (demoRole):
* Bearer Authentication (bearerAuth):

```python
import payfound_sdk
from payfound_sdk.models.profile_patch import ProfilePatch
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
    api_instance = payfound_sdk.MerchantApi(api_client)
    profile_patch = payfound_sdk.ProfilePatch() # ProfilePatch | 
    merchant_id = 'merchant_id_example' # str |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Patch Profile
        api_response = api_instance.patch_profile_api_merchant_profile_patch(profile_patch, merchant_id=merchant_id, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of MerchantApi->patch_profile_api_merchant_profile_patch:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MerchantApi->patch_profile_api_merchant_profile_patch: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **profile_patch** | [**ProfilePatch**](ProfilePatch.md)|  | 
 **merchant_id** | **str**|  | [optional] 
 **authorization** | **str**|  | [optional] 
 **x_demo_role** | **str**|  | [optional] 

### Return type

**object**

### Authorization

[demoRole](../README.md#demoRole), [bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **pickup_calendar_api_merchant_pickup_slots_get**
> object pickup_calendar_api_merchant_pickup_slots_get(start_at, end_at, merchant_id=merchant_id, authorization=authorization, x_demo_role=x_demo_role)

Pickup Calendar

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
    api_instance = payfound_sdk.MerchantApi(api_client)
    start_at = '2013-10-20T19:20:30+01:00' # datetime | 
    end_at = '2013-10-20T19:20:30+01:00' # datetime | 
    merchant_id = 'merchant_id_example' # str |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Pickup Calendar
        api_response = api_instance.pickup_calendar_api_merchant_pickup_slots_get(start_at, end_at, merchant_id=merchant_id, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of MerchantApi->pickup_calendar_api_merchant_pickup_slots_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MerchantApi->pickup_calendar_api_merchant_pickup_slots_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **start_at** | **datetime**|  | 
 **end_at** | **datetime**|  | 
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

# **publish_api_merchant_connections_connection_id_publish_post**
> object publish_api_merchant_connections_connection_id_publish_post(connection_id, publish_input, authorization=authorization, x_demo_role=x_demo_role)

Publish

### Example

* Api Key Authentication (demoRole):
* Bearer Authentication (bearerAuth):

```python
import payfound_sdk
from payfound_sdk.models.publish_input import PublishInput
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
    api_instance = payfound_sdk.MerchantApi(api_client)
    connection_id = 'connection_id_example' # str | 
    publish_input = payfound_sdk.PublishInput() # PublishInput | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Publish
        api_response = api_instance.publish_api_merchant_connections_connection_id_publish_post(connection_id, publish_input, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of MerchantApi->publish_api_merchant_connections_connection_id_publish_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MerchantApi->publish_api_merchant_connections_connection_id_publish_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **connection_id** | **str**|  | 
 **publish_input** | [**PublishInput**](PublishInput.md)|  | 
 **authorization** | **str**|  | [optional] 
 **x_demo_role** | **str**|  | [optional] 

### Return type

**object**

### Authorization

[demoRole](../README.md#demoRole), [bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **reauthorize_api_merchant_connections_connection_id_authorize_post**
> object reauthorize_api_merchant_connections_connection_id_authorize_post(connection_id, authorization=authorization, x_demo_role=x_demo_role)

Reauthorize

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
    api_instance = payfound_sdk.MerchantApi(api_client)
    connection_id = 'connection_id_example' # str | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Reauthorize
        api_response = api_instance.reauthorize_api_merchant_connections_connection_id_authorize_post(connection_id, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of MerchantApi->reauthorize_api_merchant_connections_connection_id_authorize_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MerchantApi->reauthorize_api_merchant_connections_connection_id_authorize_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **connection_id** | **str**|  | 
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

# **register_hooks_api_merchant_connections_connection_id_webhooks_post**
> object register_hooks_api_merchant_connections_connection_id_webhooks_post(connection_id, authorization=authorization, x_demo_role=x_demo_role)

Register Hooks

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
    api_instance = payfound_sdk.MerchantApi(api_client)
    connection_id = 'connection_id_example' # str | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Register Hooks
        api_response = api_instance.register_hooks_api_merchant_connections_connection_id_webhooks_post(connection_id, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of MerchantApi->register_hooks_api_merchant_connections_connection_id_webhooks_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MerchantApi->register_hooks_api_merchant_connections_connection_id_webhooks_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **connection_id** | **str**|  | 
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

# **revoke_staff_api_merchant_staff_membership_id_delete**
> object revoke_staff_api_merchant_staff_membership_id_delete(membership_id, authorization=authorization, x_demo_role=x_demo_role)

Revoke Staff

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
    api_instance = payfound_sdk.MerchantApi(api_client)
    membership_id = 'membership_id_example' # str | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Revoke Staff
        api_response = api_instance.revoke_staff_api_merchant_staff_membership_id_delete(membership_id, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of MerchantApi->revoke_staff_api_merchant_staff_membership_id_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MerchantApi->revoke_staff_api_merchant_staff_membership_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **membership_id** | **str**|  | 
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

# **runs_api_merchant_connections_connection_id_runs_get**
> object runs_api_merchant_connections_connection_id_runs_get(connection_id, authorization=authorization, x_demo_role=x_demo_role)

Runs

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
    api_instance = payfound_sdk.MerchantApi(api_client)
    connection_id = 'connection_id_example' # str | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Runs
        api_response = api_instance.runs_api_merchant_connections_connection_id_runs_get(connection_id, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of MerchantApi->runs_api_merchant_connections_connection_id_runs_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MerchantApi->runs_api_merchant_connections_connection_id_runs_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **connection_id** | **str**|  | 
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

# **set_consent_api_merchant_ai_consent_post**
> object set_consent_api_merchant_ai_consent_post(merchant_id, consent_input, authorization=authorization, x_demo_role=x_demo_role)

Set Consent

### Example

* Api Key Authentication (demoRole):
* Bearer Authentication (bearerAuth):

```python
import payfound_sdk
from payfound_sdk.models.consent_input import ConsentInput
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
    api_instance = payfound_sdk.MerchantApi(api_client)
    merchant_id = 'merchant_id_example' # str | 
    consent_input = payfound_sdk.ConsentInput() # ConsentInput | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Set Consent
        api_response = api_instance.set_consent_api_merchant_ai_consent_post(merchant_id, consent_input, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of MerchantApi->set_consent_api_merchant_ai_consent_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MerchantApi->set_consent_api_merchant_ai_consent_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **merchant_id** | **str**|  | 
 **consent_input** | [**ConsentInput**](ConsentInput.md)|  | 
 **authorization** | **str**|  | [optional] 
 **x_demo_role** | **str**|  | [optional] 

### Return type

**object**

### Authorization

[demoRole](../README.md#demoRole), [bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **source_locations_api_merchant_connections_connection_id_locations_get**
> object source_locations_api_merchant_connections_connection_id_locations_get(connection_id, authorization=authorization, x_demo_role=x_demo_role)

Source Locations

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
    api_instance = payfound_sdk.MerchantApi(api_client)
    connection_id = 'connection_id_example' # str | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Source Locations
        api_response = api_instance.source_locations_api_merchant_connections_connection_id_locations_get(connection_id, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of MerchantApi->source_locations_api_merchant_connections_connection_id_locations_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MerchantApi->source_locations_api_merchant_connections_connection_id_locations_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **connection_id** | **str**|  | 
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

# **sync_api_merchant_connections_connection_id_sync_post**
> object sync_api_merchant_connections_connection_id_sync_post(connection_id, authorization=authorization, x_demo_role=x_demo_role)

Sync

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
    api_instance = payfound_sdk.MerchantApi(api_client)
    connection_id = 'connection_id_example' # str | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Sync
        api_response = api_instance.sync_api_merchant_connections_connection_id_sync_post(connection_id, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of MerchantApi->sync_api_merchant_connections_connection_id_sync_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MerchantApi->sync_api_merchant_connections_connection_id_sync_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **connection_id** | **str**|  | 
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

# **update_report_api_merchant_reports_report_id_put**
> object update_report_api_merchant_reports_report_id_put(report_id, report_update, authorization=authorization, x_demo_role=x_demo_role)

Update Report

### Example

* Api Key Authentication (demoRole):
* Bearer Authentication (bearerAuth):

```python
import payfound_sdk
from payfound_sdk.models.report_update import ReportUpdate
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
    api_instance = payfound_sdk.MerchantApi(api_client)
    report_id = 'report_id_example' # str | 
    report_update = payfound_sdk.ReportUpdate() # ReportUpdate | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Update Report
        api_response = api_instance.update_report_api_merchant_reports_report_id_put(report_id, report_update, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of MerchantApi->update_report_api_merchant_reports_report_id_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MerchantApi->update_report_api_merchant_reports_report_id_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **report_id** | **str**|  | 
 **report_update** | [**ReportUpdate**](ReportUpdate.md)|  | 
 **authorization** | **str**|  | [optional] 
 **x_demo_role** | **str**|  | [optional] 

### Return type

**object**

### Authorization

[demoRole](../README.md#demoRole), [bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

