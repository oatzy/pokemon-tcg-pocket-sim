# Pokemon TCG Pocket Simulation

Monte Carlo simulation of pulling rare cards from Pokemon TCG Pocket boosters.

The goal is to determine - for a given set of cards, how many packs would I need to open to either pull all the cards or have enough pack points to buy the ones I haven't pulled yet.

Currently it's hardcoded for pulling the "Champion of the Sinnoh Region" secret mission cards from "Space Time Smackdown" Palkia boosters.

Blog post: [When will I get the cards I want in Pokemon TCG Pocket](https://oatzy.github.io/2025/04/08/how-log-to-pull-pokemon.html)

Requires Python 3.8 or newer

## Example output

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

# Probabilities of card sets
 - Garchomp, Gastrodon: 0.0001
 - Cynthia, Spiritomb: 0.0002
 - Cynthia, Garchomp: 0.0002
 - Cynthia, Gastrodon: 0.0002
 - Cynthia, Lucario: 0.0004
 - Cynthia, Garchomp, Gastrodon: 0.0084
 - Cynthia, Lucario, Spiritomb: 0.0084
 - Cynthia, Gastrodon, Spiritomb: 0.009
 - Cynthia, Garchomp, Spiritomb: 0.0092
 - Cynthia, Garchomp, Lucario: 0.0094
 - Cynthia, Gastrodon, Lucario: 0.0094
 - Gastrodon, Lucario, Spiritomb: 0.012
 - Garchomp, Gastrodon, Lucario: 0.0133
 - Garchomp, Gastrodon, Spiritomb: 0.0135
 - Garchomp, Lucario, Spiritomb: 0.0147
 - Cynthia, Garchomp, Gastrodon, Lucario: 0.0621
 - Cynthia, Garchomp, Lucario, Spiritomb: 0.0641
 - Cynthia, Gastrodon, Lucario, Spiritomb: 0.0642
 - Cynthia, Garchomp, Gastrodon, Spiritomb: 0.0657
 - Cynthia, Garchomp, Gastrodon, Lucario, Spiritomb: 0.1305
 - Garchomp, Gastrodon, Lucario, Spiritomb: 0.505
```
