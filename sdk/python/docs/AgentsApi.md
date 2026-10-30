# payfound_sdk.AgentsApi

All URIs are relative to *http://127.0.0.1:8000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**agent_merchant_api_agents_merchant_post**](AgentsApi.md#agent_merchant_api_agents_merchant_post) | **POST** /api/agents/merchant | Agent Merchant
[**agent_shop_api_agents_shop_post**](AgentsApi.md#agent_shop_api_agents_shop_post) | **POST** /api/agents/shop | Agent Shop
[**agent_tools_api_agents_tools_get**](AgentsApi.md#agent_tools_api_agents_tools_get) | **GET** /api/agents/tools | Agent Tools


# **agent_merchant_api_agents_merchant_post**
> object agent_merchant_api_agents_merchant_post(agent_input, authorization=authorization, x_demo_role=x_demo_role)

Agent Merchant

### Example

* Api Key Authentication (demoRole):
* Bearer Authentication (bearerAuth):

```python
import payfound_sdk
from payfound_sdk.models.agent_input import AgentInput
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
    api_instance = payfound_sdk.AgentsApi(api_client)
    agent_input = payfound_sdk.AgentInput() # AgentInput | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Agent Merchant
        api_response = api_instance.agent_merchant_api_agents_merchant_post(agent_input, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of AgentsApi->agent_merchant_api_agents_merchant_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentsApi->agent_merchant_api_agents_merchant_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **agent_input** | [**AgentInput**](AgentInput.md)|  | 
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

# **agent_shop_api_agents_shop_post**
> object agent_shop_api_agents_shop_post(agent_input, authorization=authorization, x_demo_role=x_demo_role)

Agent Shop

### Example

* Api Key Authentication (demoRole):
* Bearer Authentication (bearerAuth):

```python
import payfound_sdk
from payfound_sdk.models.agent_input import AgentInput
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
    api_instance = payfound_sdk.AgentsApi(api_client)
    agent_input = payfound_sdk.AgentInput() # AgentInput | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Agent Shop
        api_response = api_instance.agent_shop_api_agents_shop_post(agent_input, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of AgentsApi->agent_shop_api_agents_shop_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentsApi->agent_shop_api_agents_shop_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **agent_input** | [**AgentInput**](AgentInput.md)|  | 
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

# **agent_tools_api_agents_tools_get**
> object agent_tools_api_agents_tools_get()

Agent Tools

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
    api_instance = payfound_sdk.AgentsApi(api_client)

    try:
        # Agent Tools
        api_response = api_instance.agent_tools_api_agents_tools_get()
        print("The response of AgentsApi->agent_tools_api_agents_tools_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentsApi->agent_tools_api_agents_tools_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

