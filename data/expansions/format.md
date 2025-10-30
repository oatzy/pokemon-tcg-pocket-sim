# Expansion file format

JSON file describing an expansion.

Fields:

- `name` - names of the expansion
- `variants` - list of variant names (if any)
- `booster_rates` - percentage probability of each booster type
- `cards_per_pack` - number of cards in a standard booster pack (plus-one boosters have this + 1). Default = 5
- `rarities` - list of rarity objects

## booster_rates

Optional. If not specified, the default rate of `99.950` regular and `0.050` rare is assumed.

Introduced to account for the new 'regular + one card' boosters introduced in "Wisdom of Sea and Sky".
Also allows for the possibility of the base rates changing, e.g. if they decide to make rare boosters less rare.

## rarities

Fields:

- `name` - name of the rarity
- `cost` - how many pack points it costs to buy a card of this rarity
- `offering_rate` - percentage probability of a card of this rarity appearing in position 1 to 5
- `counts` - number of cards of this rarity
- `common` - whether cards of this rarity are 'common', i.e. 1 to 4 diamond cards
- `rare` - whether cards of this rarity appear in rare boosters (default = false)
- `rare_count` - counts for this rarity in rare boosters (if different from regular boosters)
- `plus_one` - whether the cards are only available as the 6th card in a 'regular + 1' booster

The name must match across missions and collections (if used), but otherwise don't matter.

Offering rates can be found in game.

For `plus_one: true` the offering rate is a single number, as those cards can only appear in position 6.
Similarly, for everything else there's no need to specify a 6th probability as it is always 0

### counts

Counts are the number of cards of this rarity, broken down by variant (where relevant)

e.g.  `{"Charizard": 5, "Pikachu": 5, "_any_": 3}` means 5 cards appear in only the Charizard variant, 5 only in the Pikachu variant, and 3 cards appear in both Charizard and Pikachu variants.

If there are no variants, then a single integer can be used. E.g. `3` is equivalent to `{"_any_": 3}`

Counts can be found in game, but figuring out which cards appear in all variants (`_any_`) takes some working out.

# Plus one

Wisdom of Sea and Sky introduces a new type of booster - "regular + one card"

As the name suggest it's a regular pack but with an extra sixth card.
The sixth cards are _only_ available as the sixth in a plus-one pack, i.e. you can't get them in 'regular' regular packs..

After a lot of thought, I decided it was best to treat these as their own rarity type, e.g. `STAR1+1` rather than a special case of `STAR1`. Plus, I think it's more useful/interesting to see how long it takes to collect the plus ones independent of their nominal rarity. Also, unlike regular one star cards, the plus one star cards don't appear in rare boosters.