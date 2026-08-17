"""Grader for ex01_dunder."""

import pytest

from modules.m03_data_model.exercises.ex01_dunder import Inventory, Money


class TestMoneyConstruction:
    def test_defaults_to_usd(self) -> None:
        assert Money(100).currency == "USD"

    def test_currency_is_uppercased(self) -> None:
        assert Money(100, "eur").currency == "EUR"

    @pytest.mark.parametrize("bad", ["US", "USDD", "", "U$D", "12A", "  "])
    def test_invalid_currency_raises(self, bad: str) -> None:
        with pytest.raises(ValueError):
            Money(100, bad)

    def test_error_message_names_the_value(self) -> None:
        with pytest.raises(ValueError, match="GBPP"):
            Money(1, "GBPP")

    def test_negative_amounts_are_allowed(self) -> None:
        assert Money(-500).amount == -500


class TestMoneyDisplay:
    def test_repr_round_trips(self) -> None:
        assert repr(Money(1050, "eur")) == "Money(1050, 'EUR')"

    def test_str_is_human_readable(self) -> None:
        assert str(Money(1050)) == "10.50 USD"

    def test_str_pads_decimals(self) -> None:
        assert str(Money(5, "GBP")) == "0.05 GBP"

    def test_str_handles_negatives(self) -> None:
        assert str(Money(-1050)) == "-10.50 USD"

    def test_containers_use_repr(self) -> None:
        assert str([Money(1)]) == "[Money(1, 'USD')]"


class TestMoneyEquality:
    def test_equal_when_amount_and_currency_match(self) -> None:
        assert Money(100) == Money(100, "USD")

    def test_differing_currency_is_not_equal(self) -> None:
        assert Money(100, "USD") != Money(100, "EUR")

    def test_comparison_with_other_types_is_false_not_an_error(self) -> None:
        assert Money(100) != "100"
        assert (Money(100) == 100) is False

    def test_hash_agrees_with_eq(self) -> None:
        assert hash(Money(100)) == hash(Money(100, "usd"))

    def test_usable_in_sets_and_dicts(self) -> None:
        assert len({Money(100), Money(100), Money(200)}) == 2
        assert {Money(1): "one"}[Money(1)] == "one"


class TestMoneyOrdering:
    def test_less_than(self) -> None:
        assert Money(100) < Money(200)

    def test_total_ordering_derives_the_rest(self) -> None:
        assert Money(100) <= Money(100)
        assert Money(200) > Money(100)
        assert Money(200) >= Money(200)

    def test_sorting(self) -> None:
        coins = [Money(300), Money(100), Money(200)]
        assert [m.amount for m in sorted(coins)] == [100, 200, 300]
        assert max(coins) == Money(300)

    def test_mixed_currency_comparison_raises(self) -> None:
        with pytest.raises(TypeError):
            _ = Money(100, "USD") < Money(100, "EUR")

    def test_comparison_with_non_money_raises_type_error(self) -> None:
        """Returning NotImplemented lets PYTHON raise, with a message naming both types."""
        with pytest.raises(TypeError):
            _ = Money(100) < 100


class TestMoneyArithmetic:
    def test_add(self) -> None:
        assert Money(500) + Money(250) == Money(750)

    def test_sub(self) -> None:
        assert Money(500) - Money(750) == Money(-250)

    def test_add_preserves_currency(self) -> None:
        assert (Money(1, "EUR") + Money(1, "EUR")).currency == "EUR"

    def test_add_returns_a_new_object(self) -> None:
        original = Money(500)
        result = original + Money(1)
        assert original.amount == 500
        assert result is not original

    @pytest.mark.parametrize("op", ["add", "sub"])
    def test_currency_mismatch_raises(self, op: str) -> None:
        left, right = Money(100, "USD"), Money(100, "EUR")
        with pytest.raises(TypeError):
            left + right if op == "add" else left - right

    def test_adding_a_number_raises_type_error(self) -> None:
        with pytest.raises(TypeError):
            _ = Money(100) + 5

    def test_multiply_by_int(self) -> None:
        assert Money(250) * 4 == Money(1000)

    def test_reflected_multiply(self) -> None:
        assert 4 * Money(250) == Money(1000)

    def test_multiply_by_bool_is_rejected(self) -> None:
        """bool is a subclass of int — it must still be refused."""
        with pytest.raises(TypeError):
            _ = Money(100) * True

    def test_multiply_by_float_is_rejected(self) -> None:
        with pytest.raises(TypeError):
            _ = Money(100) * 1.5

    def test_negation_and_abs(self) -> None:
        assert -Money(100) == Money(-100)
        assert abs(Money(-100)) == Money(100)
        assert abs(Money(100)) == Money(100)

    def test_truthiness(self) -> None:
        assert bool(Money(1)) is True
        assert bool(Money(-1)) is True
        assert bool(Money(0)) is False
        assert bool(Money(0, "EUR")) is False


