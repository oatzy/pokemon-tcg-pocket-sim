# Collection file format

JSON file describing cards already collected.

Can be used to similar how much longer it will take to complete an expansion or mission

Fields:

- `expansion` - name of the expansion the collection applies to
- `mission` - the mission you're trying to complete
- `pack_points` - number of pack points accumulated (and not spent)
- `collected` - numbers of cards collected so far

The 'mission' may be simply completing the expansion.

When the mission isn't completing the expansion, the collection should only include cards _from that mission_ which have already been collected. For example, if a mission requires one specific 1 star card, the collection should only include `{"STAR1": 1}` if you have the specific card required, not some other 1 star card.

## collected

Mapping of card rarity to the number of cards of that rarity already collected.
The specific cards don't matter, just how many of each rarity, and in which variants.

The rarity names must match with those used in the expansion definition.

Possible values

- integer - when there is only one variant in the expansion
- mapping - variant to count of cards from that variant, e.g. `{"Pikachu": 1, "Charizard": 2}`

Integer `1` is equivalent to `{"_any_": 1}`

### counts

The counts for each rarity can be either

- integer - one of each of the numbered cards, e.g. `3` = one each of 3 unique cards
- list - number required of each card, e.g. `[1, 2]` = one of the first card, 2 of the second card

Integer count `3` is equivalent to list `[1, 1, 1]`

Typically you would use integer, where the amount of each card doesn't matter.
However, some missions require collecting multiples of cards.

When using multiples, the order of the counts needs to match the order of the corresponding mission.
e.g. if the mission is `[99, 1]`, and you already have 50 of the 99,
the collection should be `[50, 0]`, NOT `[0, 50]`

## Possible expansion

Inverse collection - e.g. "I have everything except these cards"
More convenient when you're down to the last few.

e.g. replace `collected` with `missing` (or `need` ?)