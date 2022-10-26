import typing
from copy import deepcopy
from enum import Enum


def empty_the_select_value(
    dictionary: dict,
    select_value: typing.Any = None,
    non_destructive: bool = True,
    recursive: bool = True
) -> dict:
    def process(dict_: dict, key: typing.Any) -> None:
        del dict_[key]
    return _process_by_comparison_expression(
        dictionary,
        lambda dict_, key: dict_[key] == select_value,
        process,
        non_destructive=non_destructive,
        recursive=recursive,
    )


def rename_now_key_to_new_key(
    dictionary: dict,
    now_key: typing.Any,
    new_key: typing.Any,
    non_destructive: bool = True,
    recursive: bool = True
) -> dict:
    def process(dict_: dict, key: typing.Any) -> None:
        dict_[new_key] = dict_.pop(key)
    return _process_by_comparison_expression(
        dictionary,
        lambda _, key: key == now_key,
        process,
        non_destructive=non_destructive,
        recursive=recursive,
    )


def enum_to_value(
    dictionary: dict,
    non_destructive: bool = True,
    recursive: bool = True
) -> dict:
    def process(dict_: dict, key: typing.Any) -> None:
        dict_[key] = dict_[key].value
    return _process_by_comparison_expression(
        dictionary,
        lambda dict_, key: isinstance(dict_[key], Enum),
        process,
        non_destructive=non_destructive,
        recursive=recursive,
    )


def _process_by_comparison_expression(
    dictionary: dict,
    comparison_expression: typing.Callable[[dict, str], bool],
    process: typing.Callable[[dict, str], None],
    non_destructive: bool = True,
    recursive: bool = True
) -> dict:
    if non_destructive:
        dict_ = deepcopy(dictionary)
    else:
        dict_ = dictionary
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
