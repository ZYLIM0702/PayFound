# ProductsApi

All URIs are relative to *http://127.0.0.1:8000*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**productDetailApiProductsProductIdGet**](ProductsApi.md#productdetailapiproductsproductidget) | **GET** /api/products/{product_id} | Product Detail |
| [**productsApiProductsGet**](ProductsApi.md#productsapiproductsget) | **GET** /api/products | Products |



## productDetailApiProductsProductIdGet

> any productDetailApiProductsProductIdGet(productId, latitude, longitude)

Product Detail

### Example

```ts
import {
  Configuration,
  ProductsApi,
} from 'payfound-sdk';
import type { ProductDetailApiProductsProductIdGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new ProductsApi(config);

  const body = {
    // string
    productId: productId_example,
    // number (optional)
    latitude: 8.14,
    // number (optional)
    longitude: 8.14,
  } satisfies ProductDetailApiProductsProductIdGetRequest;

  try {
    const data = await api.productDetailApiProductsProductIdGet(body);
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
| **latitude** | `number` |  | [Optional] [Defaults to `undefined`] |
| **longitude** | `number` |  | [Optional] [Defaults to `undefined`] |

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


## productsApiProductsGet

> any productsApiProductsGet(q, category, merchantId, latitude, longitude, radiusKm, openNow, inStock, locationId, ids, limit, offset)

Products

### Example

```ts
import {
  Configuration,
  ProductsApi,
} from 'payfound-sdk';
import type { ProductsApiProductsGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new ProductsApi(config);

  const body = {
    // string (optional)
    q: q_example,
    // string (optional)
    category: category_example,
    // string (optional)
    merchantId: merchantId_example,
    // number (optional)
    latitude: 8.14,
    // number (optional)
    longitude: 8.14,
    // number (optional)
    radiusKm: 8.14,
    // boolean (optional)
    openNow: true,
    // boolean (optional)
    inStock: true,
    // string (optional)
    locationId: locationId_example,
    // string (optional)
    ids: ids_example,
    // number (optional)
    limit: 56,
    // number (optional)
    offset: 56,
  } satisfies ProductsApiProductsGetRequest;

  try {
    const data = await api.productsApiProductsGet(body);
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
| **category** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |
| **merchantId** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |
| **latitude** | `number` |  | [Optional] [Defaults to `undefined`] |
| **longitude** | `number` |  | [Optional] [Defaults to `undefined`] |
| **radiusKm** | `number` |  | [Optional] [Defaults to `100`] |
| **openNow** | `boolean` |  | [Optional] [Defaults to `false`] |
| **inStock** | `boolean` |  | [Optional] [Defaults to `false`] |
| **locationId** | `string` |  | [Optional] [Defaults to `undefined`] |
| **ids** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |
| **limit** | `number` |  | [Optional] [Defaults to `400`] |
| **offset** | `number` |  | [Optional] [Defaults to `0`] |

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

