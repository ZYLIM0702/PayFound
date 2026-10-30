# ConnectorsApi

All URIs are relative to *http://127.0.0.1:8000*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**nativeCheckoutApiConnectorsConnectionIdCheckoutGet**](ConnectorsApi.md#nativecheckoutapiconnectorsconnectionidcheckoutget) | **GET** /api/connectors/{connection_id}/checkout | Native Checkout |
| [**receiveHookApiConnectorsProviderConnectionIdWebhookPost**](ConnectorsApi.md#receivehookapiconnectorsproviderconnectionidwebhookpost) | **POST** /api/connectors/{provider}/{connection_id}/webhook | Receive Hook |
| [**shopifyCallbackApiConnectorsShopifyCallbackGet**](ConnectorsApi.md#shopifycallbackapiconnectorsshopifycallbackget) | **GET** /api/connectors/shopify/callback | Shopify Callback |



## nativeCheckoutApiConnectorsConnectionIdCheckoutGet

> any nativeCheckoutApiConnectorsConnectionIdCheckoutGet(connectionId, productId)

Native Checkout

### Example

```ts
import {
  Configuration,
  ConnectorsApi,
} from 'payfound-sdk';
import type { NativeCheckoutApiConnectorsConnectionIdCheckoutGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new ConnectorsApi(config);

  const body = {
    // string
    connectionId: connectionId_example,
    // string
    productId: productId_example,
  } satisfies NativeCheckoutApiConnectorsConnectionIdCheckoutGetRequest;

  try {
    const data = await api.nativeCheckoutApiConnectorsConnectionIdCheckoutGet(body);
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
| **productId** | `string` |  | [Defaults to `undefined`] |

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


## receiveHookApiConnectorsProviderConnectionIdWebhookPost

> any receiveHookApiConnectorsProviderConnectionIdWebhookPost(provider, connectionId)

Receive Hook

### Example

```ts
import {
  Configuration,
  ConnectorsApi,
} from 'payfound-sdk';
import type { ReceiveHookApiConnectorsProviderConnectionIdWebhookPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new ConnectorsApi(config);

  const body = {
    // string
    provider: provider_example,
    // string
    connectionId: connectionId_example,
  } satisfies ReceiveHookApiConnectorsProviderConnectionIdWebhookPostRequest;

  try {
    const data = await api.receiveHookApiConnectorsProviderConnectionIdWebhookPost(body);
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
| **provider** | `string` |  | [Defaults to `undefined`] |
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


## shopifyCallbackApiConnectorsShopifyCallbackGet

> any shopifyCallbackApiConnectorsShopifyCallbackGet()

Shopify Callback

### Example

```ts
import {
  Configuration,
  ConnectorsApi,
} from 'payfound-sdk';
import type { ShopifyCallbackApiConnectorsShopifyCallbackGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new ConnectorsApi(config);

  try {
    const data = await api.shopifyCallbackApiConnectorsShopifyCallbackGet();
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

