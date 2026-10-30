# OnlineApi

All URIs are relative to *http://127.0.0.1:8000*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**onlineProductApiOnlineProductsProductIdGet**](OnlineApi.md#onlineproductapionlineproductsproductidget) | **GET** /api/online/products/{product_id} | Online Product |
| [**onlineSearchApiOnlineSearchGet**](OnlineApi.md#onlinesearchapionlinesearchget) | **GET** /api/online/search | Online Search |



## onlineProductApiOnlineProductsProductIdGet

> any onlineProductApiOnlineProductsProductIdGet(productId, authorization, xDemoRole)

Online Product

### Example

```ts
import {
  Configuration,
  OnlineApi,
} from 'payfound-sdk';
import type { OnlineProductApiOnlineProductsProductIdGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new OnlineApi(config);

  const body = {
    // string
    productId: productId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies OnlineProductApiOnlineProductsProductIdGetRequest;

  try {
    const data = await api.onlineProductApiOnlineProductsProductIdGet(body);
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
| **productId** | `string` |  | [Defaults to `undefined`] |
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


## onlineSearchApiOnlineSearchGet

> any onlineSearchApiOnlineSearchGet(q, pageToken, authorization, xDemoRole)

Online Search

### Example

```ts
import {
  Configuration,
  OnlineApi,
} from 'payfound-sdk';
import type { OnlineSearchApiOnlineSearchGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new OnlineApi(config);

  const body = {
    // string
    q: q_example,
    // string (optional)
    pageToken: pageToken_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies OnlineSearchApiOnlineSearchGetRequest;

  try {
    const data = await api.onlineSearchApiOnlineSearchGet(body);
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
| **q** | `string` |  | [Defaults to `undefined`] |
| **pageToken** | `string` |  | [Optional] [Defaults to `undefined`] |
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

