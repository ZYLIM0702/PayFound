
# AgentInput


## Properties

Name | Type
------------ | -------------
`message` | string
`latitude` | number
`longitude` | number
`radiusKm` | number
`merchantId` | string

## Example

```typescript
import type { AgentInput } from 'payfound-sdk'

// TODO: Update the object below with actual values
const example = {
  "message": null,
  "latitude": null,
  "longitude": null,
  "radiusKm": null,
  "merchantId": null,
} satisfies AgentInput

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as AgentInput
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


