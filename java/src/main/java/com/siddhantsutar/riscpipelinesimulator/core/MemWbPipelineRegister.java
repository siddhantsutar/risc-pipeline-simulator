package com.siddhantsutar.riscpipelinesimulator.core;

public class MemWbPipelineRegister extends PipelineRegister {

	private Binary16 aluResult;
	private Binary16 readData;
	private Binary rd;
	
	public MemWbPipelineRegister() {
		super(new ControlSignalsHandler(WbPipelineControlSignal.class));
		aluResult = null;
		readData = null;
		rd = null;
	}
	
	public Binary16 getAluResult() {
		return aluResult;
	}
	
	public Binary16 getReadData() {
		return readData;
	}
	
	public Binary getRd() {
		return rd;
	}

	public void setAluResult(Binary16 aluResult) {
		this.aluResult = aluResult;
	}

	public void setReadData(Binary16 readData) {
		this.readData = readData;
	}

	public void setRd(Binary rd) {
		this.rd = rd;
	}
		
	@Override public boolean isEmpty() {
		return getControlSignalsHandler().isEmpty()
				&& aluResult == null
				&& readData == null
				&& rd == null;
	}
	
}