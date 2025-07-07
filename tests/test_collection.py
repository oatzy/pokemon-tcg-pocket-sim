import pytest

from pokemon_tcg_simulate.collection import (Collection,
                                             MissionRarityCollection,
                                             RarityCollection, Variant)
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


class TestRarityCollection:
    @pytest.mark.parametrize("state", [3, {ANY: 3}])
    def test_load_state_no_variants(self, state):
        rarity = diamond(5)

        c = RarityCollection(rarity=rarity)
        c.load_initial_state(state)

        assert list(c.collected.keys()) == [ANY]
        assert c.collected[ANY].collection == [1, 1, 1, 0, 0]

    @pytest.mark.parametrize("state", [[2, 1], {ANY: [2, 1]}])
    def test_load_state_no_variants_with_counts(self, state):
        rarity = diamond(5)

        c = RarityCollection(rarity=rarity)
        c.load_initial_state(state)

        assert list(c.collected.keys()) == [ANY]
        assert c.collected[ANY].collection == [2, 1, 0, 0, 0]

    def test_load_state_with_variants(self):
        rarity = diamond({"Charizard": 5, "Pikachu": 5})

        c = RarityCollection(rarity=rarity)
        c.load_initial_state({"Charizard": 1, "Pikachu": 1})

        assert list(c.collected.keys()) == ["Charizard", "Pikachu"]
        assert c.collected["Charizard"].collection == [1, 0, 0, 0, 0]
        assert c.collected["Pikachu"].collection == [1, 0, 0, 0, 0]

    def test_load_state_with_variant_counts(self):
        rarity = diamond({ANY: 5, "Charizard": 5, "Pikachu": 5})

        c = RarityCollection(rarity=rarity)
        c.load_initial_state({ANY: 1, "Charizard": [1, 1], "Pikachu": [2, 1]})

        assert list(c.collected.keys()) == [ANY, "Charizard", "Pikachu"]
        assert c.collected[ANY].collection == [1, 0, 0, 0, 0]
        assert c.collected["Charizard"].collection == [1, 1, 0, 0, 0]
        assert c.collected["Pikachu"].collection == [2, 1, 0, 0, 0]

    def test_add(self):
        rarity = diamond(3)
        c = RarityCollection(rarity=rarity)
        c.add((ANY, 1), opened=1)

        assert c.collected[ANY].collection == [0, 1, 0]
        assert c.collected[ANY].unique == 1
        assert c.collected[ANY].total == 1

    def test_add_crown(self):
        # Simulate crown card logic: only ANY in rarity.counts, but add with a variant
        crown = Rarity(
            name="crown",
            cost=2500,
            offering_rate=(100, 100, 100, 100, 100),
            counts={ANY: 2},
            rare_counts={"Charizard": 1, "Pikachu": 1},
        )

        c = RarityCollection(rarity=crown)
        c.add(("Pikachu", 0), opened=1)
        # Should have added to ANY
        assert c.collected[ANY].collection == [0, 1]

    def test_add_completed(self):
        rarity = diamond(2)
        c = RarityCollection(rarity=rarity)
        c.add((ANY, 0), opened=1)
        assert c.completed_at is None
        c.add((ANY, 1), opened=2)
        assert c.completed_at == 2

    def test_buy(self):
        rarity = diamond(2)
        c = RarityCollection(rarity=rarity)
        c.buy((ANY, 0), opened=1)
        assert c.collected[ANY].collection == [1, 0]
        assert c.bought == [(ANY, 0)]

    def test_count_all(self):
        rarity = diamond({ANY: 2, "Charizard": 2, "Pikachu": 2})
        c = RarityCollection(rarity=rarity)
        c.add(("Charizard", 0), opened=1)
        c.add(("Pikachu", 1), opened=2)
        c.add((ANY, 0), opened=3)
        assert c.count() == 3

    def test_count_variant(self):
        rarity = diamond({ANY: 2, "A": 2, "B": 2})
        c = RarityCollection(rarity=rarity)

        c.add(("A", 0), opened=1)
        c.add(("B", 1), opened=2)
        assert c.count("A") == 1

        c.add((ANY, 0), opened=3)
        assert c.count("A") == 2
        assert c.count("B") == 2

    def test_count_any(self):
        rarity = diamond({ANY: 2})
        c = RarityCollection(rarity=rarity)
        c.add((ANY, 0), opened=1)
        c.add((ANY, 1), opened=2)
        assert c.count(ANY) == 2

    def test_count_with_duplicates(self):
        rarity = diamond(3)
        c = RarityCollection(rarity=rarity)
        c.add((ANY, 0), opened=1)
        c.add((ANY, 0), opened=2)
        assert c.count() == 1

    def test_iter_missing(self):
        rarity = diamond(3)
        c = RarityCollection(rarity=rarity)
        c.add((ANY, 0), opened=1)
        missing = list(c.iter_missing())
        assert missing == [(ANY, 1), (ANY, 2)]

    def test_remaining_all(self):
        rarity = diamond(3)
        c = RarityCollection(rarity=rarity)
        c.add((ANY, 0), opened=1)
        assert c.remaining() == 2
        assert c.remaining_cost() == 2 * 70

    def test_remaining_variant(self):
        rarity = diamond({"A": 2, "B": 2})
        c = RarityCollection(rarity=rarity)
        c.add(("A", 0), opened=1)
        assert c.remaining("A") == 1
        assert c.remaining("B") == 2


