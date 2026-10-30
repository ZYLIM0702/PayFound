import type { ConversationStarterProps } from '@openuidev/react-ui';

export const shopperSuggestions = [
  'I want to make pasta, help me prep ingredients',
  'What should I buy for a chicken curry for two?',
  'Find a USB-C charger I can pick up tonight',
  'Add the ingredients for fried rice to my basket',
  'Cheapest wireless mouse, open now',
  'Where are my orders?',
] as const;

export const shopperStarters: ConversationStarterProps[] = shopperSuggestions.map(prompt => ({ displayText: prompt, prompt }));

export const merchantStarters: ConversationStarterProps[] = [
  { displayText: 'What needs attention today?', prompt: 'What needs my attention today?' },
  { displayText: "Restock before Friday's rain", prompt: "Which products should I restock before Friday's rain?" },
  { displayText: 'Pickup queue', prompt: 'Show my pickup queue' },
  { displayText: 'Fresh items expiring first', prompt: 'Which fresh items will expire first?' },
  { displayText: 'Low or stale stock', prompt: 'Which products are low on stock or have not been counted recently?' },
  { displayText: 'Sales this week', prompt: 'Show recorded sales for the last 7 days, per currency.' },
  { displayText: 'Recent reviews', prompt: 'What are customers saying in my recent reviews?' },
];
