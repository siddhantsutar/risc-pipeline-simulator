package com.siddhantsutar.riscpipelinesimulator.core;

public class ArithmeticLogicControlUnit extends ControlUnit {

	public ArithmeticLogicControlUnit(InterstageBuffer read) {
		super(read);
	}

	private int not(int input) {
		return 1 - input;
	}
	
	public Binary use() {
		ControlSignalsHandler controlSignalsHandler = getRead().getIdEx().getControlSignalsHandler();
		char[] operation = new char[3];
		String funct = getRead().getIdEx().getSEImm().subBitString(13, 16);
		int f2 = Character.getNumericValue(funct.charAt(0));
		int f1 = Character.getNumericValue(funct.charAt(1));
		int f0 = Character.getNumericValue(funct.charAt(2));
		int aluOp2 = controlSignalsHandler.get(ExPipelineControlSignal.ALU_OP2) == ControlSignalValue.TRUE ? 1 : 0;
		int aluOp1 = controlSignalsHandler.get(ExPipelineControlSignal.ALU_OP1) == ControlSignalValue.TRUE ? 1 : 0;
		int aluOp0 = controlSignalsHandler.get(ExPipelineControlSignal.ALU_OP0) == ControlSignalValue.TRUE ? 1 : 0;
		operation[0] = ((aluOp2) + (not(aluOp1) * not(aluOp2)) + (f2 * not(aluOp0))) == 0 ? '0' : '1';
		operation[1] = ((aluOp2 * aluOp1) + (f1 * aluOp1 * not(aluOp0))) == 0 ? '0' : '1';
		operation[2] = ((aluOp2 * aluOp0) + (f0 * not(aluOp2) * aluOp1 * not(aluOp0))) == 0 ? '0' : '1';
		return new Binary(String.valueOf(operation));
	}
	
}