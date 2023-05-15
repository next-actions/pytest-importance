from __future__ import annotations

import pytest

ImportanceStashKey = pytest.StashKey[str]()


class ImportancePlugin(object):
    def __init__(self, config: pytest.Config) -> None:
        values = map(lambda x: x.strip(), config.getini("importance_values").split(","))

        self.values: list[str] = [x for x in values if x]
        self.default_value: str = config.getini("importance_default")
        self.metaname: str = config.getini("importance_meta_name")
        self.filter: list[str] = config.getoption("importance")

        if self.default_value not in self.values:
            raise ValueError(f"{self.default_value} is not in importance_values ini option {self.values}")

    @pytest.hookimpl(tryfirst=True)
    def pytest_collection_modifyitems(self, config: pytest.Config, items: list[pytest.Item]) -> None:
        """
        Filter collected items and deselect these that do not match the importance filter.

        :meta private:
        """
        selected = []
        deselected = []

        for item in items:
            value: str = self.default_value
            mark: pytest.Mark | None = item.get_closest_marker("importance")
            if mark is not None:
                if len(mark.args) != 1 or len(mark.kwargs) != 0:
                    raise ValueError(
                        f"{item.nodeid}: invalid use of importance marker, use it as @pytest.mark.importance(value)"
                    )

                if not isinstance(mark.args[0], str):
                    raise TypeError(f"{item.nodeid}: importance marker expect one string argument")

                value = mark.args[0]
                if value not in self.values:
                    raise ValueError(f"{item.nodeid}: {value} is not in importance_values ini option {self.values}")

            item.stash[ImportanceStashKey] = value

            if not self.filter or value in self.filter:
                selected.append(item)
            else:
                deselected.append(item)

        config.hook.pytest_deselected(items=deselected)
        items[:] = selected

    # Hook from pytest-output plugin
    @pytest.hookimpl(optionalhook=True)
    def pytest_output_item_collected(self, config: pytest.Config, item) -> None:
        try:
            from pytest_output.output import OutputDataItem
        except ImportError:
            pass

        if not isinstance(item, OutputDataItem):
            raise ValueError(f"Unexpected item type: {type(item)}")

        if ImportanceStashKey not in item.item.stash:
            return

        importance: str = item.item.stash[ImportanceStashKey]
        if importance:
            item.meta[self.metaname] = importance


def pytest_addoption(parser: pytest.Parser):
    """
    :meta private:
    """
    parser.addini(
        "importance_values",
        "Comma separated list of possible values for the importance marker",
        default="low, medium, high, critical",
    )

    parser.addini(
        "importance_default",
        "Default importance value if no marker is given",
        default="medium",
    )

    parser.addini(
        "importance_meta_name",
        "Name of pytest output metadata for importance value",
        default="caseimportance",
    )

    parser.addoption(
        "--importance",
        action="append",
        help="Filter tests by given importance, can be set multiple times",
        required=False,
        default=list(),
    )


def pytest_configure(config: pytest.Config):
    """
    :meta private:
    """

    # register additional markers
    config.addinivalue_line("markers", "importance(importance): importance of the test")

    config.pluginmanager.register(ImportancePlugin(config), name="PytestImportance")
