# AccountApi

All URIs are relative to *http://127.0.0.1:8000*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**addWishlistApiMeWishlistPost**](AccountApi.md#addwishlistapimewishlistpost) | **POST** /api/me/wishlist | Add Wishlist |
| [**cancelDeliveryApiOrdersOrderIdDeliveryRequestDelete**](AccountApi.md#canceldeliveryapiordersorderiddeliveryrequestdelete) | **DELETE** /api/orders/{order_id}/delivery-request | Cancel Delivery |
| [**deliveryProvidersApiDeliveryProvidersGet**](AccountApi.md#deliveryprovidersapideliveryprovidersget) | **GET** /api/delivery/providers | Delivery Providers |
| [**getCouponsApiMeCouponsGet**](AccountApi.md#getcouponsapimecouponsget) | **GET** /api/me/coupons | Get Coupons |
| [**getProfileApiMeProfileGet**](AccountApi.md#getprofileapimeprofileget) | **GET** /api/me/profile | Get Profile |
| [**getWishlistApiMeWishlistGet**](AccountApi.md#getwishlistapimewishlistget) | **GET** /api/me/wishlist | Get Wishlist |
| [**myDeliveryRequestsApiMeDeliveryRequestsGet**](AccountApi.md#mydeliveryrequestsapimedeliveryrequestsget) | **GET** /api/me/delivery-requests | My Delivery Requests |
| [**myReviewsApiMeReviewsGet**](AccountApi.md#myreviewsapimereviewsget) | **GET** /api/me/reviews | My Reviews |
| [**putProfileApiMeProfilePut**](AccountApi.md#putprofileapimeprofileput) | **PUT** /api/me/profile | Put Profile |
| [**removeWishlistApiMeWishlistProductIdDelete**](AccountApi.md#removewishlistapimewishlistproductiddelete) | **DELETE** /api/me/wishlist/{product_id} | Remove Wishlist |
| [**requestDeliveryApiOrdersOrderIdDeliveryRequestPost**](AccountApi.md#requestdeliveryapiordersorderiddeliveryrequestpost) | **POST** /api/orders/{order_id}/delivery-request | Request Delivery |



## addWishlistApiMeWishlistPost

> any addWishlistApiMeWishlistPost(wishlistInput, authorization, xDemoRole)

Add Wishlist

### Example

```ts
import {
  Configuration,
  AccountApi,
} from 'payfound-sdk';
import type { AddWishlistApiMeWishlistPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AccountApi(config);

  const body = {
    // WishlistInput
    wishlistInput: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies AddWishlistApiMeWishlistPostRequest;

  try {
    const data = await api.addWishlistApiMeWishlistPost(body);
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
| **wishlistInput** | [WishlistInput](WishlistInput.md) |  | |
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


## cancelDeliveryApiOrdersOrderIdDeliveryRequestDelete

> any cancelDeliveryApiOrdersOrderIdDeliveryRequestDelete(orderId, authorization, xDemoRole)

Cancel Delivery

### Example

```ts
import {
  Configuration,
  AccountApi,
} from 'payfound-sdk';
import type { CancelDeliveryApiOrdersOrderIdDeliveryRequestDeleteRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AccountApi(config);

  const body = {
    // string
    orderId: orderId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies CancelDeliveryApiOrdersOrderIdDeliveryRequestDeleteRequest;

  try {
    const data = await api.cancelDeliveryApiOrdersOrderIdDeliveryRequestDelete(body);
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
| **orderId** | `string` |  | [Defaults to `undefined`] |
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


## deliveryProvidersApiDeliveryProvidersGet

> any deliveryProvidersApiDeliveryProvidersGet(authorization, xDemoRole)

Delivery Providers

### Example

```ts
import {
  Configuration,
  AccountApi,
} from 'payfound-sdk';
import type { DeliveryProvidersApiDeliveryProvidersGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AccountApi(config);

  const body = {
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies DeliveryProvidersApiDeliveryProvidersGetRequest;

  try {
    const data = await api.deliveryProvidersApiDeliveryProvidersGet(body);
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


## getCouponsApiMeCouponsGet

> any getCouponsApiMeCouponsGet(authorization, xDemoRole)

Get Coupons

### Example

```ts
import {
  Configuration,
  AccountApi,
} from 'payfound-sdk';
import type { GetCouponsApiMeCouponsGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AccountApi(config);

  const body = {
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies GetCouponsApiMeCouponsGetRequest;

  try {
    const data = await api.getCouponsApiMeCouponsGet(body);
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


## getProfileApiMeProfileGet

> any getProfileApiMeProfileGet(authorization, xDemoRole)

Get Profile

### Example

```ts
import {
  Configuration,
  AccountApi,
} from 'payfound-sdk';
import type { GetProfileApiMeProfileGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AccountApi(config);

  const body = {
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies GetProfileApiMeProfileGetRequest;

  try {
    const data = await api.getProfileApiMeProfileGet(body);
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


## getWishlistApiMeWishlistGet

> any getWishlistApiMeWishlistGet(authorization, xDemoRole)

Get Wishlist

### Example

```ts
import {
  Configuration,
  AccountApi,
} from 'payfound-sdk';
import type { GetWishlistApiMeWishlistGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AccountApi(config);

  const body = {
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies GetWishlistApiMeWishlistGetRequest;

  try {
    const data = await api.getWishlistApiMeWishlistGet(body);
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


## myDeliveryRequestsApiMeDeliveryRequestsGet

> any myDeliveryRequestsApiMeDeliveryRequestsGet(authorization, xDemoRole)

My Delivery Requests

### Example

```ts
import {
  Configuration,
  AccountApi,
} from 'payfound-sdk';
import type { MyDeliveryRequestsApiMeDeliveryRequestsGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AccountApi(config);

  const body = {
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies MyDeliveryRequestsApiMeDeliveryRequestsGetRequest;

  try {
    const data = await api.myDeliveryRequestsApiMeDeliveryRequestsGet(body);
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


## myReviewsApiMeReviewsGet

> any myReviewsApiMeReviewsGet(authorization, xDemoRole)

My Reviews

### Example

```ts
import {
  Configuration,
  AccountApi,
} from 'payfound-sdk';
import type { MyReviewsApiMeReviewsGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AccountApi(config);

  const body = {
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies MyReviewsApiMeReviewsGetRequest;

  try {
    const data = await api.myReviewsApiMeReviewsGet(body);
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


## putProfileApiMeProfilePut

> any putProfileApiMeProfilePut(profileInput, authorization, xDemoRole)

Put Profile

### Example

```ts
import {
  Configuration,
  AccountApi,
} from 'payfound-sdk';
import type { PutProfileApiMeProfilePutRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AccountApi(config);

  const body = {
    // ProfileInput
    profileInput: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies PutProfileApiMeProfilePutRequest;

  try {
    const data = await api.putProfileApiMeProfilePut(body);
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
| **profileInput** | [ProfileInput](ProfileInput.md) |  | |
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


## removeWishlistApiMeWishlistProductIdDelete

> any removeWishlistApiMeWishlistProductIdDelete(productId, authorization, xDemoRole)

Remove Wishlist

### Example

```ts
import {
  Configuration,
  AccountApi,
} from 'payfound-sdk';
import type { RemoveWishlistApiMeWishlistProductIdDeleteRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AccountApi(config);

  const body = {
    // string
    productId: productId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies RemoveWishlistApiMeWishlistProductIdDeleteRequest;

  try {
    const data = await api.removeWishlistApiMeWishlistProductIdDelete(body);
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


## requestDeliveryApiOrdersOrderIdDeliveryRequestPost

> any requestDeliveryApiOrdersOrderIdDeliveryRequestPost(orderId, deliveryInput, authorization, xDemoRole)

Request Delivery

### Example

```ts
import {
  Configuration,
  AccountApi,
} from 'payfound-sdk';
import type { RequestDeliveryApiOrdersOrderIdDeliveryRequestPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AccountApi(config);

  const body = {
    // string
    orderId: orderId_example,
    // DeliveryInput
    deliveryInput: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies RequestDeliveryApiOrdersOrderIdDeliveryRequestPostRequest;

  try {
    const data = await api.requestDeliveryApiOrdersOrderIdDeliveryRequestPost(body);
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
| **orderId** | `string` |  | [Defaults to `undefined`] |
| **deliveryInput** | [DeliveryInput](DeliveryInput.md) |  | |
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

