# IntegrationsApi

All URIs are relative to *http://127.0.0.1:8000*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**integrationsStatusApiIntegrationsStatusGet**](IntegrationsApi.md#integrationsstatusapiintegrationsstatusget) | **GET** /api/integrations/status | Integrations Status |



## integrationsStatusApiIntegrationsStatusGet

> any integrationsStatusApiIntegrationsStatusGet(merchantId, authorization, xDemoRole)

Integrations Status

### Example

```ts
import {
  Configuration,
  IntegrationsApi,
} from 'payfound-sdk';
import type { IntegrationsStatusApiIntegrationsStatusGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new IntegrationsApi(config);

  const body = {
    // string (optional)
    merchantId: merchantId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies IntegrationsStatusApiIntegrationsStatusGetRequest;

  try {
    const data = await api.integrationsStatusApiIntegrationsStatusGet(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **merchantId** | `string` |  | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xDemoRole** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**any**

### Authorization

[demoRole](../README.md#demoRole), [bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

