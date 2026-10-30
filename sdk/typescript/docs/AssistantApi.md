# AssistantApi

All URIs are relative to *http://127.0.0.1:8000*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**assistantStreamApiAssistantStreamPost**](AssistantApi.md#assistantstreamapiassistantstreampost) | **POST** /api/assistant/stream | Assistant Stream |
| [**createThreadApiAssistantThreadsPost**](AssistantApi.md#createthreadapiassistantthreadspost) | **POST** /api/assistant/threads | Create Thread |
| [**deleteThreadApiAssistantThreadsThreadIdDelete**](AssistantApi.md#deletethreadapiassistantthreadsthreadiddelete) | **DELETE** /api/assistant/threads/{thread_id} | Delete Thread |
| [**getThreadApiAssistantThreadsThreadIdGet**](AssistantApi.md#getthreadapiassistantthreadsthreadidget) | **GET** /api/assistant/threads/{thread_id} | Get Thread |
| [**listThreadsApiAssistantThreadsGet**](AssistantApi.md#listthreadsapiassistantthreadsget) | **GET** /api/assistant/threads | List Threads |
| [**realtimeSessionApiAssistantRealtimeSessionPost**](AssistantApi.md#realtimesessionapiassistantrealtimesessionpost) | **POST** /api/assistant/realtime/session | Realtime Session |
| [**realtimeToolApiAssistantRealtimeToolPost**](AssistantApi.md#realtimetoolapiassistantrealtimetoolpost) | **POST** /api/assistant/realtime/tool | Realtime Tool |
| [**renameThreadApiAssistantThreadsThreadIdPatch**](AssistantApi.md#renamethreadapiassistantthreadsthreadidpatch) | **PATCH** /api/assistant/threads/{thread_id} | Rename Thread |
| [**transcribeApiAssistantTranscribePost**](AssistantApi.md#transcribeapiassistanttranscribepost) | **POST** /api/assistant/transcribe | Transcribe |



## assistantStreamApiAssistantStreamPost

> any assistantStreamApiAssistantStreamPost(streamInput, authorization, xDemoRole)

Assistant Stream

### Example

```ts
import {
  Configuration,
  AssistantApi,
} from 'payfound-sdk';
import type { AssistantStreamApiAssistantStreamPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AssistantApi(config);

  const body = {
    // StreamInput
    streamInput: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies AssistantStreamApiAssistantStreamPostRequest;

  try {
    const data = await api.assistantStreamApiAssistantStreamPost(body);
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
| **streamInput** | [StreamInput](StreamInput.md) |  | |
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


## createThreadApiAssistantThreadsPost

> any createThreadApiAssistantThreadsPost(threadIn, authorization, xDemoRole)

Create Thread

### Example

```ts
import {
  Configuration,
  AssistantApi,
} from 'payfound-sdk';
import type { CreateThreadApiAssistantThreadsPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AssistantApi(config);

  const body = {
    // ThreadIn
    threadIn: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies CreateThreadApiAssistantThreadsPostRequest;

  try {
    const data = await api.createThreadApiAssistantThreadsPost(body);
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
| **threadIn** | [ThreadIn](ThreadIn.md) |  | |
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


## deleteThreadApiAssistantThreadsThreadIdDelete

> deleteThreadApiAssistantThreadsThreadIdDelete(threadId, authorization, xDemoRole)

Delete Thread

### Example

```ts
import {
  Configuration,
  AssistantApi,
} from 'payfound-sdk';
import type { DeleteThreadApiAssistantThreadsThreadIdDeleteRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AssistantApi(config);

  const body = {
    // string
    threadId: threadId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies DeleteThreadApiAssistantThreadsThreadIdDeleteRequest;

  try {
    const data = await api.deleteThreadApiAssistantThreadsThreadIdDelete(body);
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
| **threadId** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xDemoRole** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

`void` (Empty response body)

### Authorization

[demoRole](../README.md#demoRole), [bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **204** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## getThreadApiAssistantThreadsThreadIdGet

> any getThreadApiAssistantThreadsThreadIdGet(threadId, authorization, xDemoRole)

Get Thread

### Example

```ts
import {
  Configuration,
  AssistantApi,
} from 'payfound-sdk';
import type { GetThreadApiAssistantThreadsThreadIdGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AssistantApi(config);

  const body = {
    // string
    threadId: threadId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies GetThreadApiAssistantThreadsThreadIdGetRequest;

  try {
    const data = await api.getThreadApiAssistantThreadsThreadIdGet(body);
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
| **threadId** | `string` |  | [Defaults to `undefined`] |
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


## listThreadsApiAssistantThreadsGet

> any listThreadsApiAssistantThreadsGet(surface, authorization, xDemoRole)

List Threads

### Example

```ts
import {
  Configuration,
  AssistantApi,
} from 'payfound-sdk';
import type { ListThreadsApiAssistantThreadsGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AssistantApi(config);

  const body = {
    // string (optional)
    surface: surface_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies ListThreadsApiAssistantThreadsGetRequest;

  try {
    const data = await api.listThreadsApiAssistantThreadsGet(body);
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
| **surface** | `string` |  | [Optional] [Defaults to `undefined`] |
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


## realtimeSessionApiAssistantRealtimeSessionPost

> any realtimeSessionApiAssistantRealtimeSessionPost(sessionInput, authorization, xDemoRole)

Realtime Session

### Example

```ts
import {
  Configuration,
  AssistantApi,
} from 'payfound-sdk';
import type { RealtimeSessionApiAssistantRealtimeSessionPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AssistantApi(config);

  const body = {
    // SessionInput
    sessionInput: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies RealtimeSessionApiAssistantRealtimeSessionPostRequest;

  try {
    const data = await api.realtimeSessionApiAssistantRealtimeSessionPost(body);
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
| **sessionInput** | [SessionInput](SessionInput.md) |  | |
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


## realtimeToolApiAssistantRealtimeToolPost

> any realtimeToolApiAssistantRealtimeToolPost(toolInput, authorization, xDemoRole)

Realtime Tool

Run one read-only assistant tool for the voice session, with the caller\&#39;s own Principal.

### Example

```ts
import {
  Configuration,
  AssistantApi,
} from 'payfound-sdk';
import type { RealtimeToolApiAssistantRealtimeToolPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AssistantApi(config);

  const body = {
    // ToolInput
    toolInput: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies RealtimeToolApiAssistantRealtimeToolPostRequest;

  try {
    const data = await api.realtimeToolApiAssistantRealtimeToolPost(body);
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
| **toolInput** | [ToolInput](ToolInput.md) |  | |
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


## renameThreadApiAssistantThreadsThreadIdPatch

> any renameThreadApiAssistantThreadsThreadIdPatch(threadId, threadPatch, authorization, xDemoRole)

Rename Thread

### Example

```ts
import {
  Configuration,
  AssistantApi,
} from 'payfound-sdk';
import type { RenameThreadApiAssistantThreadsThreadIdPatchRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AssistantApi(config);

  const body = {
    // string
    threadId: threadId_example,
    // ThreadPatch
    threadPatch: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies RenameThreadApiAssistantThreadsThreadIdPatchRequest;

  try {
    const data = await api.renameThreadApiAssistantThreadsThreadIdPatch(body);
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
| **threadId** | `string` |  | [Defaults to `undefined`] |
| **threadPatch** | [ThreadPatch](ThreadPatch.md) |  | |
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


## transcribeApiAssistantTranscribePost

> any transcribeApiAssistantTranscribePost(file, authorization, xDemoRole)

Transcribe

### Example

```ts
import {
  Configuration,
  AssistantApi,
} from 'payfound-sdk';
import type { TranscribeApiAssistantTranscribePostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AssistantApi(config);

  const body = {
    // Blob
    file: BINARY_DATA_HERE,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies TranscribeApiAssistantTranscribePostRequest;

  try {
    const data = await api.transcribeApiAssistantTranscribePost(body);
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
| **file** | `Blob` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xDemoRole** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**any**

### Authorization

[demoRole](../README.md#demoRole), [bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: `multipart/form-data`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

