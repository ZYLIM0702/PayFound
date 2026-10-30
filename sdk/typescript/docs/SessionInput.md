
# SessionInput


## Properties

Name | Type
------------ | -------------
`vad` | string
`voice` | string
`forwardedProps` | { [key: string]: any; }

## Example

```typescript
import type { SessionInput } from 'payfound-sdk'

// TODO: Update the object below with actual values
const example = {
  "vad": null,
  "voice": null,
  "forwardedProps": null,
} satisfies SessionInput

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as SessionInput
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


