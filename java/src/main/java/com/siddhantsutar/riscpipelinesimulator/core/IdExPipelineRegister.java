package com.siddhantsutar.riscpipelinesimulator.core;

public class IdExPipelineRegister extends PipelineRegister {

	private int programCounterPlus2;
	private Binary16 readData1;
	private Binary16 readData2;
	private Binary rs;
	private Binary rt;
	private Binary rd;
	private Binary16 sEImm;
	
	public IdExPipelineRegister() {
		super(new ControlSignalsHandler(ExPipelineControlSignal.class, MemPipelineControlSignal.class, WbPipelineControlSignal.class));
		programCounterPlus2 = -1;
		readData1 = null;
		readData2 = null;
		rs = null;
		rt = null;
		rd = null;
		sEImm = null;
	}
	
	public int getProgramCounterPlus2() {
		return programCounterPlus2;
	}
	
	public Binary16 getReadData1() {
		return readData1;
	}
	
	public Binary16 getReadData2() {
		return readData2;
	}
	
	public Binary getRs() {
		return rs;
	}
	
	public Binary getRt() {
		return rt;
	}
	
	public Binary getRd() {
		return rd;
	}
	
	public Binary16 getSEImm() {
		return sEImm;
	}
	
	public void setProgramCounterPlus2(int programCounterPlus2) {
		this.programCounterPlus2 = programCounterPlus2;
	}

	public void setReadData1(Binary16 readData1) {
		this.readData1 = readData1;
	}

	public void setReadData2(Binary16 readData2) {
		this.readData2 = readData2;
	}

	public void setRs(Binary rs) {
		this.rs = rs;
	}

	public void setRt(Binary rt) {
		this.rt = rt;
	}

	public void setRd(Binary rd) {
		this.rd = rd;
	}
	
	public void setSEImm(Binary16 sEImm) {
		this.sEImm = sEImm;
	}
	
	@Override public boolean isEmpty() {
		return getControlSignalsHandler().isEmpty()
				&& programCounterPlus2 == -1 
				&& readData1 == null
				&& readData2 == null
				&& rs == null
				&& rt == null
				&& rd == null
				&& sEImm == null;
	}

}