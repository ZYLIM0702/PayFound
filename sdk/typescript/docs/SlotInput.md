
# SlotInput


## Properties

Name | Type
------------ | -------------
`merchantId` | string
`locationId` | string
`startAt` | Date
`endAt` | Date
`capacity` | number

## Example

```typescript
import type { SlotInput } from 'payfound-sdk'

// TODO: Update the object below with actual values
const example = {
  "merchantId": null,
  "locationId": null,
  "startAt": null,
  "endAt": null,
  "capacity": null,
} satisfies SlotInput

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as SlotInput
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


