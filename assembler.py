import sys
from math import ceil
from collections import defaultdict
from utils import Instruction, opcode_table


class Line:
    """
    Break SIC instruction into label, opcode, operands.


    Parameters
    ----------
    line: str
    SIC instruction
    """

    def __init__(self, line):
        super().__init__()
        if len(line) != 0:
            self.label, self.operation_name, self.operand = self.parse_line(
                line)
            self.line_location = ''
        else:
            self.label, self.operation_name, self.operand = '', '', ''
            self.line_location = ''

    def parse_line(self, line: str):
        """
        Break SIC instruction into label, opcode, operands.

        Parameters
        ----------
        Line: str
        SIC instruction

        Returns
        ----------
        label: str
        label of the SIC instruction

        operation_name: str
        opcodel of the SIC instruction

        operand: str
        operand of the SIC instruction
        """
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
            raise SyntaxError(f'Fixed format only {line}')


class Assembler:
    """
    Assembles a SIC source code file and operate pass1 on it.

    Parameters
    ----------
    input_file: str
    SIC source file
    """

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
        self.objects_list = []
        self.object_addresses = []
        self.text_records = []

    def is_comment(self, line):
        return line.split()[0].startswith('.')

    def is_empty(self, line):
        return len(line.split()) == 0

    def hexify_objects_code(self):
        self.objects_list = ['\t' if obj == '' else "{:08x}".format(
            int(obj, 2))[2:].upper() if len(obj) == 24 else obj for obj in self.objects_list]

    def pass_one(self):
        """
        Operate pass1 on the source code.

        Parameters
        ----------

        Returns
        ----------
        """
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
                        raise ProcessLookupError(
                            f'No duplicate labels are allowed on line {line_number}')

                if operation_name in opcode_table:
                    self.locctr += opcode_table[operation_name].format
                    if operand is not None and operand.startswith('='):
                        operand = operand.replace("=", '')
                        if operand.startswith('X'):
                            # X means that we have literals whith half byte for each charachter
                            literal_size = ceil((len(operand)-3)/2)
                        elif operand.startswith('C'):
                            literal_size = len(operand) - 3
                            # C means that we have letters which need one byte each to be stored
                        else:
                            raise SyntaxError(
                                f'Byte operand should only start with either X or C not {operand[0]} on line {line_number}')
                        literals_list.append(('=' + operand, literal_size))

                elif operation_name == 'LTORG':
                    # remove duplicates from literal list
                    literals_list = list(dict.fromkeys(literals_list))
                    for literal_value, literal_size in literals_list:
                        # Add the Literal to the symbol table
                        self.symbol_table[literal_value] = hex(
                            int(self.locctr))
                        # literal_line = Line(f'* {literal_value}  .NOOPERAND')
                        literal_line = Line('')
                        literal_line.label = '*'
                        literal_line.operation_name = literal_value
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
                        raise SyntaxError(
                            f'Byte operand should only start with either X or C not {operand[0]} on line {line_number}')
                elif operation_name == 'RESB':
                    self.locctr += int(operand)
                elif operation_name == 'WORD':
                    self.locctr += 3
                elif operation_name == 'RESW':
                    self.locctr += 3 * int(operand)
                # Program finished, Stop Reading.
                elif operation_name == 'END':
                    break
                elif operation_name == 'EQU':
                    pass
                else:
                    raise SyntaxError(
                        f'Undefined operation at {hex(int(self.locctr))} on line {line_number}')

        if len(literals_list) > 0:
            # Remove duplicates
            literals_list = list(dict.fromkeys(literals_list))
            for literal_value, literal_size in literals_list:
                # Add the Literal to the symbol table
                if literal_value in self.symbol_table:
                    continue
                self.symbol_table[literal_value] = hex(
                    int(self.locctr))
                literal_line = Line('')
                literal_line.label = '*'
                literal_line.operation_name = literal_value
                literal_line.line_location = self.locctr
                self.locctr += literal_size
                # Add the literal to the intermediate file
                self.intermediate.append(literal_line)
            literals_list = None  # Remove the list since we con't need it any more

        self.prog_length = int(hex(self.locctr - self.start_address), 0)

    def generate_objects_list(self):
        for line_object in self.intermediate:
            object_code = ''
            line_location, label, operation_name, operand = line_object.line_location, line_object.label, line_object.operation_name, line_object.operand

            if label == '*':  # Literal
                if operation_name[1] == 'X':
                    object_code = operand.replace("X", '').replace("'", '')
                elif operation_name[1] == 'C':
                    operation_name = operation_name.replace(
                        "C", '').replace("'", '')
                    object_code = ''.join(
                        [hex(ord(ch))[2:].upper() for ch in operation_name])
            else:
                if operation_name in opcode_table:
                    object_code += "{0:08b}".format(
                        int(opcode_table[operation_name].opcode, 16))
                    if operation_name == 'RSUB':
                        object_code += '0' * 16

                    elif ',' in operand:
                        object_code += '1'
                        base_operand, _ = operand.split(',')
                        object_code += "{0:015b}".format(
                            int(self.symbol_table[base_operand], 16))
                    else:
                        if operand in self.symbol_table:
                            object_code += '0'
                            object_code += "{0:015b}".format(
                                int(self.symbol_table[operand], 16))
                        else:
                            raise SyntaxError(
                                f'Operand not fount at {line_location}')
                else:
                    if operation_name == 'RESW' or operation_name == 'RESB':
                        object_code = ''
                    else:
                        if operation_name == 'WORD':
                            object_code += "{0:024b}".format(int(operand))
                        elif operation_name == 'BYTE':
                            if operand.startswith('X'):
                                object_code = operand.replace(
                                    "X", '').replace("'", '')
                            elif operand.startswith('C'):
                                operand = operand.replace(
                                    "C", '').replace("'", '')
                                object_code = ''.join(
                                    [hex(ord(ch))[2:].upper() for ch in operand])
            self.objects_list.append(object_code)
            self.object_addresses.append(line_location)
        self.hexify_objects_code()

    def generate_text_records(self):
        self.text_records.append(
            f'H{self.prog_name}    {"{0:06x}".format(int(hex(self.start_address), 16)).upper()}{"{0:06x}".format(int(hex(self.prog_length), 16)).upper()}')
        j = 0
        while j < len(self.objects_list):
            if self.objects_list[j] == '\t':
                j += 1
                continue

            record = ''
            start_address = self.object_addresses[j]
            length = 0
            while j < len(self.objects_list) and self.objects_list[j] != '\t' and len(record + self.objects_list[j]) <= 60:
                record += self.objects_list[j]
                j += 1
            length = ceil(len(record) / 2)
            length = "{0:02x}".format(length).upper()
            print(length)
            record = 'T' + "{0:06x}".format(int(hex(start_address), 16)).upper() + length + record
            self.text_records.append(record)
        self.text_records.append(f'E{"{0:06x}".format(int(hex(self.start_address), 16)).upper()}')

    def pass2(self):
        self.generate_objects_list()
        self.generate_text_records()


