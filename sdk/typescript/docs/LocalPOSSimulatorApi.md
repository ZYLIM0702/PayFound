# LocalPOSSimulatorApi

All URIs are relative to *http://127.0.0.1:8000*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**connectApiPosSimulatorConnectPost**](LocalPOSSimulatorApi.md#connectapipossimulatorconnectpost) | **POST** /api/pos-simulator/connect | Connect |
| [**connectionApiPosSimulatorConnectionPatch**](LocalPOSSimulatorApi.md#connectionapipossimulatorconnectionpatch) | **PATCH** /api/pos-simulator/connection | Connection |
| [**saleApiPosSimulatorSalesPost**](LocalPOSSimulatorApi.md#saleapipossimulatorsalespost) | **POST** /api/pos-simulator/sales | Sale |
| [**stateApiPosSimulatorStateGet**](LocalPOSSimulatorApi.md#stateapipossimulatorstateget) | **GET** /api/pos-simulator/state | State |
| [**stockCountApiPosSimulatorStockCountPost**](LocalPOSSimulatorApi.md#stockcountapipossimulatorstockcountpost) | **POST** /api/pos-simulator/stock-count | Stock Count |
| [**synchronizeApiPosSimulatorSyncPost**](LocalPOSSimulatorApi.md#synchronizeapipossimulatorsyncpost) | **POST** /api/pos-simulator/sync | Synchronize |



## connectApiPosSimulatorConnectPost

> any connectApiPosSimulatorConnectPost(merchantId, authorization, xDemoRole)

Connect

### Example

```ts
import {
  Configuration,
  LocalPOSSimulatorApi,
} from 'payfound-sdk';
import type { ConnectApiPosSimulatorConnectPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new LocalPOSSimulatorApi(config);

  const body = {
    // string
    merchantId: merchantId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies ConnectApiPosSimulatorConnectPostRequest;

  try {
    const data = await api.connectApiPosSimulatorConnectPost(body);
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


## connectionApiPosSimulatorConnectionPatch

> any connectionApiPosSimulatorConnectionPatch(merchantId, connectionInput, authorization, xDemoRole)

Connection

### Example

```ts
import {
  Configuration,
  LocalPOSSimulatorApi,
} from 'payfound-sdk';
import type { ConnectionApiPosSimulatorConnectionPatchRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new LocalPOSSimulatorApi(config);

  const body = {
    // string
    merchantId: merchantId_example,
    // ConnectionInput
    connectionInput: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies ConnectionApiPosSimulatorConnectionPatchRequest;

  try {
    const data = await api.connectionApiPosSimulatorConnectionPatch(body);
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
| **connectionInput** | [ConnectionInput](ConnectionInput.md) |  | |
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


## saleApiPosSimulatorSalesPost

> any saleApiPosSimulatorSalesPost(merchantId, saleInput, authorization, xDemoRole)

Sale

### Example

```ts
import {
  Configuration,
  LocalPOSSimulatorApi,
} from 'payfound-sdk';
import type { SaleApiPosSimulatorSalesPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new LocalPOSSimulatorApi(config);

  const body = {
    // string
    merchantId: merchantId_example,
    // SaleInput
    saleInput: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies SaleApiPosSimulatorSalesPostRequest;

  try {
    const data = await api.saleApiPosSimulatorSalesPost(body);
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
| **saleInput** | [SaleInput](SaleInput.md) |  | |
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


## stateApiPosSimulatorStateGet

> any stateApiPosSimulatorStateGet(merchantId, authorization, xDemoRole)

State

### Example

```ts
import {
  Configuration,
  LocalPOSSimulatorApi,
} from 'payfound-sdk';
import type { StateApiPosSimulatorStateGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new LocalPOSSimulatorApi(config);

  const body = {
    // string
    merchantId: merchantId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies StateApiPosSimulatorStateGetRequest;

  try {
    const data = await api.stateApiPosSimulatorStateGet(body);
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


## stockCountApiPosSimulatorStockCountPost

> any stockCountApiPosSimulatorStockCountPost(merchantId, stockInput, authorization, xDemoRole)

Stock Count

### Example

```ts
import {
  Configuration,
  LocalPOSSimulatorApi,
} from 'payfound-sdk';
import type { StockCountApiPosSimulatorStockCountPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new LocalPOSSimulatorApi(config);

  const body = {
    // string
    merchantId: merchantId_example,
    // StockInput
    stockInput: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies StockCountApiPosSimulatorStockCountPostRequest;

  try {
    const data = await api.stockCountApiPosSimulatorStockCountPost(body);
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
| **stockInput** | [StockInput](StockInput.md) |  | |
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


## synchronizeApiPosSimulatorSyncPost

> any synchronizeApiPosSimulatorSyncPost(merchantId, authorization, xDemoRole)

Synchronize

### Example

```ts
import {
  Configuration,
  LocalPOSSimulatorApi,
} from 'payfound-sdk';
import type { SynchronizeApiPosSimulatorSyncPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new LocalPOSSimulatorApi(config);

  const body = {
    // string
    merchantId: merchantId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies SynchronizeApiPosSimulatorSyncPostRequest;

  try {
    const data = await api.synchronizeApiPosSimulatorSyncPost(body);
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