class TestMissionRarityCollection:
    @pytest.mark.parametrize("mission", [2, {ANY: 2}])
    def test_post_init_integer_count(self, mission):
        rarity = diamond(3)
        mc = MissionRarityCollection(rarity=rarity, mission=mission)
        assert mc.mission[ANY] == [1, 1]

    @pytest.mark.parametrize("mission", [[2, 1], {ANY: [2, 1]}])
    def test_post_init_list_counts(self, mission):
        rarity = diamond(3)
        mc = MissionRarityCollection(rarity=rarity, mission=mission)
        assert mc.mission[ANY] == [2, 1]

    def test_count_all(self):
        rarity = diamond(3)
        mission = {ANY: [1, 1]}
        mc = MissionRarityCollection(rarity=rarity, mission=mission)
        mc.collected[ANY].add(0)
        mc.collected[ANY].add(2)
        assert mc.count() == 2

    def test_count_variant(self):
        rarity = diamond({ANY: 2, "A": 2, "B": 2})
        mission = {"A": [1, 1], "B": [1, 1]}
        mc = MissionRarityCollection(rarity=rarity, mission=mission)
        mc.collected["A"].add(0)
        assert mc.count("A") == 1
        assert mc.count("B") == 0

        mc.collected[ANY].add(0)
        assert mc.count("A") == 2
        assert mc.count("B") == 1

    def test_count_any(self):
        rarity = diamond({ANY: 2, "A": 2})
        mission = {ANY: [1, 1], "A": [1, 1]}
        mc = MissionRarityCollection(rarity=rarity, mission=mission)
        mc.collected[ANY].add(0)
        assert mc.count(ANY) == 1

    def test_count_with_duplicates(self):
        rarity = diamond(2)
        mission = {ANY: [2, 1]}
        mc = MissionRarityCollection(rarity=rarity, mission=mission)
        mc.collected[ANY].add(0)
        mc.collected[ANY].add(0)
        assert mc.count() == 1

    def test_iter_missing_all(self):
        rarity = diamond({"A": 2, "B": 2})
        mission = {"A": [1, 1], "B": [1, 1]}
        mc = MissionRarityCollection(rarity=rarity, mission=mission)
        mc.collected["A"].add(1)
        missing = list(mc.iter_missing())
        assert missing == [("A", 0), ("B", 0), ("B", 1)]

    def test_iter_missing_variant(self):
        rarity = diamond({"A": 2, "B": 2})
        mission = {"A": [1, 1], "B": [1, 1]}
        mc = MissionRarityCollection(rarity=rarity, mission=mission)
        mc.collected["A"].add(0)
        missing = list(mc.iter_missing("A"))
        assert missing == [("A", 1)]

    def test_iter_missing_any(self):
        rarity = diamond(3)
        mission = {ANY: [1, 2, 1]}
        mc = MissionRarityCollection(rarity=rarity, mission=mission)
        mc.collected[ANY].add(1)
        missing = list(mc.iter_missing())
        assert missing == [(ANY, 0), (ANY, 1), (ANY, 2)]

    def test_remaining_all(self):
        rarity = diamond({ANY: 2, "A": 2, "B": 2})
        mission = {ANY: [1], "A": [1, 2]}
        mc = MissionRarityCollection(rarity=rarity, mission=mission)
        mc.collected["A"].add(1)
        mc.collected["B"].add(0)  # doesn't contribute to mission
        assert mc.remaining() == 3
        assert mc.remaining_cost() == 3 * 70

    def test_remaining_variant(self):
        rarity = diamond({"A": 2, "B": 2})
        mission = {"A": [1, 1], "B": [1, 1]}
        mc = MissionRarityCollection(rarity=rarity, mission=mission)
        mc.collected["A"].add(0)
        assert mc.remaining("A") == 1
        assert mc.remaining("B") == 2

    def test_remaining_any(self):
        rarity = diamond({ANY: 2, "A": 2})
        mission = {ANY: [1, 1], "A": [1, 1]}
        mc = MissionRarityCollection(rarity=rarity, mission=mission)
        mc.collected[ANY].add(0)
        assert mc.remaining(ANY) == 1