class TestInventoryConstruction:
    def test_empty_by_default(self) -> None:
        assert len(Inventory()) == 0

    def test_from_mapping(self) -> None:
        assert Inventory({"apple": 3})["apple"] == 3

    def test_negative_starting_quantity_raises(self) -> None:
        with pytest.raises(ValueError):
            Inventory({"apple": -1})

    def test_does_not_alias_the_caller_mapping(self) -> None:
        source = {"apple": 3}
        inv = Inventory(source)
        source["banana"] = 9
        assert "banana" not in inv

    def test_repr(self) -> None:
        assert repr(Inventory({"apple": 3})) == "Inventory({'apple': 3})"

    def test_empty_repr(self) -> None:
        assert repr(Inventory()) == "Inventory({})"


class TestInventoryContainerProtocol:
    def test_len_counts_distinct_items(self) -> None:
        assert len(Inventory({"apple": 3, "pear": 10})) == 2

    def test_getitem(self) -> None:
        assert Inventory({"apple": 3})["apple"] == 3

    def test_getitem_missing_raises_key_error(self) -> None:
        with pytest.raises(KeyError):
            _ = Inventory()["nope"]

    def test_setitem_adds_and_updates(self) -> None:
        inv = Inventory()
        inv["apple"] = 3
        inv["apple"] = 5
        assert inv["apple"] == 5
        assert len(inv) == 1

    def test_setitem_zero_removes(self) -> None:
        inv = Inventory({"apple": 3, "pear": 1})
        inv["apple"] = 0
        assert "apple" not in inv
        assert len(inv) == 1

    def test_setitem_zero_on_missing_item_is_a_noop(self) -> None:
        inv = Inventory()
        inv["ghost"] = 0
        assert len(inv) == 0

    def test_setitem_negative_raises(self) -> None:
        inv = Inventory()
        with pytest.raises(ValueError):
            inv["apple"] = -1

    def test_delitem(self) -> None:
        inv = Inventory({"apple": 3})
        del inv["apple"]
        assert len(inv) == 0

    def test_delitem_missing_raises(self) -> None:
        with pytest.raises(KeyError):
            del Inventory()["nope"]

    def test_contains(self) -> None:
        inv = Inventory({"apple": 3})
        assert "apple" in inv
        assert "pear" not in inv

    def test_iterates_names_in_insertion_order(self) -> None:
        inv = Inventory({"zebra": 1, "apple": 2})
        assert list(inv) == ["zebra", "apple"]

    def test_is_reusable_not_a_one_shot_iterator(self) -> None:
        inv = Inventory({"a": 1, "b": 2})
        assert list(inv) == ["a", "b"]
        assert list(inv) == ["a", "b"]

    def test_truthiness_from_len(self) -> None:
        assert bool(Inventory({"a": 1})) is True
        assert bool(Inventory()) is False

    def test_free_behaviour_from_iter(self) -> None:
        inv = Inventory({"zebra": 1, "apple": 2})
        assert sorted(inv) == ["apple", "zebra"]
        assert max(inv, key=len) == "zebra"
        assert [name.upper() for name in inv] == ["ZEBRA", "APPLE"]


class TestInventoryEqualityAndTotal:
    def test_equal_regardless_of_order(self) -> None:
        assert Inventory({"a": 1, "b": 2}) == Inventory({"b": 2, "a": 1})

    def test_not_equal_on_different_quantities(self) -> None:
        assert Inventory({"a": 1}) != Inventory({"a": 2})

    def test_comparison_with_other_types(self) -> None:
        assert Inventory({"a": 1}) != {"a": 1}

    def test_total(self) -> None:
        assert Inventory({"a": 1, "b": 2, "c": 3}).total() == 6

    def test_total_empty(self) -> None:
        assert Inventory().total() == 0
