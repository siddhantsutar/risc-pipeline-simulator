package com.siddhantsutar.riscpipelinesimulator.core;

public abstract class PipelineRegister {
	
	private ControlSignalsHandler controlSignalsHandler; //Member variable since 3 out of 4 subclasses require this
	
	public PipelineRegister(ControlSignalsHandler controlSignalsHandler) {
		this.controlSignalsHandler = controlSignalsHandler;
	}

	public ControlSignalsHandler getControlSignalsHandler() {
		return controlSignalsHandler;
	}
	
	public abstract boolean isEmpty();
		
}