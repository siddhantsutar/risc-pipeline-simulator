package com.siddhantsutar.riscpipelinesimulator.core;

import org.apache.commons.lang3.builder.RecursiveToStringStyle;
import org.apache.commons.lang3.builder.ToStringBuilder;

public class InterstageBuffer {

	private IfIdPipelineRegister ifId;
	private IdExPipelineRegister idEx;
	private ExMemPipelineRegister exMem;
	private MemWbPipelineRegister memWb;
	
	public InterstageBuffer() {
		init();
	}
	
	public void clear() {
		init();
	}
	
	public void copyFrom(InterstageBuffer interstageBuffer) {
		ifId = interstageBuffer.getIfId();
		idEx = interstageBuffer.getIdEx();
		exMem = interstageBuffer.getExMem();
		memWb = interstageBuffer.getMemWb();
	}
	
	public IfIdPipelineRegister getIfId() {
		return ifId;
	}
	
	public IdExPipelineRegister getIdEx() {
		return idEx;
	}
	
	public ExMemPipelineRegister getExMem() {
		return exMem;
	}
	
	public MemWbPipelineRegister getMemWb() {
		return memWb;
	}
	
	private void init() {
		ifId = new IfIdPipelineRegister();
		idEx = new IdExPipelineRegister();
		exMem = new ExMemPipelineRegister();
		memWb = new MemWbPipelineRegister();
	}
	
	public boolean isEmpty() {
		return ifId.isEmpty()
				&& idEx.isEmpty()
				&& exMem.isEmpty()
				&& memWb.isEmpty();
	}
	
	@Override public String toString() {
		return ToStringBuilder.reflectionToString(this, new RecursiveToStringStyle());
	}
	
}