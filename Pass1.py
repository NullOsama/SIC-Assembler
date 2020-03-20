from collections import defaultdict
from utils import Instruction, opcode_table
from math import ceil


def parse_line(line: str):

    line = line.split()
    for indx, segment in enumerate():
        if segment.split()[0].startswith('.'):
            line = line[:indx]

    # remove spaces in between operands
    if len(line) > 1 and line[1].endswith(','):  # if there is no label
        # remove and return the compaund values
        line.append(line.pop(1) + line.pop(1))
    elif len(line) > 2 and line[2].endswith(','):  # if there is a label
        # remove and return the compaund values
        line.append(line.pop(2) + line.pop(2))

    if len(line) == 3:
        return line  # label, operation_name, operand
    elif len(line) == 2:
        return None, line  # No label, operation_name, operand
    elif len(line) == 1:
        return None, line[0], None  # No label, operation name, no operand
    else:
        raise SyntaxError


class Assembler:
    def __init__(self, input_file):
        super().__init__()

        # The content of the source file, i.e. lines
        self.content = [line.rstrip('\n') for line in input_file.readlines()]
        # Symbol Table
        self.symbol_table = defaultdict(str)
        # Locattion Counter
        self.locctr = 0
        self.prog_name = ''
        self.start_address = 0
        self.prog_length = 0

    def is_comment(self, line):
        return line.split()[0].startswith('.')

    def is_empty(self, line):
        return len(line.split()) == 0

    def pass_one(self):

        # Find the starting address and the name of the program.
        first_line = self.content[0]
        label, operation_name, operand = parse_line(first_line)

        if operation_name is not None:
            if operation_name == 'START':
                self.start_address = int(operand, base=16)
                self.locctr = int(operand, base=16)
                self.prog_name = label
        next(self.content)  # To jump on the first line

        for line_number, line in enumerate(self.content):
            if not self.is_comment(line) and not self.is_empty(line):
                label, operation_name, operand = parse_line(line)

                if label is not None:
                    if label not in self.symbol_table:
                        self.symbol_table[label] = hex(int(self.locctr))
                    else:
                        raise ProcessLookupError
                operation_name, form4 = operation_name[1:], 1 if operation_name.startswith(
                    '+') else operation_name, 0

                if operation_name in opcode_table:
                    self.locctr += opcode_table[operation_name].format + form4
                elif operation_name == 'BYTE':
                    if operand.startswith('X'):
                        operand = operand.replace("X", '')
                        operand = operand.replace("'", '')
                        operand = int(operand, base=16)
                        # hex representation has 0x extr charechters so we subtract 2 and then
                        # divide by 2 because hex numbers needs half byte to be stored
                        self.locctr += ceil((len(hex(operand)) - 2) / 2)
                    elif operand.startswith('C'):
                        operand = operand.replace("C", '')
                        operand = operand.replace("'", '')
                        # C means that we have letters which need one byte each to be stored
                        self.locctr += len(operand)
                    else:
                        raise SyntaxError
                elif operation_name == 'RESB':
                    self.locctr += int(operand)
                elif operation_name == 'WORD':
                    self.locctr += 3
                elif operation_name == 'RESW':
                    self.locctr += 3 * int(operand)
                # Program finished, Stop Reading.
                elif operation_name == 'END':
                    break
                elif operation_name == 'BASE':
                    pass
                else:
                    raise SyntaxError
