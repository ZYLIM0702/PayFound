# What drives local store sales, and what the PayFound demo forecast models

This is a plain-language summary of commonly reported retail drivers, written from general retail-operations knowledge
(retail footfall and weather studies, payday and calendar effects, stock-availability research). It cites no figures from
specific papers and invents no statistics. Sizes are qualitative or rough ranges that the demo uses as fixed assumptions.
The PayFound forecast is deterministic arithmetic, not a trained AI model, and calls no LLM.

Confidence labels used in the app: **observed** = measured from this store's own data; **modelled** = real input data with an
assumed effect size; **demo** = demo-only input (fictional events feed, demo calendar); **not modelled** = a real driver we do not have data for.

| Driver | Direction | Categories most affected | What PayFound can observe | Demo models it? |
|---|---|---|---|---|
| Rain and storms | Fewer walk-ins; some demand shifts to pickup and online; essentials hold up | Outdoor, sports, garden, discretionary down (commonly reported up to a quarter or a third in heavy rain); grocery, hardware, pharmacy steady or slightly up | Open-Meteo daily rain chance (live) | Yes. Below 40% chance nothing changes; above, outdoor up to -30%, other discretionary up to -10%, essentials up to +10% (modelled) |
| Heat | Cold drinks and grocery top-ups rise; outdoor activity softens in extreme heat | Beverages, grocery up; outdoor down slightly | Open-Meteo daily max temperature | Yes. From 28 degrees C, grocery/drinks up to +20%, outdoor down to -8% (modelled) |
| Haze / air quality | Outdoor categories and walk-ins fall; masks and air products rise | Outdoor, sports; health | Not connected | No (not modelled) |
| Day of week and time of day | Weekend and Friday peaks; food and cafe peak at lunch and after work; pickup concentrates on weekday evenings | All, food and cafe most | Order timestamps (orders by hour, orders by weekday) | Weekday curve modelled, blended with the store's own weekday pattern once there are 30+ orders. Hour of day is shown in Overview analytics, not in the 7-day index |
| Payday and month-end | First days after payday lift discretionary spend; the days before are tighter | Discretionary (electronics, accessories, gifts) more than essentials | Nothing directly; order history could confirm | Yes, with a demo payday rule per country (month-end; plus the 15th in the US, the 25th in Malaysia). Up to +10% on the payday, fading over 3 days; slightly tighter in the last 3 days before payday (demo) |
| Public holidays | Can close or surge local footfall; travel reduces local footfall while families shop for celebrations | Gifts, food and grocery up before big holidays; local footfall down on the day itself | Nothing directly | Yes, demo calendar (Malaysia, Singapore, United States, plus international dates). Approximate dates, not authoritative |
| School holidays | Families at home: more family and kids' items, more daytime footfall; travel weeks reduce it | Electronics, toys, pet, sports | Fictional events feed has school holidays near the demo stores | Yes (events feed and demo calendar) |
| Local events | Markets, sports fixtures, festivals and concerts pull crowds nearby; parking matters | Categories matching the event (food, drinks, sports, hardware at markets) | Not observed from real feeds; PayFound has a fictional demo feed within 3 km | Yes, from the fictional feed. Boosts scale with footfall class and distance, capped |
| Promotions and price changes | Discount days lift units, sometimes pulling sales forward from the next days | The promoted category | PayFound holds no promotion schedule yet | Not in the baseline. A demo scenario shows a +18% lift for a top category |
| Stock availability | Out of stock caps sales at zero. A stock-out must never be read as low demand | Any | Current counts and holds; last-sale age | Yes. Trailing zero-sale days of a product that is now out of stock are left out of its demand rate; the page says not to reorder on suppressed demand |
| Traffic and commute disruption | Roadworks, rain jams and transit strikes reduce footfall and parking | Walk-in dependent stores | Not connected | No (not modelled) |
| Seasonality | Back-to-school, festive season, Ramadan and Eid, Chinese New Year, Deepavali shift basket size and timing. Ramadan shifts food to evenings and lifts groceries before Eid | Grocery, gifts, electronics, apparel | Nothing directly | Partly. Demo calendar entries for the markets above (marked demo). No month-by-month seasonal curve is fitted |
| Pickup capacity | Sales can only convert up to the published pickup slots | Any pickup-led store | Published slots and booked counts (real) | Yes. Expected orders vs slots per day, flagged ok, tight (85%+), capped (full) or none (no slots) |

## What the demo forecast does

Demand index per category per day = 100 x recent-sales trend x weather x local events x weekday x payday x holiday (100 means a normal day).
Prep quantities are three days of expected units plus a 25% buffer, minus what is available. Every prep line names the driver
that moves that category the most, for example "Rain Friday: +6 USB-C chargers".

## What is demo-only

The holiday and payday calendar, the fictional events feed, the scenario lifts (+18% promotion, rain removed) and all effect
sizes are fixed demo assumptions. The Open-Meteo forecast, stock counts, pickup slots and order history are real data in the demo database.
Do not use the forecast for real purchasing decisions without validating it against actual sales.
