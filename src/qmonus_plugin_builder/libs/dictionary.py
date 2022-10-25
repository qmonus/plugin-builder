import typing
from copy import deepcopy


def empty_the_select_value(
    dictionaly: dict,
    select_value: typing.Any = None,
    non_destructive: bool = True,
    recursive: bool = True
) -> dict:
    def process(dict_: dict, key: typing.Any) -> None:
        del dict_[key]
    return _process_by_comparison_expression(
        dictionaly,
        lambda dict_, key: dict_[key] == select_value,
        process,
        non_destructive=non_destructive,
        recursive=recursive,
    )


def rename_now_key_to_new_key(
    dictionaly: dict,
    now_key: typing.Any,
    new_key: typing.Any,
    non_destructive: bool = True,
    recursive: bool = True
) -> dict:
    def process(dict_: dict, key: typing.Any) -> None:
        dict_[new_key] = dict_.pop(key)
    return _process_by_comparison_expression(
        dictionaly,
        lambda _, key: key == now_key,
        process,
        non_destructive=non_destructive,
        recursive=recursive,
    )


def _process_by_comparison_expression(
    dictionaly: dict,
    comparison_expression: typing.Callable[[dict, str], None],
    process: typing.Callable[[dict, str], bool],
    non_destructive: bool = True,
    recursive: bool = True
) -> dict:
    if non_destructive:
        dict_ = deepcopy(dictionaly)
    else:
        dict_ = dictionaly
    process_keys = []
    for key in dict_.keys():
        if comparison_expression(dict_, key):
            process_keys.append(key)
        elif recursive:
            if isinstance(dict_.get(key), dict):
                _process_by_comparison_expression(
                    dict_.get(key), process=process, comparison_expression=comparison_expression, non_destructive=False, recursive=recursive
                )
            elif isinstance(dict_.get(key), list):
                for value in dict_.get(key):
                    if isinstance(value, dict):
                        _process_by_comparison_expression(
                            value, process=process, comparison_expression=comparison_expression, non_destructive=False, recursive=recursive
                        )
    for process_key in process_keys:
        process(dict_, process_key)
    return dict_
