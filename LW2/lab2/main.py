from analyzer import Analyzer
from tabulate import tabulate

errors = {'missing': [], 'extra': []}


def balance_check(code):

    double_quotes_count = 0
    single_quotes_count = 0
    parentheses_count = 0
    curly_braces_count = 0
    comment_open_count = 0
    comment_close_count = 0

    in_string = False
    in_comment = False

    i = 0
    while i < len(code):
        char = code[i]

        if char == '"' and not in_comment:
            double_quotes_count += 1
            in_string = not in_string
        elif char == "'" and not in_comment:
            single_quotes_count += 1
            in_string = not in_string
        elif char == '(' and not in_comment and not in_string:
            parentheses_count += 1
        elif char == ')' and not in_comment and not in_string:
            parentheses_count -= 1
        elif char == '{' and not in_comment and not in_string:
            curly_braces_count += 1
        elif char == '}' and not in_comment and not in_string:
            curly_braces_count -= 1
        elif char == '/' and i < len(code) - 1 and code[i + 1] == '*' and not in_string:
            comment_open_count += 1
            in_comment = True
            i += 1
        elif char == '*' and i < len(code) - 1 and code[i + 1] == '/' and in_comment and not in_string:
            comment_close_count += 1
            in_comment = False
            i += 1

        i += 1

    if (double_quotes_count % 2 == 0 and
            single_quotes_count % 2 == 0 and
            parentheses_count == 0 and
            curly_braces_count == 0 and
            comment_open_count == comment_close_count):
        return True, errors
    else:
        if double_quotes_count % 2 != 0:
            errors['missing'].append('"')
        if single_quotes_count % 2 != 0:
            errors['missing'].append("'")
        if parentheses_count != 0:
            errors['missing'].append(')')
        if curly_braces_count != 0:
            errors['missing'].append('}')
        if comment_open_count != comment_close_count:
            errors['missing'].append('*/' if comment_open_count < comment_close_count else '/*')

        return False


if __name__ == '__main__':
    with open('input.cpp', 'r', encoding='utf-8') as file:
        code = file.read()

    balance_errors = balance_check(code)
    if not balance_errors:
        errors_message = ", ".join([f"Missing {error}" for error in errors['missing']])
        errors_message += ", " if errors_message and errors['extra'] else ""
        errors_message += ", ".join([f"Extra {error}" for error in errors['extra']])
        print(f"SYNTAX ERROR! {errors_message}")
    else:
        result = Analyzer.analyze(code)

        headers = ['Number', 'Category', 'Value']

        with open("output.txt", "w", encoding='utf-8') as output_file:
            import sys
            sys.stdout = output_file

            print(tabulate(list(result), headers=headers))

            sys.stdout = sys.__stdout__
