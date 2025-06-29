# Mission file format

JSON file with fields

- `expansion` - expansion name
- `mission` - mission name/description
- `cards` - cards required to complete the mission

## cards

Mapping of card rarity to the number of cards of that rarity required to complete the mission.
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

### Possible extension

For a mission where there are multiple ways of completing the goal

e.g. "collect 100 of one of three cards"
```
{
    "cards": {
        "DIAMOND1": [
            [100, 0, 0],
            [0, 100, 0],
            [0, 0, 100]
        ]
    }
}
````

Possible shorthand `{"DIAMOND1": "FIRST(100, 3)"}`