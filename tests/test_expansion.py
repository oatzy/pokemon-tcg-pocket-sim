from pokemon_tcg_simulate.expansion import ANY, Rarity, Expansion


def diamond(counts):
    return Rarity(
        name="diamond",
        cost=70,
        offering_rate=(100, 100, 100, 0, 0),
        counts=counts,
    )


class TestRarity:
    def test_init_single_count(self):
        r = diamond(5)
        assert r.counts == {ANY: 5}

    def test_init_no_rare_count(self):
        pass

    def test_iter_rare_cards_not_rare(self):
        r = diamond(5)
        assert list(r.iter_rare_cards(ANY)) == []

    def iter_rare_cards(self):
        pass

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

        for _ in range(10):
            pick = r.pick("Pikachu")
            variant, card = pick

            assert variant in (ANY, "Pikachu")
            assert 0 <= card < r.counts[variant]


class TestExpansion:
    def test_init_cummulative_probabilities(self):
        r1 = Rarity(
            name="diamond", cost=70, offering_rate=(60, 30, 10, 0, 0), counts={ANY: 5}
        )
        r2 = Rarity(
            name="gold", cost=50, offering_rate=(40, 70, 90, 100, 100), counts={ANY: 3}
        )
        exp = Expansion(name="Test", variants=[ANY], rarities=(r1, r2))
        # Check that cumulative probabilities are calculated correctly
        assert exp._cum_prob[0] == [60, 100]
        assert exp._cum_prob[1] == [30, 100]
        assert exp._cum_prob[2] == [10, 100]
        assert exp._cum_prob[3] == [0, 100]
        assert exp._cum_prob[4] == [0, 100]

    def test_from_json_no_variants(self):
        data = {
            "name": "Test",
            "rarities": [
                {
                    "name": "diamond",
                    "cost": 70,
                    "offering_rate": [100, 100, 100, 0, 0],
                    "counts": {ANY: 5},
                }
            ],
        }
        exp = Expansion.from_json(data)
        assert exp.name == "Test"
        assert exp.variants == [ANY]
        assert len(exp.rarities) == 1
        assert exp.rarities[0].name == "diamond"

    def test_from_json_rarity_order(self):
        data = {
            "name": "Test",
            "rarities": [
                {
                    "name": "gold",
                    "cost": 50,
                    "offering_rate": [0, 0, 0, 100, 100],
                    "counts": {ANY: 2},
                },
                {
                    "name": "diamond",
                    "cost": 70,
                    "offering_rate": [100, 100, 100, 0, 0],
                    "counts": {ANY: 5},
                },
            ],
        }
        exp = Expansion.from_json(data)
        # Should be sorted by cost descending
        assert exp.rarities[0].name == "diamond"
        assert exp.rarities[1].name == "gold"

    def test_open_rare(self):
        r1 = Rarity(
            name="diamond",
            cost=70,
            offering_rate=(100, 100, 100, 0, 0),
            counts={ANY: 5},
            rare=True,
        )
        r2 = Rarity(
            name="gold",
            cost=50,
            offering_rate=(0, 0, 0, 100, 100),
            counts={ANY: 2},
            rare=True,
        )
        exp = Expansion(name="Test", variants=[ANY], rarities=(r1, r2))
        result = exp.open_rare(ANY)
        assert len(result) == 5

        for item in result:
            assert item[0] in ("diamond", "gold")
            assert item[1][0] == ANY
            if item[0] == "diamond":
                assert item[1][1] in range(5)
            else:
                assert item[1][1] in range(2)

    def test_open_regular(self):
        r1 = Rarity(
            name="diamond",
            cost=70,
            offering_rate=(100, 100, 100, 0, 0),
            counts={ANY: 5},
        )
        r2 = Rarity(
            name="gold", cost=50, offering_rate=(0, 0, 0, 100, 100), counts={ANY: 2}
        )
        exp = Expansion(name="Test", variants=[ANY], rarities=(r1, r2))
        result = exp.open_regular(ANY)
        assert len(result) == 5

        for item in result[:3]:
            assert item[0] == "diamond"
            assert item[1][0] == ANY
            assert item[1][1] in range(5)

        for item in result[3:]:
            assert item[0] == "gold"
            assert item[1][0] == ANY
            assert item[1][1] in range(2)

    def test_open_regular_with_variants(self):
        r1 = Rarity(
            name="diamond",
            cost=70,
            offering_rate=(100, 100, 100, 0, 0),
            counts={ANY: 5, "Pikachu": 3, "Charizard": 2},
        )
        r2 = Rarity(
            name="gold", cost=50, offering_rate=(0, 0, 0, 100, 100), counts={ANY: 2}
        )
        exp = Expansion(name="Test", variants=["Pikachu", ANY], rarities=(r1, r2))
        result = exp.open_regular("Pikachu")
        assert len(result) == 5

        for item in result[:3]:
            assert item[0] == "diamond"
            assert item[1][0] in ("Pikachu", ANY)
            assert item[1][1] in range(5)

        for item in result[3:]:
            assert item[0] == "gold"
            assert item[1][0] in (ANY)
            assert item[1][1] in range(2)

    def test_open_regular_with_offering_doesnt_total_100(self):
        r1 = Rarity(
            name="diamond",
            cost=70,
            offering_rate=(100, 100, 100, 33, 33),
            counts={ANY: 5},
        )
        r2 = Rarity(
            name="gold", cost=50, offering_rate=(0, 0, 0, 66, 66), counts={ANY: 2}
        )
        exp = Expansion(name="Test", variants=[ANY], rarities=(r1, r2))
        result = exp.open_regular(ANY)
        assert len(result) == 5

        for item in result[:3]:
            assert item[0] == "diamond"
            assert item[1][0] == ANY
            assert item[1][1] in range(5)

        for item in result[3:]:
            assert item[0] in ("gold", "diamond")
            assert item[1][0] == ANY
            assert item[1][1] in range(5)
