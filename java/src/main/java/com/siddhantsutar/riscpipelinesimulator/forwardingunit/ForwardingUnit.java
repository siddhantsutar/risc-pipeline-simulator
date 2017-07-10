package com.siddhantsutar.riscpipelinesimulator.forwardingunit;

import com.siddhantsutar.riscpipelinesimulator.core.Binary;
import com.siddhantsutar.riscpipelinesimulator.core.Binary16;
import com.siddhantsutar.riscpipelinesimulator.core.ControlSignalValue;
import com.siddhantsutar.riscpipelinesimulator.core.ControlSignalsHandler;
import com.siddhantsutar.riscpipelinesimulator.core.ExMemPipelineRegister;
import com.siddhantsutar.riscpipelinesimulator.core.HazardType;
import com.siddhantsutar.riscpipelinesimulator.core.IdExPipelineRegister;
import com.siddhantsutar.riscpipelinesimulator.core.InterstageBuffer;
import com.siddhantsutar.riscpipelinesimulator.core.MemWbPipelineRegister;
import com.siddhantsutar.riscpipelinesimulator.core.Unit;
import com.siddhantsutar.riscpipelinesimulator.core.WbPipelineControlSignal;
import java.util.Observable;
import java.util.Observer;

public abstract class ForwardingUnit extends Unit {

	private Binary16 forwardA;
	private Binary16 forwardB;
	private ForwardingUnitObservable observable;

	public ForwardingUnit(InterstageBuffer read) {
		super(read);
		observable = new ForwardingUnitObservable();
	}
	
	public void addObserver(Observer o) {
		observable.addObserver(o);
	}

	private void detectedHazard(HazardType hazardType) {
		observable.hasChanged(hazardType);
	}
	
	public Binary16 getForwardA() {
		return forwardA;
	}
	
	public Binary16 getForwardB() {
		return forwardB;
	}

	private Binary16 getForwardHazard(HazardType hazardType) {
		detectedHazard(hazardType);
		if (hazardType == HazardType.EX) {
			return getForwardExHazard();
		} else {
			return getForwardMemHazard();
		}
	}

	private Binary16 getForwardExHazard() {
		return getRead().getExMem().getAluResult();
	}
	
	private Binary16 getForwardMemHazard() {
		MemWbPipelineRegister memWb = getRead().getMemWb();
		ControlSignalsHandler memWbControlSignalsHandler = memWb.getControlSignalsHandler();
		if (memWbControlSignalsHandler.get(WbPipelineControlSignal.MEM_TO_REG) == ControlSignalValue.FALSE) {
			return memWb.getAluResult();
		} else if (memWbControlSignalsHandler.get(WbPipelineControlSignal.MEM_TO_REG) == ControlSignalValue.TRUE) {
			return memWb.getReadData();
		} else {
			return null;
		}
	}
	
	private boolean hazardCondition(ControlSignalsHandler controlSignalsHandler) {
		return controlSignalsHandler.get(WbPipelineControlSignal.REG_WRITE) == ControlSignalValue.TRUE;
	}
	
	protected void initForwards() {
		IdExPipelineRegister idEx = getRead().getIdEx();
		forwardA = idEx.getReadData1();
		forwardB = idEx.getReadData2();
	}
	
	private boolean setForwardHazard(Binary rd, HazardType hazardType) {
		IdExPipelineRegister idEx = getRead().getIdEx();
		boolean hazard = false;
		if (rd.equals(idEx.getRs())) {
			forwardA = getForwardHazard(hazardType);
			hazard = true;
		}
		if (rd.equals(idEx.getRt())) {
			forwardB = getForwardHazard(hazardType);
			hazard = true;
		}
		return hazard;
	}

	protected void use() {
		ExMemPipelineRegister exMem = getRead().getExMem();
		MemWbPipelineRegister memWb = getRead().getMemWb();
		boolean doubleData = false;
		boolean hazard = false;
		if (memWb.getRd() != null && memWb.getRd().equals(exMem.getRd())) {
			doubleData = true;
		}
		if (hazardCondition(exMem.getControlSignalsHandler())) { //EXE hazard
			hazard = setForwardHazard(exMem.getRd(), HazardType.EX);
		}
		if (!doubleData && !hazard) {
			if (hazardCondition(memWb.getControlSignalsHandler())) { //MEM hazard
				setForwardHazard(memWb.getRd(), HazardType.MEM);
			}
		}
	}
	
	class ForwardingUnitObservable extends Observable {
		
		private void hasChanged(HazardType hazardType) {
			setChanged();
			observable.notifyObservers(String.format("%s hazard detected", hazardType));
		}
		
	}
	
}