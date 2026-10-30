# AgentsApi

All URIs are relative to *http://127.0.0.1:8000*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**agentMerchantApiAgentsMerchantPost**](AgentsApi.md#agentmerchantapiagentsmerchantpost) | **POST** /api/agents/merchant | Agent Merchant |
| [**agentShopApiAgentsShopPost**](AgentsApi.md#agentshopapiagentsshoppost) | **POST** /api/agents/shop | Agent Shop |
| [**agentToolsApiAgentsToolsGet**](AgentsApi.md#agenttoolsapiagentstoolsget) | **GET** /api/agents/tools | Agent Tools |



## agentMerchantApiAgentsMerchantPost

> any agentMerchantApiAgentsMerchantPost(agentInput, authorization, xDemoRole)

Agent Merchant

### Example

```ts
import {
  Configuration,
  AgentsApi,
} from 'payfound-sdk';
import type { AgentMerchantApiAgentsMerchantPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AgentsApi(config);

  const body = {
    // AgentInput
    agentInput: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies AgentMerchantApiAgentsMerchantPostRequest;

  try {
    const data = await api.agentMerchantApiAgentsMerchantPost(body);
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
| **agentInput** | [AgentInput](AgentInput.md) |  | |
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


## agentShopApiAgentsShopPost

> any agentShopApiAgentsShopPost(agentInput, authorization, xDemoRole)

Agent Shop

### Example

```ts
import {
  Configuration,
  AgentsApi,
} from 'payfound-sdk';
import type { AgentShopApiAgentsShopPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AgentsApi(config);

  const body = {
    // AgentInput
    agentInput: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies AgentShopApiAgentsShopPostRequest;

  try {
    const data = await api.agentShopApiAgentsShopPost(body);
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
| **agentInput** | [AgentInput](AgentInput.md) |  | |
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


## agentToolsApiAgentsToolsGet

> any agentToolsApiAgentsToolsGet()

Agent Tools

### Example

```ts
import {
  Configuration,
  AgentsApi,
} from 'payfound-sdk';
import type { AgentToolsApiAgentsToolsGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AgentsApi(config);

  try {
    const data = await api.agentToolsApiAgentsToolsGet();
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

