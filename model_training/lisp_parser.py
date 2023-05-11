from typing import *
from enum import Enum
import logging
import string


class TerminalDirective(Enum):
    # indicates party sending the transmission e.g. (FROM AAABBBB)
    FROM = "FROM"
    # indicates party receiving the transmission e.g. (TO AAABBBB)
    TO = "TO"
    # text transcription of the transmission e.g. (TEXT ...)
    TEXT = "TEXT"
    # start/end times of the transmission e.g. (TIMES start end)
    TIMES = "TIMES"
    # comment(s) from transcriber e.g. (COMMENT "...")
    COMMENT = "COMMENT"
    # metadata for the tape, also indicates that start of the tape e.g. (TAPE-HEADER "...")
    TAPE_HEADER = "TAPE-HEADER"
    # meatdata for the tape, also indicates the end of the tape e.g. (TAPE-TAIL "...")
    TAPE_TAIL = "TAPE-TAIL"
    # unspecified identifier included in some of the tapes, usualy a unique identifier
    # based on the tape name, a dash, and a number representing the transmission
    # i.e. 1 for the first transmission, 2 for the second, etc.
    TRANSMISSION_ID = "NUM"
    # an escape sequence for contractions since the ' character has special meaning in LISP (denotes a list) e.g. (TEXT WE (QUOTE LL)) -> WE'LL
    QUOTE = "QUOTE"

    def __str__(self) -> str:
        return self.value


class TerminalConstant(Enum):
    SPACE = " "
    OPEN_PAREN = "("
    CLOSE_PAREN = ")"

    def __str__(self) -> str:
        return self.value

    # these mongoloids wrote out contractions in AT LEAST 5 DIFFERENT WAYS
    # so here are special cases to normalize all of them (e.g. the contraction
    # for 'we will' ("we'll"), shows up as "we 'll", "we' ll", "we'll", "we ' ll", and "we (QUOTE ll)", wtf)
    #
    # according to the limited lexical analysis I've done on this data,
    # all 5 cases should be covered and normalized by this code


class Directive(object):
    directive: TerminalDirective
    arguments: Union[str, List[str]]

    def __init__(self, directive: str, arguments: str) -> "Directive":
        self.directive = TerminalDirective(directive)
        self.arguments = arguments

    def __repr__(self) -> str:
        return f"Directive(directive={self.directive}, arguments='{self.arguments}')"


def get_string_and_normalize(string: str) -> str:
    if string is None:
        return ""

    string = string.replace("\n", " ")
    string = string.replace("\t", " ")
    string = string.strip()

    # these mongoloids wrote out contractions in AT LEAST 5 DIFFERENT WAYS
    # so here are special cases to normalize all of them (e.g. the contraction
    # for 'we will' ("we'll"), shows up as "we 'll", "we' ll", "we'll", "we ' ll", and "we (QUOTE ll)", wtf)
    #
    # according to the limited lexical analysis I've done on this data,
    # all 5 cases should be covered and normalized by this code
    while string.find("  ") != -1:
        string = string.replace("  ", " ")
    while string.find(" '") != -1:
        string = string.replace(" '", "'")
    while string.find("' ") != -1:
        string = string.replace("' ", "'")

    return string


def get_times(time_string: str) -> Dict[str, float]:
    for char in string.whitespace:
        time_string = time_string.replace(char, " ")
    times = [x for x in time_string.strip().split(" ") if len(x) != 0]
    return {"start": float(times[0].strip()), "end": float(times[1].strip())}


DIRECTIVES = [str(val) for val in TerminalDirective.__members__.values()]
CONSTANT_TERMINALS = [str(val) for val in TerminalConstant.__members__.values()]


callbacks: Dict[TerminalDirective, Callable] = {
    TerminalDirective.TEXT: get_string_and_normalize,
    TerminalDirective.TIMES: get_times,
}


def parse_directive(expression: str) -> Directive:
    directive = ""
    arguments = ""
    position = 0

    while position < len(expression) and directive not in DIRECTIVES:
        directive += expression[position]
        position += 1

    if directive in DIRECTIVES and len(directive) != len(expression):
        arguments = expression[position:]

    return Directive(directive=directive, arguments=arguments.strip())


def parse_list(document: str, position: int) -> Tuple[int, List[str]]:
    lists: List[str] = []
    content = ""

    while document[position] != str(TerminalConstant.CLOSE_PAREN):
        current_char = document[position]

        # an expression starting and ending with quotes is to be taken as a string literal
        if current_char == '"':
            content += document[position]
            position += 1
            while document[position] != '"':
                content += document[position]
                position += 1

        if current_char == str(TerminalConstant.OPEN_PAREN):
            # lisp lists are defined recursively, so it makes sense to parse them recursively as well
            position, temp = parse_list(document, position + 1)

            # special case for escaped quotes in text fields
            try:
                parsed_expression = parse_directive(temp[0])
                if parsed_expression.directive == TerminalDirective.QUOTE:
                    content = content.strip() + "'" + parsed_expression.arguments
                else:
                    lists.extend(temp)
            except ValueError:
                # ValueError is raised if the keyword found doesn't match
                # any of the pre-defined keywords so we have to assume that
                # it is a mislabeled (or unlabeled) comment and does not
                # contribute significant information to the transcript
                logging.info(f"Discarding unrecognized symbol(s): {temp}")
        else:
            content += current_char
            position += 1

    if content != "":
        lists.append(content)

    return position + 1, lists


def reformat(data: List[str]) -> Dict:
    formatted_data = {}
    for expression in data:
        try:
            parsed_data = parse_directive(expression)
            callback_function = callbacks.get(
                parsed_data.directive, lambda x: x.strip()
            )
            formatted_data[str(parsed_data.directive)] = callback_function(
                parsed_data.arguments
            )
        except ValueError as e:
            logging.info(e)
        except Exception as e:
            logging.error(e)
    return formatted_data


def parse(lines: List[str]) -> List[Dict]:
    document = ""
    for line in lines:
        # remove trailing whitespace
        document += line.rstrip()
    document_length = len(document)

    data_blocks = []
    position = 0
    while position < document_length:
        # start of a list
        if document[position] == str(TerminalConstant.OPEN_PAREN):
            position, block = parse_list(document, position + 1)
            data_blocks.append(block)
        else:
            position += 1

    for i, data in enumerate(data_blocks):
        data_blocks[i] = reformat(data)

    return data_blocks
