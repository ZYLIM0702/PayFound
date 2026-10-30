
# StreamInput


## Properties

Name | Type
------------ | -------------
`threadId` | string
`runId` | string
`messages` | [Array&lt;Msg&gt;](Msg.md)
`forwardedProps` | { [key: string]: any; }

## Example

```typescript
import type { StreamInput } from 'payfound-sdk'

// TODO: Update the object below with actual values
const example = {
  "threadId": null,
  "runId": null,
  "messages": null,
  "forwardedProps": null,
} satisfies StreamInput

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as StreamInput
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


