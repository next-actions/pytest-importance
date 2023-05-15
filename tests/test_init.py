from __future__ import annotations

import pytest


def test_init__implicit(pytester: pytest.Pytester):
    """Make sure that the plugin is not automatically loaded."""
    pytester.makeconftest("")
    pytester.makepyfile(
        """
        def test_loaded(request):
            assert request.config.pluginmanager.getplugin("PytestImportance") is None
        """
    )

    # run all tests with pytest
    result = pytester.runpytest()
    result.assert_outcomes(passed=1)


def test_init__explicit(pytester: pytest.Pytester):
    """Make sure that the plugin can be loaded explicitly."""
    pytester.makeconftest(
        """
        pytest_plugins = ["pytest_importance"]
        """
    )
    pytester.makepyfile(
        """
        def test_loaded(request):
            assert request.config.pluginmanager.getplugin("PytestImportance") is not None
        """
    )

    # run all tests with pytest
    result = pytester.runpytest("-s")
    result.assert_outcomes(passed=1)
