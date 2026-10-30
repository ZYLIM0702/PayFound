# DemoApi

All URIs are relative to *http://127.0.0.1:8000*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**demoIpAnchorApiDemoIpAnchorGet**](DemoApi.md#demoipanchorapidemoipanchorget) | **GET** /api/demo/ip-anchor | Demo Ip Anchor |
| [**demoPlacementResetApiDemoPlacementResetPost**](DemoApi.md#demoplacementresetapidemoplacementresetpost) | **POST** /api/demo/placement/reset | Demo Placement Reset |
| [**demoPlacementStateApiDemoPlacementGet**](DemoApi.md#demoplacementstateapidemoplacementget) | **GET** /api/demo/placement | Demo Placement State |



## demoIpAnchorApiDemoIpAnchorGet

> any demoIpAnchorApiDemoIpAnchorGet()

Demo Ip Anchor

City-level default area from the caller\&#39;s IP (2 dp, memory-cached, never stored). 204 when unknown.

### Example

```ts
import {
  Configuration,
  DemoApi,
} from 'payfound-sdk';
import type { DemoIpAnchorApiDemoIpAnchorGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new DemoApi(config);

  try {
    const data = await api.demoIpAnchorApiDemoIpAnchorGet();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

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

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## demoPlacementResetApiDemoPlacementResetPost

> any demoPlacementResetApiDemoPlacementResetPost()

Demo Placement Reset

Demo-only, loopback-only: forget cached layouts (used to simulate a cold server).

### Example

```ts
import {
  Configuration,
  DemoApi,
} from 'payfound-sdk';
import type { DemoPlacementResetApiDemoPlacementResetPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new DemoApi(config);

  try {
    const data = await api.demoPlacementResetApiDemoPlacementResetPost();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

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

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## demoPlacementStateApiDemoPlacementGet

> any demoPlacementStateApiDemoPlacementGet()

Demo Placement State

How the demo stores are laid out for this viewer (relocated around the anchor, or the original San Francisco set).

### Example

```ts
import {
  Configuration,
  DemoApi,
} from 'payfound-sdk';
import type { DemoPlacementStateApiDemoPlacementGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new DemoApi(config);

  try {
    const data = await api.demoPlacementStateApiDemoPlacementGet();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

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

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

