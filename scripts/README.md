# Scripts

## Simulate Mission

The goal of this simulation is to determine - for a given set of cards, how many packs would I need to open to either pull all the cards or have enough pack points to buy the ones I haven't pulled yet.

This was written before the more general main package; it's less flexible, and the output is slightly different.

It's hardcoded for pulling (a subset of) the "Champion of the Sinnoh Region" secret mission cards from "Space Time Smackdown" Palkia boosters.

Blog post: [When will I get the cards I want in Pokemon TCG Pocket](https://oatzy.github.io/2025/04/08/how-log-to-pull-pokemon.html)

Requires Python 3.8 or newer

### Example output

```
# Average boosters opened - 211.7082

# Most likely number opened - 250 (0.438)
# Probability above most common - 0.1374

# Average left over points - 192.131

# Average copies of each card
 - Cynthia: 0.4695
 - Garchomp: 2.2514
 - Spiritomb: 2.2746
 - Gastrodon: 2.2823
 - Lucario: 2.2929
```