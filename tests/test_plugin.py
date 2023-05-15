from __future__ import annotations

import pytest


@pytest.fixture(autouse=True, scope="function")
def _enable_plugin(pytester: pytest.Pytester):
    pytester.makeconftest(
        """
        pytest_plugins = ["pytest_importance"]
        """
    )


def test_plugin__unknown_default(pytester: pytest.Pytester):
    """Make sure that unknown default value yields error."""
    pytester.makeini(
        """
        [pytest]
        importance_values = medium
        importance_default = high
        """
    )

    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.importance("medium")
        def test_importance():
            pass
        """
    )

    result = pytester.runpytest()
    result.stderr.re_match_lines(r".*high is not in importance_values ini option.*")


def test_plugin__unknown_value(pytester: pytest.Pytester):
    """Make sure that unknown value yields error."""
    pytester.makeini(
        """
        [pytest]
        importance_values = medium
        importance_default = medium
        """
    )

    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.importance("high")
        def test_importance():
            pass
        """
    )

    result = pytester.runpytest()
    result.stdout.re_match_lines(r".*high is not in importance_values ini option.*")


@pytest.mark.parametrize("value", ['"medium", 0', '0, "medium"', 'value="medium"', '"medium", value="high"'])
def test_plugin__invalid_arguments(pytester: pytest.Pytester, value: str):
    """Make sure that invalid argument yields error."""
    pytester.makepyfile(
        f"""
        import pytest

        @pytest.mark.importance({value})
        def test_importance():
            pass
        """
    )

    result = pytester.runpytest()
    result.stdout.re_match_lines(r".*invalid use of importance marker, use it as @pytest.mark.importance\(value\).*")


def test_plugin__invalid_type(pytester: pytest.Pytester):
    """Make sure that invalid argument type yields error."""
    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.importance(0)
        def test_importance():
            pass
        """
    )

    result = pytester.runpytest()
    result.stdout.re_match_lines(r".*importance marker expect one string argument.*")


def test_plugin__correct_value(pytester: pytest.Pytester):
    """Make sure that correct value does not yield error."""
    pytester.makeini(
        """
        [pytest]
        importance_values = medium
        importance_default = medium
        """
    )

    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.importance("medium")
        def test_importance():
            pass

        def test_default():
            pass
        """
    )

    result = pytester.runpytest()
    result.assert_outcomes(passed=2)


def test_plugin__filter(pytester: pytest.Pytester):
    """Make sure that filter works correctly."""

    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.importance("low")
        def test_1():
            pass

        @pytest.mark.importance("medium")
        def test_2():
            pass

        @pytest.mark.importance("high")
        def test_3():
            pass

        def test_4():
            pass
        """
    )

    result = pytester.runpytest("-vvv")
    result.assert_outcomes(passed=4)
    result.stdout.re_match_lines(r".*test_1 +PASSED")
    result.stdout.re_match_lines(r".*test_2 +PASSED")
    result.stdout.re_match_lines(r".*test_3 +PASSED")
    result.stdout.re_match_lines(r".*test_4 +PASSED")

    result = pytester.runpytest("-vvv", "--importance=low")
    result.assert_outcomes(passed=1, deselected=3)
    result.stdout.re_match_lines(r".*test_1 +PASSED")
    result.stdout.no_re_match_line(r".*test_2 +PASSED")
    result.stdout.no_re_match_line(r".*test_3 +PASSED")
    result.stdout.no_re_match_line(r".*test_4 +PASSED")

    result = pytester.runpytest("-vvv", "--importance=medium")
    result.assert_outcomes(passed=2, deselected=2)
    result.stdout.no_re_match_line(r".*test_1 +PASSED")
    result.stdout.re_match_lines(r".*test_2 +PASSED")
    result.stdout.no_re_match_line(r".*test_3 +PASSED")
    result.stdout.re_match_lines(r".*test_4 +PASSED")

    result = pytester.runpytest("-vvv", "--importance=high")
    result.assert_outcomes(passed=1, deselected=3)
    result.stdout.no_re_match_line(r".*test_1 +PASSED")
    result.stdout.no_re_match_line(r".*test_2 +PASSED")
    result.stdout.re_match_lines(r".*test_3 +PASSED")
    result.stdout.no_re_match_line(r".*test_4 +PASSED")

    result = pytester.runpytest("-vvv", "--importance=critical")
    result.assert_outcomes(passed=0, deselected=4)
    result.stdout.no_re_match_line(r".*test_1 +PASSED")
    result.stdout.no_re_match_line(r".*test_2 +PASSED")
    result.stdout.no_re_match_line(r".*test_3 +PASSED")
    result.stdout.no_re_match_line(r".*test_4 +PASSED")

    result = pytester.runpytest("-vvv", "--importance=medium", "--importance=low")
    result.assert_outcomes(passed=3, deselected=1)
    result.stdout.re_match_lines(r".*test_1 +PASSED")
    result.stdout.re_match_lines(r".*test_2 +PASSED")
    result.stdout.no_re_match_line(r".*test_3 +PASSED")
    result.stdout.re_match_lines(r".*test_4 +PASSED")


def test_plugin__filter_class(pytester: pytest.Pytester):
    """Make sure that filter works correctly with class."""
    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.importance("low")
        class TestImportance(object):
            def test_1(self):
                pass

            @pytest.mark.importance("medium")
            def test_2(self):
                pass

            @pytest.mark.importance("high")
            def test_3(self):
                pass

            def test_4(self):
                pass
        """
    )

    result = pytester.runpytest("-vvv")
    result.assert_outcomes(passed=4)
    result.stdout.re_match_lines(r".*test_1 +PASSED")
    result.stdout.re_match_lines(r".*test_2 +PASSED")
    result.stdout.re_match_lines(r".*test_3 +PASSED")
    result.stdout.re_match_lines(r".*test_4 +PASSED")

    result = pytester.runpytest("-vvv", "--importance=low")
    result.assert_outcomes(passed=2, deselected=2)
    result.stdout.re_match_lines(r".*test_1 +PASSED")
    result.stdout.no_re_match_line(r".*test_2 +PASSED")
    result.stdout.no_re_match_line(r".*test_3 +PASSED")
    result.stdout.re_match_lines(r".*test_4 +PASSED")

    result = pytester.runpytest("-vvv", "--importance=medium")
    result.assert_outcomes(passed=1, deselected=3)
    result.stdout.no_re_match_line(r".*test_1 +PASSED")
    result.stdout.re_match_lines(r".*test_2 +PASSED")
    result.stdout.no_re_match_line(r".*test_3 +PASSED")
    result.stdout.no_re_match_line(r".*test_4 +PASSED")

    result = pytester.runpytest("-vvv", "--importance=high")
    result.assert_outcomes(passed=1, deselected=3)
    result.stdout.no_re_match_line(r".*test_1 +PASSED")
    result.stdout.no_re_match_line(r".*test_2 +PASSED")
    result.stdout.re_match_lines(r".*test_3 +PASSED")
    result.stdout.no_re_match_line(r".*test_4 +PASSED")

    result = pytester.runpytest("-vvv", "--importance=critical")
    result.assert_outcomes(passed=0, deselected=4)
    result.stdout.no_re_match_line(r".*test_1 +PASSED")
    result.stdout.no_re_match_line(r".*test_2 +PASSED")
    result.stdout.no_re_match_line(r".*test_3 +PASSED")
    result.stdout.no_re_match_line(r".*test_4 +PASSED")

    result = pytester.runpytest("-vvv", "--importance=medium", "--importance=low")
    result.assert_outcomes(passed=3, deselected=1)
    result.stdout.re_match_lines(r".*test_1 +PASSED")
    result.stdout.re_match_lines(r".*test_2 +PASSED")
    result.stdout.no_re_match_line(r".*test_3 +PASSED")
    result.stdout.re_match_lines(r".*test_4 +PASSED")


