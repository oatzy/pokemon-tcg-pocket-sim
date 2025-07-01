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

For the Eevee Grove emblem secret mission, it is required to collect 100 cards made up of any of 6 cards.

To represent this, we might do something like

```
{
    "cards": {
        "$total": {
            "cards": {
                "DIAMOND1": 4,
                "DIAMOND2": 2
            },
            "total": 100
        }
    }
}
```

or

```
{
    "cards": {
        "DIAMOND1": 4,
        "DIAMOND2": 2
    }
    "condition": {
        "$total": 100
    }
}
```

The latter is simpler, but the former is more flexible, and potentially supports recursive conditions (if indeed such a thing is needed).

This suggests a syntax for general mission 'functions' (plugins?).

The standard behaviour would be equivalent to something like `"condition": {"$all": true}`

Q: how to represent alternates - e.g. collect any eevee card (whether 1 diamond, 4 diamond (ex), 1 star, etc)