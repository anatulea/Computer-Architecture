"""CPU functionality."""

import sys

flagL = 0b00000100
flagG = 0b00000010
flagE = 0b00000001

# CPU = Central Processing Unit


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0]*256  # memory
        self.reg = [0]*8  # 8 general-purpose registers
        self.pc = 0  # program count
        self.halted = False
        # SP: stack pointer is in register[7], but the stack is always in RAM, the start of the stack is F4 hexadecimal
        self.sp = int(0xF4)
        self.reg[7] = self.sp
        self.flag = 0
        self.running = True

     # read RAM at given address
     # MAR - Memory Address Register
    def ram_read(self, mar):
        return self.ram[mar]

    # Memory Data Register (MDR)
    # write value to ram address
    def ram_write(self, mdr, mar):
        self.ram[mar] = mdr

    def load(self):
        """Load a program into memory. Open a program file, read its contents and 
        save appropriate data into RAM"""
        address = 0

        try:
            if len(sys.argv) < 2:
                print(f'Error from {sys.argv[0]}: missing filename argument')
                print(f'Usage: python3 {sys.argv[0]} <somefilename>')
                sys.exit(1)

            with open(sys.argv[1]) as f:
                for line in f:
                    split_line = line.split('#')[0]
                    stripped_split_line = split_line.strip()
                    if stripped_split_line != "":

                        command = int(stripped_split_line, 2)

                        self.ram[address] = command
                        # self.ram_write(command, address)

                        address += 1

        except FileNotFoundError:
            print(f'Error from {sys.argv[0]}: {sys.argv[1]} not found')
            print("(Did you double check the file name?)")

    # Arithmetic logic unit
    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        # Add the value in two registers and store the result in registerA.
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]

        # Subtract the value in the second register from the first, storing the result in registerA.
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]

        # Multiply the values in two registers together and store the result in registerA.
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]

        # Divide the value in the first register by the value in the second, storing the result in registerA.
        elif op == "DIV":
            self.reg[reg_a] /= self.reg[reg_b]

        # Bitwise-AND the values in registerA and registerB, then store the result in registerA.
        elif op == "AND":
            self.reg[reg_a] = self.reg[reg_a] & self.reg[reg_b]

        # Perform a bitwise-OR between the values in registerA and registerB, storing the result in registerA.
        elif op == "OR":
            self.reg[reg_a] = self.reg[reg_a] | self.reg[reg_b]

        # Perform a bitwise-XOR between the values in registerA and registerB, storing the result in registerA.
        elif op == "XOR":
            self.reg[reg_a] = self.reg[reg_a] ^ self.reg[reg_b]

        # Perform a bitwise-NOT on the value in a register, storing the result in the register.
        elif op == "NOT":
            self.reg[reg_a] != self.reg[reg_b]

        # Shift the value in registerA left by the number of bits specified in registerB, filling the low bits with 0.
        elif op == "SHL":
            self.reg[reg_a] <<= self.reg[reg_b]

        # Shift the value in registerA right by the number of bits specified in registerB, filling the high bits with 0.
        elif op == "SHR":
            self.reg[reg_a] <<= self.reg[reg_b]

        # Divide the value in the first register by the value in the second, storing the remainder of the result in registerA.
        # If the value in the second register is 0, the system should print an error message and halt.
        elif op == "MOD":
            if self.reg[reg_b] == 0:
                print("A system error occurred! Division by zero. Program stopped!")
                self.running = False
            else:
                self.reg[reg_a] %= self.reg[reg_b]

        # Compare the values in two registers.
            # L Less-than: during a CMP, set to 1 if registerA is less than registerB, zero otherwise.
            # G Greater-than: during a CMP, set to 1 if registerA is greater than registerB, zero otherwise.
            # E Equal: during a CMP, set to 1 if registerA is equal to registerB, zero otherwis
        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.flag = flagE

            elif self.reg[reg_a] < self.reg[reg_b]:
                self.flag = flagL
            else:
                self.flag = flagG
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        HLT = 0b00000001
        LDI = 0b10000010
        PRN = 0b01000111
        MUL = 0b10100010
        ADD = 0b10100000
        SUB = 0b10100001
        DIV = 0b10100011
        PUSH = 0b01000101
        POP = 0b01000110
        CALL = 0b01010000
        RET = 0b00010001
        CMP = 0b10100111
        JMP = 0b01010100
        JEQ = 0b01010101
        JNE = 0b01010110
        ST = 0b10000100
        PRA = 0b01001000
        IRET = 0b00010011
        AND = 0b10101000
        OR = 0b10101010
        XOR = 0b10101011
        NOT = 0b01101001
        SHL = 0b10101100
        SHR = 0b10101101
        MOD = 0b10100100

        while self.running:
            ir = self.ram_read(self.pc)
            op_a = self.ram_read(self.pc + 1)  # address
            op_b = self.ram_read(self.pc + 2)  # value

            if ir == HLT:  # halt, stop the program
                self.running = False
                self.pc = 0

            # Set the value of a register to an integer.
            elif ir == LDI:  # register immediate
                self.reg[op_a] = op_b
                self.pc += 3

            # Print numeric value stored in the given register
            elif ir == PRN:  # register pseudo-instruction
                print(self.reg[op_a])
                self.pc += 2

            elif ir == MUL:
                self.alu("MUL", op_a, op_b)
                self.pc += 3

            elif ir == ADD:
                self.alu("ADD", op_a, op_b)
                self.pc += 3

            elif ir == SUB:
                self.alu("SUB", op_a, op_b)
                self.pc += 3
            elif ir == DIV:
                self.alu("DIV", op_a, op_b)
                self.pc += 3
            elif ir == AND:
                self.alu("AND", op_a, op_b)
                self.pc += 3
            elif ir == OR:
                self.alu("OR", op_a, op_b)
                self.pc += 3
            elif ir == XOR:
                self.alu("XOR", op_a, op_b)
                self.pc += 3
            elif ir == NOT:
                self.alu("NOT", op_a, op_b)
                self.pc += 3
            elif ir == SHL:
                self.alu("SHL", op_a, op_b)
                self.pc += 3
            elif ir == SHR:
                self.alu("SHR", op_a, op_b)
                self.pc += 3
            elif ir == MOD:
                self.alu("MOD", op_a, op_b)
                self.pc += 3
            # Push the value in the given register on the stack.
            elif ir == PUSH:
                self.sp -= 1  # Decrement the self.SP
                # Copy the value in the given register to the address pointed to by self.SP.
                self.ram_write(self.reg[op_a], self.sp)
                self.pc += 2

            # Pop the value at the top of the stack into the given register.
            elif ir == POP:
                # Copy the value from the address pointed to by self.SP to the given register.
                value = self.ram_read(self.sp)
                print(value)
                self.reg[op_a] = value
                self.sp += 1  # Increment self.SP
                self.pc += 2

            # Calls a subroutine (function) at the address stored in the register.
            elif ir == CALL:
                # get the value at return address (the one after subroutine_addr)
                return_addr = self.pc+2
                self.sp -= 1  # push it to stack
                self.ram_write(return_addr, self.sp)
                # set the pc to the subroutine address
                self.pc = self.reg[op_a]

            # Return from subroutine
            elif ir == RET:
                # Pop the value from the top of the stack and store it in the PC.
                self.pc = self.ram[self.sp]
                self.sp += 1

            # Compare the values in two registers
            elif ir == CMP:
                self.alu("CMP", op_a, op_b)
                self.pc += 3

            # Jump to the address stored in the given register.
            elif ir == JMP:
                # Set the PC to the address stored in the given register.
                self.pc = self.reg[op_a]

            # If equal flag is set (true), jump to the address stored in the given register.
            elif ir == JEQ:
                if self.flag == flagE:
                    self.pc = self.reg[op_a]
                else:
                    self.pc += 2

            elif ir == JNE:
                if self.flag != flagE:
                    self.pc = self.reg[op_a]
                else:
                    self.pc += 2
            # Store value in registerB in the address stored in registerA.
            elif ir == ST:
                print("st")
                self.reg[op_a] = self.reg[op_b]
                self.pc += 3
            # Print alpha character value stored in the given register.
            elif ir == PRA:
                # Print to the console the ASCII character corresponding to the value in the register.
                print(self.reg[op_b])

            # Return from an interrupt handler.
            elif ir == IRET:
                # Registers R6-R0 are popped off the stack in that order.
                for i in range(6, -1, -1):
                    reg_value = self.ram_read(self.reg[i])
                    self.reg[op_a] = reg_value
                    self.sp += 1
                    self.pc += 1

                # The FL register is popped off the stack.
                fl_value = self.ram_read(self.flag)
                self.reg[op_a] = fl_value
                self.sp += 1
                self.pc += 1

                # The return address is popped off the stack and stored in PC.
                pc_value = self.ram_read(self.pc)
                self.reg[op_a] = pc_value
                self.sp += 1
                self.pc += 1
                # Interrupts are re-enabled

        number_of_operands = ir >> 6

        # bit shift and mask to isolate the 'C' bit
        sets_pc_directly = ((ir >> 4) & 0b001) == 0b001

        if not sets_pc_directly:
            self.pc += (1 + number_of_operands)
