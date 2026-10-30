
# ReviewInput


## Properties

Name | Type
------------ | -------------
`orderId` | string
`rating` | number
`body` | string

## Example

```typescript
import type { ReviewInput } from 'payfound-sdk'

// TODO: Update the object below with actual values
const example = {
  "orderId": null,
  "rating": null,
  "body": null,
} satisfies ReviewInput

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as ReviewInput
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


