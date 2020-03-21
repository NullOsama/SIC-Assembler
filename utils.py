
class Instruction:
    """ 
    Represents a single instruction. 
    """

    def __init__(self, opcode, format, operands):
        self.opcode = opcode
        self.operands = operands
        self.format = format


# Operation code table, Appendex A in the book
opcode_table = {'ADD':     Instruction('18', 3, ['m']),
                'ADDF':    Instruction('58', 3, ['m']),
                'ADDR':    Instruction('90', 2, ['r1', 'r2']),
                'AND':     Instruction('40', 3, ['m']),
                'CLEAR':   Instruction('B4', 2, ['r1']),
                'COMP':    Instruction('28', 3, ['m']),
                'COMPF':   Instruction('88', 3, ['m']),
                'COMPR':   Instruction('A0', 2, ['r1', 'r2']),
                'DIV':     Instruction('24', 3, ['m']),
                'DIVF':    Instruction('64', 3, ['m']),
                'DIVR':    Instruction('9C', 2, ['r1', 'r2']),
                'FIX':     Instruction('C4', 1, None),
                'FLOAT':   Instruction('C0', 1, None),
                'HIO':     Instruction('F4', 1, None),
                'J':       Instruction('3C', 3, ['m']),
                'JEQ':     Instruction('30', 3, ['m']),
                'JGT':     Instruction('34', 3, ['m']),
                'JLT':     Instruction('38', 3, ['m']),
                'JSUB':    Instruction('48', 3, ['m']),
                'LDA':     Instruction('00', 3, ['m']),
                'LDB':     Instruction('68', 3, ['m']),
                'LDCH':    Instruction('50', 3, ['m']),
                'LDF':     Instruction('70', 3, ['m']),
                'LDL':     Instruction('08', 3, ['m']),
                'LDS':     Instruction('6C', 3, ['m']),
                'LDT':     Instruction('74', 3, ['m']),
                'LDX':     Instruction('04', 3, ['m']),
                'LPS':     Instruction('D0', 3, ['m']),
                'MULF':    Instruction('60', 3, ['m']),
                'MULR':    Instruction('98', 2, ['r1', 'r2']),
                'NORM':    Instruction('C8', 1, None),
                'OR':      Instruction('44', 3, ['m']),
                'RD':      Instruction('D8', 3, ['m']),
                'RMO':     Instruction('AC', 2, ['r1', 'r2']),
                'RSUB':    Instruction('4C', 3, None),
                'SHIFTL':  Instruction('A4', 2, ['r1', 'n']),
                'SHIFTR':  Instruction('A8', 2, ['r1', 'n']),
                'SIO':     Instruction('F0', 1, None),
                'SSK':     Instruction('EC', 3, ['m']),
                'STA':     Instruction('0C', 3, ['m']),
                'STB':     Instruction('78', 3, ['m']),
                'STCH':    Instruction('54', 3, ['m']),
                'STF':     Instruction('80', 3, ['m']),
                'STI':     Instruction('D4', 3, ['m']),
                'STL':     Instruction('14', 3, ['m']),
                'STS':     Instruction('7C', 3, ['m']),
                'STSW':    Instruction('E8', 3, ['m']),
                'STT':     Instruction('84', 3, ['m']),
                'STX':     Instruction('10', 3, ['m']),
                'SUB':     Instruction('1C', 3, ['m']),
                'SUBF':    Instruction('5C', 3, ['m']),
                'SUBR':    Instruction('94', 2, ['r1', 'r2']),
                'SVC':     Instruction('B0', 2, ['n']),
                'TD':      Instruction('E0', 3, ['m']),
                'TIO':     Instruction('F8', 1, None),
                'TIX':     Instruction('2C', 3, ['m']),
                'TIXR':    Instruction('B8', 2, ['r1']),
                'WD':      Instruction('DC', 3, ['m'])
                }