import typing
import tokenize
import inspect
import io


def outdent(
    code: str,
    size: typing.Optional[int] = None,
) -> str:
    lines = code.split('\n')
    if size is None:
        size = inspect.indentsize(lines[0])

    new_lines: typing.List[str] = []
    for line in lines:
        _indent_size = inspect.indentsize(line)
        if _indent_size < size:
            offset = _indent_size
        else:
            offset = size
        new_lines.append(line[offset:])

    new_code = '\n'.join(new_lines)
    return new_code


def get_function_code(func: typing.Callable[..., typing.Any]) -> str:
    code = inspect.getsource(func)
    lines = code.split('\n')
    tokens = tokenize.generate_tokens(io.StringIO(code).readline)
    last_func_def_token = None
    count = 0
    for token in tokens:
        # print(token.string, token.start, token.end, tokenize.tok_name[token.type], tokenize.tok_name[token.exact_type])
        if token.type == tokenize.OP and token.string == '(':
            count = count + 1
        elif token.type == tokenize.OP and token.string == ')':
            count = count - 1
        elif token.type == tokenize.OP and token.string == ':' and count == 0:
            last_func_def_token = token
            break
    if last_func_def_token is None:
        raise ValueError(f"Invalid function code: '{code}'")

    first_func_code_token = next(tokens)
    if first_func_code_token.type == tokenize.NEWLINE:
        func_lines = lines[first_func_code_token.start[0]:]
        func_indent = None
        for token in tokens:
            if token.type == tokenize.INDENT:
                func_indent = token.end[1]
                break
        if func_indent is None:
            raise ValueError(f"Invalid function code: '{code}'")
        func_code = outdent(code='\n'.join(func_lines), size=func_indent)
    elif first_func_code_token.type == tokenize.COMMENT:
        func_lines = lines[first_func_code_token.start[0] - 1:]
        func_indent = None
        for token in tokens:
            if token.type == tokenize.INDENT:
                func_indent = token.end[1]
                break
        if func_indent is None:
            raise ValueError(f"Invalid function code: '{code}'")

        func_lines[0] = ' ' * func_indent + func_lines[0][first_func_code_token.start[1]:]
        func_code = outdent(code='\n'.join(func_lines))
    else:
        # one line case
        func_lines = lines[first_func_code_token.start[0] - 1:]
        func_lines[0] = ' ' * first_func_code_token.start[1] + func_lines[0][first_func_code_token.start[1]:]
        func_code = outdent(code='\n'.join(func_lines))

    return func_code
