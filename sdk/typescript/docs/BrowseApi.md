# BrowseApi

All URIs are relative to *http://127.0.0.1:8000*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**browseApiBrowseGet**](BrowseApi.md#browseapibrowseget) | **GET** /api/browse | Browse |



## browseApiBrowseGet

> any browseApiBrowseGet(q, mode, latitude, longitude, radiusKm, limit, authorization, xDemoRole)

Browse

Read-only. Local products (real stock, distance) and online offers are returned in separate sections.

### Example

```ts
import {
  Configuration,
  BrowseApi,
} from 'payfound-sdk';
import type { BrowseApiBrowseGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new BrowseApi(config);

  const body = {
    // string (optional)
    q: q_example,
    // string (optional)
    mode: mode_example,
    // number (optional)
    latitude: 8.14,
    // number (optional)
    longitude: 8.14,
    // number (optional)
    radiusKm: 8.14,
    // number (optional)
    limit: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies BrowseApiBrowseGetRequest;

  try {
    const data = await api.browseApiBrowseGet(body);
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
| **q** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |
| **mode** | `string` |  | [Optional] [Defaults to `&#39;both&#39;`] |
| **latitude** | `number` |  | [Optional] [Defaults to `undefined`] |
| **longitude** | `number` |  | [Optional] [Defaults to `undefined`] |
| **radiusKm** | `number` |  | [Optional] [Defaults to `100`] |
| **limit** | `number` |  | [Optional] [Defaults to `40`] |
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

