package com.siddhantsutar.riscpipelinesimulator.core;

import com.siddhantsutar.riscpipelinesimulator.memory.DataMemory;
import com.siddhantsutar.riscpipelinesimulator.memory.InstructionMemory;
import com.siddhantsutar.riscpipelinesimulator.memory.RegisterFileMemory;

public class MemoryHandler {

	private int clockCycles;
	private DataMemory dataMemory;
	private InstructionMemory instructionMemory;
	private int programCounter;
	private RegisterFileMemory registerFileMemory;
	
	public MemoryHandler(Binary16[] registerFile) {
		clockCycles = 0;
		dataMemory = new DataMemory();
		instructionMemory = new InstructionMemory();
		programCounter = 0;
		registerFileMemory = new RegisterFileMemory(registerFile);
	}
	
	public int getClockCycles() {
		return clockCycles;
	}
	
	public DataMemory getDataMemory() {
		return dataMemory;
	}
	
	public InstructionMemory getInstructionMemory() {
		return instructionMemory;
	}
	
	public int getProgramCounter() {
		return programCounter;
	}
	
	public RegisterFileMemory getRegisterFileMemory() {
		return registerFileMemory;
	}
	
	public void incrementClockCycles() {
		clockCycles += 1;
	}
	
	public void setProgramCounter(int programCounter) {
		this.programCounter = programCounter;
	}

}