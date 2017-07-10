package com.siddhantsutar.riscpipelinesimulator.core;

public class RiscPipelineSimulator {

	public static void main(String[] args) throws InvalidBinaryException {
		RiscPipelineSimulatorView view = new RiscPipelineSimulatorView();
		RiscPipelineSimulatorModel model = new RiscPipelineSimulatorModel();
		RiscPipelineSimulatorController controller = new RiscPipelineSimulatorController(view, model);
		model.addObserver(controller);
		view.setVisible(true);		
	}
	
}