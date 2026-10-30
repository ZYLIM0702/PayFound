
# UpdateInput


## Properties

Name | Type
------------ | -------------
`schedule` | string
`paused` | boolean

## Example

```typescript
import type { UpdateInput } from 'payfound-sdk'

// TODO: Update the object below with actual values
const example = {
  "schedule": null,
  "paused": null,
} satisfies UpdateInput

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as UpdateInput
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


