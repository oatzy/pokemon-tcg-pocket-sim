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

        c = Collection(rarity=rarity)
        c.load_initial_state(state)

        assert list(c.collected.keys()) == [ANY]
        assert c.collected[ANY].collection == [1, 1, 1, 0, 0]

    @pytest.mark.parametrize("state", [[2, 1], {ANY: [2, 1]}])
    def test_load_state_no_variants_with_counts(self, state):
        rarity = diamond(5)

        c = Collection(rarity=rarity)
        c.load_initial_state(state)

        assert list(c.collected.keys()) == [ANY]
        assert c.collected[ANY].collection == [2, 1, 0, 0, 0]

    def test_load_state_with_variants(self):
        rarity = diamond({"Charizard": 5, "Pikachu": 5})

        c = Collection(rarity=rarity)
        c.load_initial_state({"Charizard": 1, "Pikachu": 1})

        assert list(c.collected.keys()) == ["Charizard", "Pikachu"]
        assert c.collected["Charizard"].collection == [1, 0, 0, 0, 0]
        assert c.collected["Pikachu"].collection == [1, 0, 0, 0, 0]

    def test_load_state_with_variant_counts(self):
        rarity = diamond({ANY: 5, "Charizard": 5, "Pikachu": 5})

        c = Collection(rarity=rarity)
        c.load_initial_state({ANY: 1, "Charizard": [1, 1], "Pikachu": [2, 1]})

        assert list(c.collected.keys()) == [ANY, "Charizard", "Pikachu"]
        assert c.collected[ANY].collection == [1, 0, 0, 0, 0]
        assert c.collected["Charizard"].collection == [1, 1, 0, 0, 0]
        assert c.collected["Pikachu"].collection == [2, 1, 0, 0, 0]

    def test_add(self):
        pass

    def test_add_crown(self):
        # rare_count behaviour for crown cards causes problems
        pass

    def test_add_completed(self):
        pass

    def test_buy(self):
        pass

    def test_count_all(self):
        pass

    def test_count_variant(self):
        pass

    def test_count_any(self):
        pass

    def test_count_with_duplicates(self):
        pass

    def test_iter_missing(self):
        pass

    def test_remaining_all(self):
        pass  # also check cost

    def test_remaining_variant(self):
        pass

    def test_remaining_any(self):
        pass


class TestMissionCollection:
    def test_post_init_integer_count(self):
        pass

    def test_post_init_list_counts(self):
        pass

    def test_count_all(self):
        pass

    def test_count_variant(self):
        pass

    def test_count_any(self):
        pass

    def test_count_with_duplicates(self):
        pass

    def test_iter_missing_all(self):
        pass

    def test_iter_missing_variant(self):
        pass

    def test_iter_missing_any(self):
        pass

    def test_remaining_all(self):
        pass  # also check cost

    def test_remaining_variant(self):
        pass

    def test_remaining_any(self):
        pass


def diamond(counts):
    return Rarity(
        name="diamond",
        cost=70,
        offering_rate=(100, 100, 100, 0, 0),
        counts=counts,
    )
