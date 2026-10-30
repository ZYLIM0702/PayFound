
# StartInput


## Properties

Name | Type
------------ | -------------
`merchantId` | string
`orderId` | string
`body` | string

## Example

```typescript
import type { StartInput } from 'payfound-sdk'

// TODO: Update the object below with actual values
const example = {
  "merchantId": null,
  "orderId": null,
  "body": null,
} satisfies StartInput

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as StartInput
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


