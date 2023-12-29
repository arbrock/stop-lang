#!/usr/bin/python3
from tkinter import *
import sys

nregisters = 16

#imem = [0x05, 0x91, 0xE1, 0x90, 0xFF, 0x9F, 0x23, 0xDF]
if(len(sys.argv) < 2):
    print("Usage: {0} <file.hex>".format(sys.argv[0]))
    sys.exit(1)
imem = []
with open(sys.argv[1], "r") as fp:
    for l in fp.read().splitlines():
        imem.append(int(l, base=16))

reg = [0] * nregisters
opcode = 0
pc = -1
accum = 0
def update():
    accum_var.set("0x{:08x}".format(accum))
    opcode_var.set("0b{:08b}".format(opcode))
    pc_var.set(pc)
    for r in range(nregisters):
        registers_var[r].set(reg[r])

def step():
    global accum
    global opcode
    global reg
    global pc
    global running
    # pull mutable state from the VM
    accum = int(accum_var.get(), base=16)
    pc = int(pc_var.get())
    for r in range(nregisters):
        reg[r] = int(registers_var[r].get())
    # Fetch
    opcode = imem[pc]
    # Decode
    imm_val = opcode & 0x7F
    ex_ctrl = (opcode & 0x70) >> 4
    is_load = (opcode & 0x80) >> 7
    rs = opcode & 0xF
    # Execute
    next_pc = pc + 1
    if(not is_load): # LDI
        accum = imm_val
    elif(ex_ctrl == 0): # LDR
        accum = reg[rs]
    elif(ex_ctrl == 1): # STR
        if(rs == 0):
            print(accum)
        else:
            reg[rs] = accum
    elif(ex_ctrl == 2): # ADD
        accum = accum + reg[rs]
    elif(ex_ctrl == 3): # SUB
        accum = reg[rs] - accum
    elif(ex_ctrl == 4): # BZI
        next_pc = pc + rs
    elif(ex_ctrl == 5): # BRR
        next_pc = reg[rs]
    elif(ex_ctrl == 6): # BLR
        accum = next_pc
        next_pc = reg[rs]
    elif(ex_ctrl == 7): # STOP
        running = 0
    pc = next_pc
    # update the GUI
    update()

def run():
    global running
    running = 1
    while(running):
        step()

root = Tk()
root.title("Stop Language VM")
inst_frame = LabelFrame(root, text="Instructions")
work_frame = Frame(root)
reg_frame = LabelFrame(root, text="Registers")

inst_frame.pack(side=LEFT)
reg_frame.pack(side=RIGHT)
work_frame.pack()

# Right Panel: display registers
pc_frame = Frame(reg_frame)
pc_var = StringVar()
pc_lbl = Label(pc_frame, text="PC")
pc_lbl.pack(side=LEFT)
pc_entry = Entry(pc_frame, width=20, textvariable=pc_var)
pc_entry.pack(side=RIGHT)
pc_frame.pack()
registers_var = [0] * nregisters
for r in range(nregisters):
    frame = Frame(reg_frame)
    registers_var[r] = StringVar()
    lbl = Label(frame, text="R"+str(r))
    lbl.pack(side=LEFT)
    entry = Entry(frame, width=20, textvariable=registers_var[r])
    entry.pack(side=RIGHT)
    frame.pack()

# Center Panel
status_frame = Frame(work_frame)
status_frame.pack(side=TOP)
control_frame = Frame(work_frame)
control_frame.pack(side=BOTTOM)

acc_frame = LabelFrame(status_frame, text="Accumulator")
op_frame = LabelFrame(status_frame, text="Current Opcode")
acc_frame.pack(side=LEFT)
op_frame.pack(side=RIGHT)

accum_var = StringVar()
opcode_var = StringVar()
accum_entry = Entry(acc_frame, width=20, textvariable=accum_var)
opcode_entry = Entry(op_frame, width=20, textvariable=opcode_var)
accum_entry.pack()
opcode_entry.pack()

step_button = Button(control_frame, text="Step", command = step)
run_button = Button(control_frame, text="Run", command = run)
step_button.pack(side=LEFT)
run_button.pack(side=RIGHT)

step_button.focus()
update()

root.mainloop()
