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
- De-escalation (110 markets) — deal, pause, reduce, agreement<br>
- Escalation — impose, increase, new tariff<br>

=== NET SIGNAL correlation with btc_change daily (de-escalation - escalation) ===<br>
  Lag  1 days: +0.163<br>
  Lag  3 days: +0.197<br>
  Lag  5 days: +0.317<br>
  Lag  7 days: +0.349<br>
  Lag 10 days: +0.517<br>
  Lag 14 days: +0.534<br>


Story behind:<br>

Trump announces/escalates tariffs<br>
→ Escalation odds rise on Polymarket<br>
→ Net signal goes negative<br>
→ Risk-off sentiment builds<br>
→ Bitcoin falls 10-14 days later<br>

Trump pauses/reduces tariffs<br>
→ De-escalation odds rise on Polymarket<br>
→ Net signal goes positive  <br>
→ Risk-on sentiment returns<br>
→ Bitcoin rises 10-14 days later<br>
