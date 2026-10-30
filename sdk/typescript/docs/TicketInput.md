
# TicketInput


## Properties

Name | Type
------------ | -------------
`topic` | string
`subject` | string
`message` | string
`orderId` | string

## Example

```typescript
import type { TicketInput } from 'payfound-sdk'

// TODO: Update the object below with actual values
const example = {
  "topic": null,
  "subject": null,
  "message": null,
  "orderId": null,
} satisfies TicketInput

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as TicketInput
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


