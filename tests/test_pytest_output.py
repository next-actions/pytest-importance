from __future__ import annotations

import pytest


@pytest.fixture(autouse=True, scope="function")
def _enable_plugin(pytester: pytest.Pytester):
    pytester.makeconftest(
        """
        import pytest

        pytest_plugins = ["pytest_importance"]
        """
    )


def test_pytest_output__default(pytester: pytest.Pytester):
    """Make sure that meta field is set to default value if no marker is present."""
    pytester.makepyfile(
        """
        import pytest

        def test_importance(output_data_item):
            assert "caseimportance" in output_data_item.meta
            assert output_data_item.meta["caseimportance"] == "medium"
        """
    )

    result = pytester.runpytest()
    result.assert_outcomes(passed=1)


def test_pytest_output__set(pytester: pytest.Pytester):
    """Make sure that meta field is set if marker is present."""
    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.importance("high")
        def test_importance(output_data_item):
            assert "caseimportance" in output_data_item.meta
            assert output_data_item.meta["caseimportance"] == "high"
        """
    )

    result = pytester.runpytest()
    result.assert_outcomes(passed=1)


def test_pytest_output__class(pytester: pytest.Pytester):
    """Make sure that meta field is set if marker is added to class."""
    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.importance("high")
        class Testimportance(object):
            def test_0(self, output_data_item):
                assert "caseimportance" in output_data_item.meta
                assert output_data_item.meta["caseimportance"] == "high"

            @pytest.mark.importance("low")
            def test_1(self, output_data_item):
                assert "caseimportance" in output_data_item.meta
                assert output_data_item.meta["caseimportance"] == "low"
        """
    )

    result = pytester.runpytest()
    result.assert_outcomes(passed=2)


def test_pytest_output__custom_default(pytester: pytest.Pytester):
    """Make sure that custom meta field is set to default value if no marker is present."""
    pytester.makeini(
        """
        [pytest]
        importance_meta_name = mymeta
        """
    )

    pytester.makepyfile(
        """
        import pytest

        def test_importance(output_data_item):
            assert "mymeta" in output_data_item.meta
            assert output_data_item.meta["mymeta"] == "medium"
        """
    )

    result = pytester.runpytest()
    result.assert_outcomes(passed=1)


def test_pytest_output__custom_set(pytester: pytest.Pytester):
    """Make sure that meta field is set if marker is present."""
    pytester.makeini(
        """
        [pytest]
        importance_meta_name = mymeta
        """
    )

    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.importance("high")
        def test_importance(output_data_item):
            assert "mymeta" in output_data_item.meta
            assert output_data_item.meta["mymeta"] == "high"
        """
    )

    result = pytester.runpytest()
    result.assert_outcomes(passed=1)


def test_pytest_output__custom_class(pytester: pytest.Pytester):
    """Make sure that meta field is set if marker is added to class."""
    pytester.makeini(
        """
        [pytest]
        importance_meta_name = mymeta
        """
    )

    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.importance("high")
        class Testimportance(object):
            def test_0(self, output_data_item):
                assert "mymeta" in output_data_item.meta
                assert output_data_item.meta["mymeta"] == "high"

            @pytest.mark.importance("low")
            def test_1(self, output_data_item):
                assert "mymeta" in output_data_item.meta
                assert output_data_item.meta["mymeta"] == "low"
        """
    )

    result = pytester.runpytest()
    result.assert_outcomes(passed=2)