class TestCollection:
    def test_add(self):
        rarity = diamond(3)
        c = Collection(collected={"diamond": RarityCollection(rarity=rarity)})
        c.opened = 1
        c.add([("diamond", (ANY, 1))])
        assert c.collected["diamond"].collected[ANY].collection == [0, 1, 0]

    def test_buy(self):
        rarity = diamond(3)
        c = Collection(collected={"diamond": RarityCollection(rarity=rarity)})
        c.collected["diamond"].collected[ANY].collection = [0, 1, 0]
        c.pack_points = 100
        c.buy(("diamond", (ANY, 2)))
        assert c.collected["diamond"].collected[ANY].collection == [0, 1, 1]
        assert c.collected["diamond"].bought == [(ANY, 2)]
        assert c.pack_points == 30  # 100 - 70

    def test_load_initial_state(self):
        rarity = diamond(3)
        c = Collection(collected={"diamond": RarityCollection(rarity=rarity)})
        initial_state = {"pack_points": 50, "collected": {"diamond": [2, 1]}}
        c.load_initial_state(initial_state)
        assert c.pack_points == 50
        assert c.collected["diamond"].collected[ANY].collection == [2, 1, 0]

    def test_from_json_without_mission(self):
        class DummyExpansion:
            rarities = [diamond(2)]

        expansion = DummyExpansion()
        collection = Collection.from_json(expansion)
        assert "diamond" in collection.collected
        assert isinstance(collection.collected["diamond"], RarityCollection)

    def test_from_json_with_mission(self):
        class DummyExpansion:
            rarities = [diamond(3)]

        mission = {"diamond": [1, 1]}
        expansion = DummyExpansion()
        collection = Collection.from_json(expansion, mission=mission)
        assert "diamond" in collection.collected
        assert isinstance(collection.collected["diamond"], MissionRarityCollection)
        assert collection.collected["diamond"].mission == {ANY: [1, 1]}


def diamond(counts):
    return Rarity(
        name="diamond",
        cost=70,
        offering_rate=(100, 100, 100, 0, 0),
        counts=counts,
    )
