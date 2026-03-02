## Summary

Step 1 : ACF Analysis<br>
I ran autocorrelation on daily odds changes for each Polymarket question to find how long each market's signal persists.<br>
Get rid of less than 3 days. -> mostly 5-11 days

Step 2 : Event Study<br>
found date that odd change more than 5 percent in one day -> direction and average bitcoin return <br>
-> direction odds and avg_btc_return same way -> 2 question<br>

1. Will Trump agree to a tariff agreement with Brazil in September?<br>

2. MicroStrategy sells any Bitcoin by December 31, 2026?<br>

-> do not care direction -> question with high average bitcoin return and reasonable cause -> 3 questions

1. MicroStrategy sells any Bitcoin by December 31, 2026?<br>

2. US GDP growth 2.0-2.5% (MACRO SIGNAL)<br>

3. French election called (POLITICAL RISK SIGNAL)<br>

Step 3 : Theme of question

We first work on Tariff<br>
Search on list of question with<br>
- De-escalation (110 markets) — deal, pause, reduce, agreement
- Escalation — impose, increase, new tariff

=== NET SIGNAL correlation with btc_change daily (de-escalation - escalation) ===
  Lag  1 days: +0.163
  Lag  3 days: +0.197
  Lag  5 days: +0.317
  Lag  7 days: +0.349
  Lag 10 days: +0.517
  Lag 14 days: +0.534


Story behind:

Trump announces/escalates tariffs
→ Escalation odds rise on Polymarket
→ Net signal goes negative
→ Risk-off sentiment builds
→ Bitcoin falls 10-14 days later

Trump pauses/reduces tariffs
→ De-escalation odds rise on Polymarket
→ Net signal goes positive  
→ Risk-on sentiment returns
→ Bitcoin rises 10-14 days later
