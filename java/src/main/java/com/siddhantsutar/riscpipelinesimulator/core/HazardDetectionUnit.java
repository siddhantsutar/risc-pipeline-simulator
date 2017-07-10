package com.siddhantsutar.riscpipelinesimulator.core;

public class HazardDetectionUnit extends Unit {

	private ControlSignalsHandler hazardDetectionUnitSignals;
	
	public HazardDetectionUnit(InterstageBuffer read) {
		super(read);
	}
	
	public HazardDetectionUnit(InterstageBuffer read, ControlSignalsHandler hazardDetectionUnitSignals) {
		this(read);
		this.hazardDetectionUnitSignals = hazardDetectionUnitSignals;
	}

	private void setSignals(MainControlUnit mainControlUnit, ControlSignalsHandler branchSignals, ControlSignalValue value) {
		mainControlUnit.use(branchSignals, value == ControlSignalValue.TRUE ? false : true);
		hazardDetectionUnitSignals.put(HazardDetectionUnitControlSignal.PC_WRITE, value);
		hazardDetectionUnitSignals.put(HazardDetectionUnitControlSignal.IF_ID_WRITE, value);
	}

	public void use(MainControlUnit mainControlUnit, ControlSignalsHandler branchSignals) {
		IfIdPipelineRegister ifId = getRead().getIfId();
		IdExPipelineRegister idEx = getRead().getIdEx();
		ExMemPipelineRegister exMem = getRead().getExMem();
		ControlSignalsHandler idExControlSignalsHandler = idEx.getControlSignalsHandler();
		ControlSignalsHandler exMemControlSignalsHandler = exMem.getControlSignalsHandler();
		String ifIdSubBitString47 = ifId.getInstruction().subBitString(4, 7);
		String ifIdSubBitString710 = ifId.getInstruction().subBitString(7, 10);
		if (idExControlSignalsHandler.get(MemPipelineControlSignal.MEM_READ) == ControlSignalValue.TRUE
				&& (idEx.getRt().toString().equals(ifIdSubBitString47) 
						|| idEx.getRt().toString().equals(ifIdSubBitString710))) {
			setSignals(mainControlUnit, branchSignals, ControlSignalValue.FALSE);
		} else if ((branchSignals.get(BranchControlSignal.BRANCH) == ControlSignalValue.TRUE
				|| branchSignals.get(BranchControlSignal.BRANCH_NE) == ControlSignalValue.TRUE)
				&& (idExControlSignalsHandler.get(WbPipelineControlSignal.REG_WRITE) == ControlSignalValue.TRUE)
				&& (idEx.getRd().toString().equals(ifIdSubBitString47))
				&& (idEx.getRd().toString().equals(ifIdSubBitString710))) {
			setSignals(mainControlUnit, branchSignals, ControlSignalValue.FALSE);
		} else if ((branchSignals.get(BranchControlSignal.BRANCH) == ControlSignalValue.TRUE
				|| branchSignals.get(BranchControlSignal.BRANCH_NE) == ControlSignalValue.TRUE)
				&& (idExControlSignalsHandler.get(MemPipelineControlSignal.MEM_READ) == ControlSignalValue.TRUE)
				&& (idEx.getRd().toString().equals(ifIdSubBitString47))
				&& (idEx.getRd().toString().equals(ifIdSubBitString710))) {
			setSignals(mainControlUnit, branchSignals, ControlSignalValue.FALSE);
		} else if ((branchSignals.get(BranchControlSignal.BRANCH) == ControlSignalValue.TRUE
				|| branchSignals.get(BranchControlSignal.BRANCH_NE) == ControlSignalValue.TRUE)
				&& (exMemControlSignalsHandler.get(MemPipelineControlSignal.MEM_READ) == ControlSignalValue.TRUE)
				&& (idEx.getRd().toString().equals(ifIdSubBitString47))
				&& (idEx.getRd().toString().equals(ifIdSubBitString710))) {
			setSignals(mainControlUnit, branchSignals, ControlSignalValue.FALSE);
		} else {
			setSignals(mainControlUnit, branchSignals, ControlSignalValue.TRUE);
		}
	}

}