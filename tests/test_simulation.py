import pytest

from pokemon_tcg_simulate import simulation
from pokemon_tcg_simulate.collection import Collection
from pokemon_tcg_simulate.expansion import Rarity, ANY


class TestPick:
    def test_pick_rarest(self):
        # Setup: 2 rarities, one with higher offering_rate
        r1 = Rarity("common", cost=1, rare=False, offering_rate=(0.5,), counts={ANY: 5})
        r2 = Rarity("rare", cost=5, rare=True, offering_rate=(0.1,), counts={ANY: 2})
        c1 = Collection(rarity=r1)
        c2 = Collection(rarity=r2)
        collection = {"common": c1, "rare": c2}
        rarity, card = simulation.pick_from_remaining(
            collection, simulation.rarest(ANY)
        )
        assert rarity == "rare"
        assert card[0] == ANY
        assert card[1] in range(2)

    def test_pick_most_expensive(self):
        r1 = Rarity(
            "rainbow", cost=5, rare=False, offering_rate=(0.5,), counts={ANY: 5}
        )
        r2 = Rarity("star", cost=1, rare=True, offering_rate=(0.1,), counts={ANY: 2})
        c1 = Collection(rarity=r1)
        c2 = Collection(rarity=r2)
        collection = {"rainbow": c1, "star": c2}
        rarity, card = simulation.pick_from_remaining(
            collection, simulation.most_expensive
        )
        assert rarity == "rainbow"
        assert card[0] == ANY
        assert card[1] in range(5)


class TestCompleted:
    def test_completed_all(self):
        r1 = Rarity("common", cost=1, rare=False, offering_rate=(0.5,), counts={ANY: 1})
        r2 = Rarity("rare", cost=5, rare=True, offering_rate=(0.1,), counts={ANY: 1})
        c1 = Collection(rarity=r1)
        c2 = Collection(rarity=r2)
        collection = {"common": c1, "rare": c2}

        c1.add((ANY, 0), opened=1)
        assert not simulation.completed_all(collection)
        c2.add((ANY, 0), opened=2)
        assert simulation.completed_all(collection)

    def test_completed_common(self):
        r1 = Rarity("common", cost=1, rare=False, offering_rate=(0.5,), counts={ANY: 1})
        r2 = Rarity("rare", cost=5, rare=True, offering_rate=(0.1,), counts={ANY: 1})
        c1 = Collection(rarity=r1)
        c2 = Collection(rarity=r2)
        collection = {"common": c1, "rare": c2}

        c2.add((ANY, 0), opened=1)
        assert not simulation.completed_common(collection)
        c1.add((ANY, 0), opened=2)
        assert simulation.completed_common(collection)

    def test_completed_variant(self):
        r1 = Rarity(
            "common",
            cost=1,
            rare=False,
            offering_rate=(0.5,),
            counts={ANY: 1, "A": 1, "B": 1},
        )
        r2 = Rarity(
            "rare",
            cost=5,
            rare=True,
            offering_rate=(0.1,),
            counts={ANY: 1, "A": 1, "B": 1},
        )

        c1 = Collection(rarity=r1)
        c1.add(("A", 0), opened=1)
        c1.add((ANY, 0), opened=2)
        c1.add(("B", 0), opened=3)

        c2 = Collection(rarity=r2)
        c2.add(("A", 0), opened=1)
        c2.add((ANY, 0), opened=2)

        collection = {"common": c1, "rare": c2}

        assert simulation.completed_variant(collection, variant="A")
        assert not simulation.completed_variant(collection, variant="B")


class TestBuy:
    def test_required_pack_points(self):
        r1 = Rarity("common", cost=3, rare=False, offering_rate=(0.5,), counts={ANY: 2})
        r2 = Rarity("rare", cost=5, rare=True, offering_rate=(0.1,), counts={ANY: 2})
        c1 = Collection(rarity=r1)
        c2 = Collection(rarity=r2)
        collection = {"common": c1, "rare": c2}
        assert simulation.required_pack_points(collection) == (3 * 2 + 2 * 5)

    def test_buy_remaining(self):
        r1 = Rarity("common", cost=3, rare=False, offering_rate=(0.5,), counts={ANY: 2})
        c1 = Collection(rarity=r1)
        collection = {"common": c1}
        remaining = simulation.buy_remaining(collection, pack_points=10, opened=5)
        assert remaining == 10 - (3 * 2)  # 6 points spent
        assert c1.bought == [(ANY, 0), (ANY, 1)]

    def test_buy_remaining_not_enough_points(self):
        r1 = Rarity("common", cost=3, rare=False, offering_rate=(0.5,), counts={ANY: 2})
        c1 = Collection(rarity=r1)
        collection = {"common": c1}
        with pytest.raises(RuntimeError):
            simulation.buy_remaining(collection, pack_points=5, opened=5)


class TestSimulate:
    @pytest.mark.skip("TODO")
    def test_simulate_basic(self, monkeypatch):
        # Patch expansion and collection
        class DummyExpansion:
            def __init__(self):
                self.rarities = [
                    Rarity("common", cost=1, rare=False),
                    Rarity("rare", cost=5, rare=True),
                ]
                self.variants = ["v1", "v2"]

            def open_rare(self, variant):
                return [("rare", "rare_card")]

            def open_regular(self, variant):
                return [("common", "common_card")]

        # Patch random.random to always return > RARE_PROBABILITY
        monkeypatch.setattr(simulation.random, "random", lambda: 1.0)

        expansion = DummyExpansion()
        result = simulation.simulate(expansion)
        assert isinstance(result, simulation.SimulationResult)
        assert result.opened > 0
