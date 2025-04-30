# Pokemon TCG Pocket Simulation

Monte Carlo simulation of pulling cards from Pokemon TCG Pocket boosters.

## Simulate Expansion

The goal of this script is to estimate how long it would take to pull all cards is each expansion of Pokemon TCG Pocket.

This assumes opening packs until all the cards have been pulled at least once, or until we acquire enough pack points to buy the ones that haven't been pulled.
Since you can only hold a maximum of 2,500 pack points, if we hit that number we buy the rarest remaining card then continue opening boosters.

For expansions with multiple variants, we repeatedly loop through the variants (e.g. Charizard, Mewtwo, Pikachu, Charizard, Mewtwo, etc.).

The `expansions` directory contains metadata about each expansion (numbers of cards, offering rates, etc.)

Blog post: _coming soon_

### Example results

The following are the average number of packs you would need to open to obtain all the common (1 to 4 diamond) cards, and the complete set of all cards.

| Expansion            | Common | Complete |
| -------------------- | -----: | -------: |
| Genetic Apex         |    781 |     2208 |
| Mythical Island      |    149 |      700 |
| Space-Time Smackdown |    460 |     1753 |
| Triumphant Light     |    191 |      876 |
| Shining Revelry      |    303 |     1185 |
| Celestial Guardians  |    484 |     2143 |

This suggests, for example, that free players would need to open 2 Genetic Apex boosters a day for on average ~3 years to complete that set.

### Missions

Missions allow you to restrict the simulation to obtaining some subset of cards within an expansion.

Missions are defined in json format files. The `missions` directory contains some examples.

NOTE: the design doesn't currently support missions with duplicate cards

### Initial state

Initial state allows you to tell the simulation which (unique) cards you already have, and how many pack points. The simulation will then estimate how long it will take to complete the set.

When combined with a 'mission', the initial state should be restricted to cards within the mission - e.g. if the mission is to obtain 4 one-star cards and you already have 2 one-star cards, one from the mission and one not, the initial state is 1 one-star card.

Initial state is define in a json format file. The `collected` directory contains some examples.

## Simulate Mission

The goal of this simulation is to determine - for a given set of cards, how many packs would I need to open to either pull all the cards or have enough pack points to buy the ones I haven't pulled yet.

This was written before the more general `simulate_expansion.py` script. It's less flexible, and the output is slightly different.

Currently it's hardcoded for pulling the "Champion of the Sinnoh Region" secret mission cards from "Space Time Smackdown" Palkia boosters.

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
