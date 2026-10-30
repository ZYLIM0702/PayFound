
# StaffInput


## Properties

Name | Type
------------ | -------------
`subject` | string
`email` | string
`role` | string

## Example

```typescript
import type { StaffInput } from 'payfound-sdk'

// TODO: Update the object below with actual values
const example = {
  "subject": null,
  "email": null,
  "role": null,
} satisfies StaffInput

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as StaffInput
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


