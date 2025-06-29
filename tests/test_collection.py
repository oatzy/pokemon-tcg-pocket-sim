import pytest

from pokemon_tcg_simulate.collection import Collection, Variant
from pokemon_tcg_simulate.expansion import ANY, Rarity


class TestVariant:
    def test_init(self):
        v = Variant(3)
        assert v.collection == [0, 0, 0]
        assert v.unique == 0
        assert len(v) == 0
        assert not v.completed
        assert v.total == 0

    def test_add(self):
        v = Variant(3)

        v.add(1)
        assert v.collection == [0, 1, 0]
        assert v.unique == 1
        assert len(v) == 1

        v.add(1)
        assert v.collection == [0, 2, 0]
        assert v.unique == 1
        assert len(v) == 1

    def test_add_with_count(self):
        v = Variant(3)

        v.add(1, 5)
        assert v.collection == [0, 5, 0]
        assert v.unique == 1

    def test_contains(self):
        v = Variant(3)

        assert 1 not in v

        v.add(1)

        assert 1 in v
        assert 0 not in v

    def test_get_item(self):
        v = Variant(3)

        v.add(0)
        v.add(1, 2)

        assert v[0] == 1
        assert v[1] == 2
        assert v[2] == 0

    def test_completed(self):
        v = Variant(3)

        v.add(0)
        assert not v.completed
        assert v.total == 1

        v.add(1)
        assert not v.completed
        assert v.total == 2

        v.add(1)
        assert not v.completed
        assert v.total == 3

        v.add(2)
        assert v.completed
        assert v.total == 4


class TestCollection:
    @pytest.mark.parametrize("state", [3, {ANY: 3}])
    def test_load_state_no_variants(self, state):
        rarity = diamond(5)

        c = Collection(rarity)
        c.load_initial_state(state)

        assert list(c.collected.keys()) == [ANY]
        assert c.collected[ANY].collection == [1, 1, 1, 0, 0]

    @pytest.mark.parametrize("state", [[2, 1], {ANY: [2, 1]}])
    def test_load_state_no_variants_with_counts(self, state):
        rarity = diamond(5)

        c = Collection(rarity)
        c.load_initial_state(state)

        assert list(c.collected.keys()) == [ANY]
        assert c.collected[ANY].collection == [2, 1, 0, 0, 0]

    def test_load_state_with_variants(self):
        rarity = diamond({"Charizard": 5, "Pikachu": 5})

        c = Collection(rarity)
        c.load_initial_state({"Charizard": 1, "Pikachu": 1})

        assert list(c.collected.keys()) == ["Charizard", "Pikachu"]
        assert c.collected["Charizard"].collection == [1, 0, 0, 0, 0]
        assert c.collected["Pikachu"].collection == [1, 0, 0, 0, 0]

    def test_load_state_with_variant_counts(self):
        rarity = diamond({ANY: 5, "Charizard": 5, "Pikachu": 5})

        c = Collection(rarity)
        c.load_initial_state({ANY: 1, "Charizard": [1, 1], "Pikachu": [2, 1]})

        assert list(c.collected.keys()) == [ANY, "Charizard", "Pikachu"]
        assert c.collected[ANY].collection == [1, 0, 0, 0, 0]
        assert c.collected["Charizard"].collection == [1, 1, 0, 0, 0]
        assert c.collected["Pikachu"].collection == [2, 1, 0, 0, 0]


def diamond(counts):
    return Rarity("diamond", 70, (100, 100, 100, 0, 0), counts)
