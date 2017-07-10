package com.siddhantsutar.riscpipelinesimulator.core;

public class IfIdPipelineRegister extends PipelineRegister {

	private int programCounterPlus2;
	private Binary16 instruction;
	
	public IfIdPipelineRegister() {
		super(null);
		programCounterPlus2 = -1;
		instruction = null;
	}
	
	public Binary16 getInstruction() {
		return instruction;
	}

	public int getProgramCounterPlus2() {
		return programCounterPlus2;
	}
	
	public void setInstruction(Binary16 instruction) {
		this.instruction = instruction;
	}
	
	public void setProgramCounterPlus2(int programCounterPlus2) {
		this.programCounterPlus2 = programCounterPlus2;
	}

	@Override public boolean isEmpty() {
		return programCounterPlus2 == -1 
				&& instruction == null;
	}
	
}