# CustomPOSConnectorApi

All URIs are relative to *http://127.0.0.1:8000*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**connectApiMerchantPosPluginConnectionsPost**](CustomPOSConnectorApi.md#connectapimerchantpospluginconnectionspost) | **POST** /api/merchant/pos-plugin/connections | Connect |
| [**disconnectApiMerchantPosPluginConnectionIdDelete**](CustomPOSConnectorApi.md#disconnectapimerchantpospluginconnectioniddelete) | **DELETE** /api/merchant/pos-plugin/{connection_id} | Disconnect |
| [**overviewApiMerchantPosPluginGet**](CustomPOSConnectorApi.md#overviewapimerchantpospluginget) | **GET** /api/merchant/pos-plugin | Overview |
| [**receiveApiPosPluginConnectionIdEventsPost**](CustomPOSConnectorApi.md#receiveapipospluginconnectionideventspost) | **POST** /api/pos-plugin/{connection_id}/events | Receive |
| [**runsApiMerchantPosPluginConnectionIdRunsGet**](CustomPOSConnectorApi.md#runsapimerchantpospluginconnectionidrunsget) | **GET** /api/merchant/pos-plugin/{connection_id}/runs | Runs |
| [**syncNowApiMerchantPosPluginConnectionIdSyncPost**](CustomPOSConnectorApi.md#syncnowapimerchantpospluginconnectionidsyncpost) | **POST** /api/merchant/pos-plugin/{connection_id}/sync | Sync Now |
| [**testApiMerchantPosPluginConnectionIdTestPost**](CustomPOSConnectorApi.md#testapimerchantpospluginconnectionidtestpost) | **POST** /api/merchant/pos-plugin/{connection_id}/test | Test |
| [**updateApiMerchantPosPluginConnectionIdPatch**](CustomPOSConnectorApi.md#updateapimerchantpospluginconnectionidpatch) | **PATCH** /api/merchant/pos-plugin/{connection_id} | Update |



## connectApiMerchantPosPluginConnectionsPost

> any connectApiMerchantPosPluginConnectionsPost(appPosPluginRoutesConnectInput, authorization, xDemoRole)

Connect

### Example

```ts
import {
  Configuration,
  CustomPOSConnectorApi,
} from 'payfound-sdk';
import type { ConnectApiMerchantPosPluginConnectionsPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new CustomPOSConnectorApi(config);

  const body = {
    // AppPosPluginRoutesConnectInput
    appPosPluginRoutesConnectInput: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies ConnectApiMerchantPosPluginConnectionsPostRequest;

  try {
    const data = await api.connectApiMerchantPosPluginConnectionsPost(body);
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
| **appPosPluginRoutesConnectInput** | [AppPosPluginRoutesConnectInput](AppPosPluginRoutesConnectInput.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xDemoRole** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**any**

### Authorization

[demoRole](../README.md#demoRole), [bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## disconnectApiMerchantPosPluginConnectionIdDelete

> any disconnectApiMerchantPosPluginConnectionIdDelete(connectionId, authorization, xDemoRole)

Disconnect

### Example

```ts
import {
  Configuration,
  CustomPOSConnectorApi,
} from 'payfound-sdk';
import type { DisconnectApiMerchantPosPluginConnectionIdDeleteRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new CustomPOSConnectorApi(config);

  const body = {
    // string
    connectionId: connectionId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies DisconnectApiMerchantPosPluginConnectionIdDeleteRequest;

  try {
    const data = await api.disconnectApiMerchantPosPluginConnectionIdDelete(body);
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
| **connectionId** | `string` |  | [Defaults to `undefined`] |
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


## overviewApiMerchantPosPluginGet

> any overviewApiMerchantPosPluginGet(merchantId, authorization, xDemoRole)

Overview

### Example

```ts
import {
  Configuration,
  CustomPOSConnectorApi,
} from 'payfound-sdk';
import type { OverviewApiMerchantPosPluginGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new CustomPOSConnectorApi(config);

  const body = {
    // string
    merchantId: merchantId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies OverviewApiMerchantPosPluginGetRequest;

  try {
    const data = await api.overviewApiMerchantPosPluginGet(body);
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
| **merchantId** | `string` |  | [Defaults to `undefined`] |
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


## receiveApiPosPluginConnectionIdEventsPost

> any receiveApiPosPluginConnectionIdEventsPost(connectionId)

Receive

Signed push. Headers: X-PayFound-Timestamp (unix seconds), X-PayFound-Signature (sha256&#x3D;hex of HMAC-SHA256(secret, timestamp + \&#39;.\&#39; + raw body)).

### Example

```ts
import {
  Configuration,
  CustomPOSConnectorApi,
} from 'payfound-sdk';
import type { ReceiveApiPosPluginConnectionIdEventsPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new CustomPOSConnectorApi(config);

  const body = {
    // string
    connectionId: connectionId_example,
  } satisfies ReceiveApiPosPluginConnectionIdEventsPostRequest;

  try {
    const data = await api.receiveApiPosPluginConnectionIdEventsPost(body);
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
| **connectionId** | `string` |  | [Defaults to `undefined`] |

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


## runsApiMerchantPosPluginConnectionIdRunsGet

> any runsApiMerchantPosPluginConnectionIdRunsGet(connectionId, authorization, xDemoRole)

Runs

### Example

```ts
import {
  Configuration,
  CustomPOSConnectorApi,
} from 'payfound-sdk';
import type { RunsApiMerchantPosPluginConnectionIdRunsGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new CustomPOSConnectorApi(config);

  const body = {
    // string
    connectionId: connectionId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies RunsApiMerchantPosPluginConnectionIdRunsGetRequest;

  try {
    const data = await api.runsApiMerchantPosPluginConnectionIdRunsGet(body);
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
| **connectionId** | `string` |  | [Defaults to `undefined`] |
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


## syncNowApiMerchantPosPluginConnectionIdSyncPost

> any syncNowApiMerchantPosPluginConnectionIdSyncPost(connectionId, authorization, xDemoRole)

Sync Now

### Example

```ts
import {
  Configuration,
  CustomPOSConnectorApi,
} from 'payfound-sdk';
import type { SyncNowApiMerchantPosPluginConnectionIdSyncPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new CustomPOSConnectorApi(config);

  const body = {
    // string
    connectionId: connectionId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies SyncNowApiMerchantPosPluginConnectionIdSyncPostRequest;

  try {
    const data = await api.syncNowApiMerchantPosPluginConnectionIdSyncPost(body);
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
| **connectionId** | `string` |  | [Defaults to `undefined`] |
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


## testApiMerchantPosPluginConnectionIdTestPost

> any testApiMerchantPosPluginConnectionIdTestPost(connectionId, authorization, xDemoRole)

Test

### Example

```ts
import {
  Configuration,
  CustomPOSConnectorApi,
} from 'payfound-sdk';
import type { TestApiMerchantPosPluginConnectionIdTestPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new CustomPOSConnectorApi(config);

  const body = {
    // string
    connectionId: connectionId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies TestApiMerchantPosPluginConnectionIdTestPostRequest;

  try {
    const data = await api.testApiMerchantPosPluginConnectionIdTestPost(body);
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
| **connectionId** | `string` |  | [Defaults to `undefined`] |
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


## updateApiMerchantPosPluginConnectionIdPatch

> any updateApiMerchantPosPluginConnectionIdPatch(connectionId, updateInput, authorization, xDemoRole)

Update

### Example

```ts
import {
  Configuration,
  CustomPOSConnectorApi,
} from 'payfound-sdk';
import type { UpdateApiMerchantPosPluginConnectionIdPatchRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new CustomPOSConnectorApi(config);

  const body = {
    // string
    connectionId: connectionId_example,
    // UpdateInput
    updateInput: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies UpdateApiMerchantPosPluginConnectionIdPatchRequest;

  try {
    const data = await api.updateApiMerchantPosPluginConnectionIdPatch(body);
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
| **connectionId** | `string` |  | [Defaults to `undefined`] |
| **updateInput** | [UpdateInput](UpdateInput.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xDemoRole** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**any**

### Authorization

[demoRole](../README.md#demoRole), [bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

