package com.siddhantsutar.riscpipelinesimulator.core;

public class MainControlUnit extends ControlUnit {
	
	private InterstageBuffer write;
	
	public MainControlUnit(InterstageBuffer read) {
		super(read);
	}
	
	public MainControlUnit(InterstageBuffer read, InterstageBuffer write) {
		this(read);
		this.write = write;
	}

	private void updatePipelineControlSignals(ControlSignalsHandler write, ControlSignalsHandler read) {
		for (Class<?> clazz : new Class[]{ExPipelineControlSignal.class, MemPipelineControlSignal.class, WbPipelineControlSignal.class}) {
			for (Object object : clazz.getEnumConstants()) {
				ControlSignal controlSignal = (ControlSignal) object;
				write.put(controlSignal, read == null ? ControlSignalValue.INVALID : read.get(controlSignal));
			}
		}
	}
	
	private void use(ControlSignalsHandler branchSignals, ControlSignalsHandler controlSignalsHandler) {
		updatePipelineControlSignals(write.getIdEx().getControlSignalsHandler(), controlSignalsHandler);
		for (BranchControlSignal branchControlSignal : BranchControlSignal.values()) {
			branchSignals.put(branchControlSignal, controlSignalsHandler.get(branchControlSignal));
		}
	}

	public void use(ControlSignalsHandler branchSignals, boolean nop) {
		ControlSignalsHandler controlSignalsHandler = new ControlSignalsHandler(ControlSignalValue.FALSE, ExPipelineControlSignal.class, MemPipelineControlSignal.class, WbPipelineControlSignal.class, BranchControlSignal.class);
		if (!nop) {
			String opcode = getRead().getIfId().getInstruction().subBitString(0, 4);
			switch (opcode) {
				case Opcode.R_FORMAT:
					controlSignalsHandler.setTrue(ExPipelineControlSignal.REG_DST);
					controlSignalsHandler.setTrue(ExPipelineControlSignal.ALU_OP1);
					controlSignalsHandler.setTrue(WbPipelineControlSignal.REG_WRITE);
					break;
				case Opcode.LW:
					controlSignalsHandler.setTrue(ExPipelineControlSignal.ALU_SRC);
					controlSignalsHandler.setTrue(MemPipelineControlSignal.MEM_READ);
					controlSignalsHandler.setTrue(WbPipelineControlSignal.MEM_TO_REG);
					controlSignalsHandler.setTrue(WbPipelineControlSignal.REG_WRITE);
					break;
				case Opcode.SW:
					controlSignalsHandler.setInvalid(ExPipelineControlSignal.REG_DST);
					controlSignalsHandler.setTrue(ExPipelineControlSignal.ALU_SRC);
					controlSignalsHandler.setTrue(MemPipelineControlSignal.MEM_WRITE);
					controlSignalsHandler.setInvalid(WbPipelineControlSignal.MEM_TO_REG);
					break;
				case Opcode.BEQ:
					updatePipelineControlSignals(controlSignalsHandler, null);
					controlSignalsHandler.setTrue(BranchControlSignal.BRANCH);
					break;
				case Opcode.BNE:
					updatePipelineControlSignals(controlSignalsHandler, null);
					controlSignalsHandler.setTrue(BranchControlSignal.BRANCH_NE);
					break;
				case Opcode.J:
					updatePipelineControlSignals(controlSignalsHandler, null);
					controlSignalsHandler.setTrue(BranchControlSignal.JUMP);
					break;
				case Opcode.ADDI:
					controlSignalsHandler.setTrue(ExPipelineControlSignal.ALU_SRC);
					controlSignalsHandler.setTrue(ExPipelineControlSignal.ALU_OP2);
					controlSignalsHandler.setTrue(WbPipelineControlSignal.REG_WRITE);
					break;
				case Opcode.ANDI:
					controlSignalsHandler.setTrue(ExPipelineControlSignal.ALU_SRC);
					controlSignalsHandler.setTrue(ExPipelineControlSignal.ALU_OP2);
					controlSignalsHandler.setTrue(ExPipelineControlSignal.ALU_OP0);
					controlSignalsHandler.setTrue(WbPipelineControlSignal.REG_WRITE);
					break;
				case Opcode.ORI:
					controlSignalsHandler.setTrue(ExPipelineControlSignal.ALU_SRC);
					controlSignalsHandler.setTrue(ExPipelineControlSignal.ALU_OP2);
					controlSignalsHandler.setTrue(ExPipelineControlSignal.ALU_OP1);
					controlSignalsHandler.setTrue(WbPipelineControlSignal.REG_WRITE);
					break;
				case Opcode.SLTI:
					controlSignalsHandler.setTrue(ExPipelineControlSignal.ALU_SRC);
					controlSignalsHandler.setTrue(ExPipelineControlSignal.ALU_OP2);
					controlSignalsHandler.setTrue(ExPipelineControlSignal.ALU_OP1);
					controlSignalsHandler.setTrue(ExPipelineControlSignal.ALU_OP0);
					controlSignalsHandler.setTrue(WbPipelineControlSignal.REG_WRITE);
					break;
			}
		}
		use(branchSignals, controlSignalsHandler);
	}

}