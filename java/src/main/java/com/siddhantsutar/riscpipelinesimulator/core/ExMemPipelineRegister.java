package com.siddhantsutar.riscpipelinesimulator.core;

public class ExMemPipelineRegister extends PipelineRegister {

	private Binary16 aluResult;
	private Binary16 readData2;
	private Binary rd;
	
	public ExMemPipelineRegister() {
		super(new ControlSignalsHandler(MemPipelineControlSignal.class, WbPipelineControlSignal.class));
		aluResult = null;
		readData2 = null;
		rd = null;
	}
	
	public Binary16 getAluResult() {
		return aluResult;
	}
	
	public Binary16 getReadData2() {
		return readData2;
	}
	
	public Binary getRd() {
		return rd;
	}
	
	public void setAluResult(Binary16 aluResult) {
		this.aluResult = aluResult;
	}
	
	public void setReadData2(Binary16 readData2) {
		this.readData2 = readData2;
	}
	
	public void setRd(Binary rd) {
		this.rd = rd;
	}
	
	@Override public boolean isEmpty() {
		return getControlSignalsHandler().isEmpty()
				&& aluResult == null
				&& readData2 == null
				&& rd == null;
	}
	
}