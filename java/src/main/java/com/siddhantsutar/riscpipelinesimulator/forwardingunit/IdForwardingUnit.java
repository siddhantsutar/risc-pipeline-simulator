package com.siddhantsutar.riscpipelinesimulator.forwardingunit;

import com.siddhantsutar.riscpipelinesimulator.core.BranchControlSignal;
import com.siddhantsutar.riscpipelinesimulator.core.ControlSignalValue;
import com.siddhantsutar.riscpipelinesimulator.core.ControlSignalsHandler;
import com.siddhantsutar.riscpipelinesimulator.core.InterstageBuffer;

public class IdForwardingUnit extends ForwardingUnit {

	public IdForwardingUnit(InterstageBuffer read) {
		super(read);
	}
	
	public void use(ControlSignalsHandler branchSignals) {
		initForwards();
		if (branchSignals.get(BranchControlSignal.BRANCH) == ControlSignalValue.TRUE
				|| branchSignals.get(BranchControlSignal.BRANCH_NE) == ControlSignalValue.TRUE) {
			use();
		}
	}
	
}