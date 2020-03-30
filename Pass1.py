import sys
import getopt
from math import ceil
from collections import defaultdict
from utils import Instruction, opcode_table


class Line:
    def __init__(self, line):
        super().__init__()
        self.label, self.operation_name, self.operand = self.parse_line(line)
        self.line_location = ''

    def parse_line(self, line: str):

        line = line.split()
        for indx, segment in enumerate(line):
            if segment.split()[0].startswith('.'):
                line = line[:indx]

        # remove spaces in between operands
        if len(line) > 1 and line[1].endswith(','):  # if there is no label
            # remove and return the compaund values
            line.append(line.pop(1) + line.pop(1))
        elif len(line) > 2 and line[2].endswith(','):  # if there is a label
            # remove and return the compaund values to the line
            line.append(line.pop(2) + line.pop(2))

        if len(line) == 3:
            return line[0], line[1], line[2]  # label, operation_name, operand
        elif len(line) == 2:
            return None, line[0], line[1]  # No label, operation_name, operand
        elif len(line) == 1:
            return None, line[0], None  # No label, operation name, no operand
        else:
            raise SyntaxError


class Assembler:
    def __init__(self, input_file):
        super().__init__()

        # The content of the source file, i.e. lines
        self.content = (line.rstrip('\n') for line in input_file.readlines())
        # Symbol Table
        self.symbol_table = defaultdict(str)
        # Location Counter
        self.locctr = 0
        self.prog_name = ''
        self.start_address = 0
        self.prog_length = 0
        self.intermediate = []

    def is_comment(self, line):
        return line.split()[0].startswith('.')

    def is_empty(self, line):
        return len(line.split()) == 0

    def pass_one(self):

        literals_list = []
        # Find the starting address and the name of the program.
        first_line = Line(next(self.content))
        label, operation_name, operand = first_line.label, first_line.operation_name, first_line.operand

        if operation_name is not None:
            if operation_name == 'START':
                self.start_address = int(operand, base=16)
                self.locctr = int(operand, base=16)
                self.prog_name = label
        # To jump on the first line
        first_line.line_location = self.start_address

        self.intermediate.append(first_line)

        for line_number, line in enumerate(self.content):
            if not self.is_empty(line) and not self.is_comment(line):
                line_object = Line(line)
                label, operation_name, operand = line_object.label, line_object.operation_name, line_object.operand
                line_object.line_location = self.locctr

                self.intermediate.append(line_object)

                if label is not None:
                    if label not in self.symbol_table:
                        self.symbol_table[label] = hex(int(self.locctr))
                    else:
                        raise ProcessLookupError

                if operation_name in opcode_table:
                    self.locctr += opcode_table[operation_name].format
                    if operand is not None and operand.startswith('='):
                        operand = operand.replace("=", '')
                        if operand.startswith('X'):
                            literal_size = ceil((len(operand)-3)/2)
                        elif operand.startswith('C'):
                            literal_size = len(operand) - 3
                            # C means that we have letters which need one byte each to be stored
                        literals_list.append(('=' + operand, literal_size))

                elif operation_name == 'LTORG':
                    # remove duplicates from literal list
                    literals_list = list(dict.fromkeys(literals_list))
                    for literal_value, literal_size in literals_list:
                        # Add the Literal to the symbol table
                        self.symbol_table[literal_value] = hex(
                            int(self.locctr))
                        literal_line = Line(f'*   {literal_value}  .NOOPERAND')
                        literal_line.line_location = self.locctr
                        self.locctr += literal_size
                        # Add the literal to the intermediate file
                        self.intermediate.append(literal_line)
                    literals_list = []

                elif operation_name == 'BYTE':
                    if operand.startswith('X'):
                        operand = operand.replace("X", '')
                        operand = operand.replace("'", '')
                        operand = int(operand, base=16)
                        # hex representation has 0x extra charechters so we subtract 2 and then
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
                elif operation_name == 'EQU':
                    pass
                else:
                    raise SyntaxError

        if len(literals_list) > 0:
            # Remove duplicates
            literals_list = list(dict.fromkeys(literals_list))
            for literal_value, literal_size in literals_list:
                # Add the Literal to the symbol table
                if literal_value in self.symbol_table:
                    continue
                self.symbol_table[literal_value] = hex(
                    int(self.locctr))
                literal_line = Line(f'*   {literal_value}  .NOOPERAND')
                literal_line.line_location = self.locctr
                self.locctr += literal_size
                # Add the literal to the intermediate file
                self.intermediate.append(literal_line)
            literals_list = None  # Remove the list since we con't need it any more

        self.prog_length = int(hex(self.locctr - self.start_address), 0)


def assembel(source_file_path, output_path):
    with open(source_file_path, 'r') as source_file, open(output_path, 'w') as intermediate_file:
        assembler = Assembler(source_file)
        assembler.pass_one()
        print(assembler.prog_name, assembler.prog_length,
              assembler.symbol_table, sep='\n')
        test = '\n'.join(['\t'.join([hex(line_object.line_location).upper().replace('X', 'x'), line_object.label if line_object.label is not None else '',
                                     line_object.operation_name, line_object.operand if line_object.operand is not None else '']) for line_object in assembler.intermediate])
        intermediate_file.write(test)

        return assembler.prog_name, assembler.prog_length,  assembler.symbol_table


assembel(r'sample_tests\literals.asm')
