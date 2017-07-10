package com.siddhantsutar.riscpipelinesimulator.core;

public enum ExPipelineControlSignal implements PipelineControlSignal {
	REG_DST,
	ALU_SRC,
	ALU_OP2,
	ALU_OP1,
	ALU_OP0
}