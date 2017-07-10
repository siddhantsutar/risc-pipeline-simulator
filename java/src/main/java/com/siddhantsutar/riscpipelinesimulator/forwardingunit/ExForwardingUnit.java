package com.siddhantsutar.riscpipelinesimulator.forwardingunit;

import com.siddhantsutar.riscpipelinesimulator.core.InterstageBuffer;

public class ExForwardingUnit extends ForwardingUnit {

	public ExForwardingUnit(InterstageBuffer read) {
		super(read);
	}
	
	public void use() {
		initForwards();
		super.use();
	}
		
}