from pokecrawler.normalizer.primitives import clean_str, to_int, to_list


class TestCleanStr:
    def test_none_returns_none(self):
        assert clean_str(None) is None

    def test_whitespace_only_returns_none(self):
        assert clean_str("   ") is None

    def test_strips_surrounding_whitespace(self):
        assert clean_str("  hello  ") == "hello"

    def test_normal_string(self):
        assert clean_str("hello") == "hello"

    def test_non_string_returns_none(self):
        assert clean_str(42) is None


class TestToInt:
    def test_digit_string(self):
        assert to_int("45") == 45

    def test_string_with_hash_prefix(self):
        assert to_int("#45") == 45

    def test_non_digit_string_returns_none(self):
        assert to_int("abc") is None

    def test_none_returns_none(self):
        assert to_int(None) is None

    def test_int_returns_none(self):
        # to_int only accepts strings
        assert to_int(45) is None

    def test_empty_string_returns_none(self):
        assert to_int("") is None


class TestToList:
    def test_list_passthrough(self):
        assert to_list(["a", "b"]) == ["a", "b"]

    def test_none_returns_empty(self):
        assert to_list(None) == []

    def test_non_list_returns_empty(self):
        assert to_list("string") == []

    def test_filters_non_strings(self):
        assert to_list(["a", 1, None, "b"]) == ["a", "b"]

    def test_drop_removes_values(self):
        assert to_list(["Grass", "Unknown", "Poison"], drop=("Unknown",)) == [
            "Grass",
            "Poison",
        ]

    def test_drop_multiple(self):
        assert to_list(["a", "b", "c"], drop=("a", "c")) == ["b"]

    def test_empty_list(self):
        assert to_list([]) == []