def assembel(source_path, intermediate_output_path, listing_output_path, object_file_path):
    if source_path == '' or intermediate_output_path == '':
        source_path = input('Enter the input source path: ')
        intermediate_output_path = input('Enter the output path: ')
    with open(source_path, 'r') as source_file, open(intermediate_output_path, 'w') as intermediate_file, open(listing_output_path, 'w') as listing_file, open(object_file_path, 'w') as object_file:
        assembler = Assembler(source_file)
        assembler.pass_one()
        assembler.pass2()
        print('\n\nProgram Name: ' + assembler.prog_name, 'Starting Address: ' +
              hex(assembler.start_address), 'Program Length: ' + str(assembler.prog_length) + ' bytes\n\n', sep='\n')

        print('label \t address')
        for label, label_address in assembler.symbol_table.items():
            print(label + ' \t ' + label_address.upper().replace('X', 'x'))
        intermediate_file_content = '\n'.join(['\t'.join([hex(line_object.line_location).upper().replace('X', 'x'), line_object.label if line_object.label is not None else '',
                                                          line_object.operation_name, line_object.operand if line_object.operand is not None else '']) for line_object in assembler.intermediate])

        listing_file_content = '\n'.join(['\t'.join([hex(line_object.line_location).upper().replace('X', 'x'), line_object.label if line_object.label is not None else '',
                                                     line_object.operation_name, line_object.operand if line_object.operand is not None else '']) + '\t' + object_code for line_object, object_code in zip(assembler.intermediate, assembler.objects_list)])

        objects_file_content = '\n'.join(assembler.text_records)

        intermediate_file.write(intermediate_file_content)
        listing_file.write(listing_file_content)

        object_file.write(objects_file_content)

        return assembler.prog_name, assembler.prog_length,  assembler.symbol_table


if __name__ == "__main__":
    if len(sys.argv) == 5:
        _, input_script_path, intermediate_path, listing_path, object_path = sys.argv
        assembel(input_script_path, intermediate_path, listing_path, object_path)