def test_plugin__filter_custom(pytester: pytest.Pytester):
    """Make sure that filter works correctly."""
    pytester.makeini(
        """
        [pytest]
        importance_values = 1, 2, 3, 4
        importance_default = 2
        """
    )

    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.importance("1")
        def test_1():
            pass

        @pytest.mark.importance("2")
        def test_2():
            pass

        @pytest.mark.importance("3")
        def test_3():
            pass

        def test_4():
            pass
        """
    )

    result = pytester.runpytest("-vvv")
    result.assert_outcomes(passed=4)
    result.stdout.re_match_lines(r".*test_1 +PASSED")
    result.stdout.re_match_lines(r".*test_2 +PASSED")
    result.stdout.re_match_lines(r".*test_3 +PASSED")
    result.stdout.re_match_lines(r".*test_4 +PASSED")

    result = pytester.runpytest("-vvv", "--importance=1")
    result.assert_outcomes(passed=1, deselected=3)
    result.stdout.re_match_lines(r".*test_1 +PASSED")
    result.stdout.no_re_match_line(r".*test_2 +PASSED")
    result.stdout.no_re_match_line(r".*test_3 +PASSED")
    result.stdout.no_re_match_line(r".*test_4 +PASSED")

    result = pytester.runpytest("-vvv", "--importance=2")
    result.assert_outcomes(passed=2, deselected=2)
    result.stdout.no_re_match_line(r".*test_1 +PASSED")
    result.stdout.re_match_lines(r".*test_2 +PASSED")
    result.stdout.no_re_match_line(r".*test_3 +PASSED")
    result.stdout.re_match_lines(r".*test_4 +PASSED")

    result = pytester.runpytest("-vvv", "--importance=3")
    result.assert_outcomes(passed=1, deselected=3)
    result.stdout.no_re_match_line(r".*test_1 +PASSED")
    result.stdout.no_re_match_line(r".*test_2 +PASSED")
    result.stdout.re_match_lines(r".*test_3 +PASSED")
    result.stdout.no_re_match_line(r".*test_4 +PASSED")

    result = pytester.runpytest("-vvv", "--importance=4")
    result.assert_outcomes(passed=0, deselected=4)
    result.stdout.no_re_match_line(r".*test_1 +PASSED")
    result.stdout.no_re_match_line(r".*test_2 +PASSED")
    result.stdout.no_re_match_line(r".*test_3 +PASSED")
    result.stdout.no_re_match_line(r".*test_4 +PASSED")

    result = pytester.runpytest("-vvv", "--importance=2", "--importance=1")
    result.assert_outcomes(passed=3, deselected=1)
    result.stdout.re_match_lines(r".*test_1 +PASSED")
    result.stdout.re_match_lines(r".*test_2 +PASSED")
    result.stdout.no_re_match_line(r".*test_3 +PASSED")
    result.stdout.re_match_lines(r".*test_4 +PASSED")
