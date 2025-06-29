# Expansion file format

JSON file describing an expansion.

Fields:

- `name` - names of the expansion
- `variants` - list of variant names (if any)
- `rarities` - list of rarity objects

## rarities

Fields:

- `name` - name of the rarity
- `cost` - how many pack points it costs to buy a card of this rarity
- `offering_rate` - percentage probability of a card of this rarity appearing in position 1 to 5
- `counts` - number of cards of this rarity
- `rare` - whether cards of this rarity appear in rare boosters (default = false)
- `rare_count` - counts for this rarity in rare boosters (if different from regular boosters)

The name must match across missions and collections (if used), but otherwise don't matter.

Offering rates can be found in game.

### counts

Counts are the number of cards of this rarity, broken down by variant (where relevant)

e.g.  `{"Charizard": 5, "Pikachu": 5, "_any_": 3}` means 5 cards appear in only the Charizard variant, 5 only in the Pikachu variant, and 3 cards appear in both Charizard and Pikachu variants.

If there are no variants, then a single integer can be used. E.g. `3` is equivalent to `{"_any_": 3}`

Counts can be found in game, but figuring out which cards appear in all variants (`_any_`) takes some working out.