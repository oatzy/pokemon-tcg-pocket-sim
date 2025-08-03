# Pokemon TCG Pocket Simulation

Monte Carlo simulation of pulling cards from Pokemon TCG Pocket boosters.

The goal of this tool is to estimate how long it would take to pull all cards in each expansion of Pokemon TCG Pocket.

This assumes opening packs until all the cards have been pulled at least once, or until we acquire enough pack points to buy the ones that haven't been pulled.
Since you can only hold a maximum of 2,500 pack points, if we hit that number we buy the rarest remaining card then continue opening boosters.

For expansions with multiple variants, we repeatedly loop through the variants (e.g. Charizard, Mewtwo, Pikachu, Charizard, Mewtwo, etc.),
dropping variants if/when they are completed.

The `data/expansions` directory contains metadata about each expansion (numbers of cards, offering rates, etc.)

Blog post: _coming soon_

## Example results

The following are the average number of packs you would need to open to obtain all the common (1 to 4 diamond) cards, and the complete set of all cards.

| Expansion               | Common | Complete |
| ----------------------- | -----: | -------: |
| Genetic Apex            |    790 |     2052 |
| Mythical Island         |    149 |      659 |
| Space-Time Smackdown    |    460 |     1660 |
| Triumphant Light        |    190 |      832 |
| Shining Revelry         |    307 |     1137 |
| Celestial Guardians     |    485 |     2048 |
| Extradimensional Crisis |    148 |      859 |
| Eevee Grove             |    182 |      906 |
| Wisdom of Sea and Sky   |    521 |     1820 |

This suggests, for example, that free players would on average need to open 2 Genetic Apex boosters a day for ~3 years to complete that set.

## Missions

Missions allow you to restrict the simulation to obtaining some subset of cards within an expansion.

Missions are defined in json format files. The `data/missions` directory contains a description, along with some examples.

## Initial state

Initial state allows you to tell the simulation which cards you already have, and how many pack points. The simulation will then estimate how long it will take to complete the set.

When combined with a 'mission', the initial state must be restricted to cards within the mission - e.g. if the mission is to obtain 4 one-star cards and you already have 2 one-star cards, one from the mission and one not, the initial state is 1 one-star card.

Initial state is define in a json format file. The `data/collected` directory contains a description, along with some examples.


## TODO

Features:

- Support more types of missions, e.g. alternates (collect card A or card B)
- Support defining collection in terms of missing cards

Quality of life:

- Improve output formatting
- Improve performance
- Logging and error handling
- Input validation