# pytest-importance

This is a `pytest` plugin that adds the ability to filter test cases by
their importance.

It adds:
* `importance_values` option to `[pytest]` section of `pytest.ini` to define
  possible importance values (defaults to `low, medium, high, critical`)
* `importance_default` option to `[pytest]` section of `pytest.ini` to define
  the default importance value if it is not set by the importance marker
  (defaults to `medium`)
* `importance_meta_name` option to `[pytest]` section of `pytest.ini` to define
  name of the meta field used in (defaults to `caseimportance`)
  [pytest-output](https://github.com/next-actions/pytest-output) plugin
* `@pytest.mark.importance` mark to set the importance of the test case
* `--important` command line option to filter out test cases that are not
  associated with selected importance(s)

## Example usage

1. Enable plugin in conftest.py

    ```python
    pytest_plugins = (
        "pytest_importance",
    )
    ```

2. Optionally, configure plugin pytest.ini

    ```ini
    [pytest]
    importance_values = low, medium, high, critical
    importance_default = medium
    importance_meta_name = caseimportance
    ```

3. Define test with importance mark

    ```python
    @pytest.mark.importance("high")
    def test_importance():
        pass
    ```

4. Run pytest with importance filter

    ```
    $ pytest --importance=high
    ```

## Importance mark

The importance mark takes one positional string argument with one of the values
configured in pytest.ini `importance_values` option.

```
@pytest.mark.importance(value: str)
```

## --importance command line option

You can filter tests using the `--importance` option, which takes the importance
value as an argument. This option can be passed multiple times.

```
pytest --importance=low --importance=medium
```
