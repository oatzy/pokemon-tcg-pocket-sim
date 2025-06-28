from pokemon_tcg_simulate.expansion import ANY, Rarity, Expansion


def diamond(counts):
    return Rarity("diamond", 70, (100, 100, 100, 0, 0), counts)


class TestRarity:
    def test_init_single_count(self):
        r = diamond(5)
        assert r.counts == {ANY: 5}

    def test_iter_rare_cards_not_rare(self):
        r = diamond(5)
        assert list(r.iter_rare_cards(ANY)) == []

    def test_count_no_variants(self):
        r = diamond({ANY: 5})

        assert r.count() == 5
        assert r.count(ANY) == 5

    def test_count_variants(self):
        r = diamond({ANY: 3, "Pikachu": 5, "Charizard": 7})

        assert r.count() == 15
        assert r.count(ANY) == 3
        assert r.count("Pikachu") == 8
        assert r.count("Charizard") == 10

    def test_pick_no_variants(self):
        r = diamond(5)

        variant, card = r.pick(ANY)
        assert variant == ANY
        assert 0 <= card < 5

    def test_pick_variant(self):
        r = diamond({ANY: 3, "Pikachu": 5, "Charizard": 7})

        pick = r.pick("Pikachu")
        variant, card = pick

        assert variant in (ANY, "Pikachu")
        assert 0 <= card < r.counts[variant]


class TestExpansion:
    pass
