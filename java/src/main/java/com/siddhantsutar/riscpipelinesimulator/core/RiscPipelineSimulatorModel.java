package com.siddhantsutar.riscpipelinesimulator.core;

import com.siddhantsutar.riscpipelinesimulator.forwardingunit.ExForwardingUnit;
import com.siddhantsutar.riscpipelinesimulator.forwardingunit.IdForwardingUnit;
import com.siddhantsutar.riscpipelinesimulator.memory.DataMemory;
import com.siddhantsutar.riscpipelinesimulator.memory.InstructionMemory;
import com.siddhantsutar.riscpipelinesimulator.memory.Memory;
import com.siddhantsutar.riscpipelinesimulator.memory.RegisterFileMemory;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.List;
import java.util.Observable;
import java.util.Observer;

public class RiscPipelineSimulatorModel extends Observable implements Observer {

	private static final int DATA_MEMORY_REGISTER_INDEX = 2;
	private String display;
	private MemoryHandler memoryHandler; //Member variable since 4 out of 5 stages require this
	private InterstageBuffer read; //Member variable since all stages require this
	private InterstageBuffer write; //Member variable since all stages require this

	public Binary8[] getDefaultDataMemoryValues() throws InvalidBinaryException {
		Binary8[] result = {
				new Binary8("00000001"),
				new Binary8("00000001"),
				new Binary8("00000001"),
				new Binary8("00010000"),
				new Binary8("00000000"),
				new Binary8("00010001"),
				new Binary8("00000000"),
				new Binary8("11110000"),
				new Binary8("00000000"),
				new Binary8("11111111")
		};
		return result;
	}
	
	public Binary16[] getDefaultRegisterFileValues() throws InvalidBinaryException {
		Binary16[] result = {
				new Binary16("0000000000000000"),
				new Binary16("0000000000000101"),
				new Binary16("0000000000010000"),
				new Binary16("0000000000000000"),
				new Binary16("0000000001000000"),
				new Binary16("0001000000010000"),
				new Binary16("0000000000001111"),
				new Binary16("0000000011110000")
		};
		return result;
	}
	
	public String getDisplay() {
		return display;
	}
	
	private void initClockCycle(ControlSignalsHandler branchSignals, ControlSignalsHandler globalSignals, ControlSignalsHandler hazardDetectionUnitSignals) {
		memoryHandler.incrementClockCycles();
		setDisplay(String.format("--- CYCLE %s ---", memoryHandler.getClockCycles()));
		initClockCycle(branchSignals, BranchControlSignal.class, ControlSignalValue.NONE);
		initClockCycle(globalSignals, GlobalControlSignal.class, ControlSignalValue.FALSE);
		initClockCycle(hazardDetectionUnitSignals, HazardDetectionUnitControlSignal.class, ControlSignalValue.TRUE);
	}

	private <T extends ControlSignal> void initClockCycle(ControlSignalsHandler controlSignalsHandler, Class<T> clazz, ControlSignalValue value) {
		for (T controlSignal : clazz.getEnumConstants()) {
			controlSignalsHandler.put(controlSignal, value);
		}
	}
	
	public void initMemory(String inFilename, Binary16[] registerFile, Binary8[] dataMemory) {
		memoryHandler = new MemoryHandler(registerFile);
		Binary8[] mainDataMemory = memoryHandler.getDataMemory().getData();
		List<Binary8> instructionMemory = memoryHandler.getInstructionMemory().getData();
		int start = registerFile[DATA_MEMORY_REGISTER_INDEX].getData();
		for (int i = 0; i < dataMemory.length; i++) {
			mainDataMemory[start+i] = dataMemory[i];
		}
		BufferedReader inFile = null;
		try {
			inFile = new BufferedReader(new FileReader(inFilename));
			String string;
			while ((string = inFile.readLine()) != null) {
				String stringWithoutSpaces = string.replace(" ", "");
				instructionMemory.add(new Binary8(stringWithoutSpaces.substring(0, 8)));
				instructionMemory.add(new Binary8(stringWithoutSpaces.substring(8, 16)));
			}
		} catch (Exception e) {
			new ErrorHandler(e);
		}
	}
	
	private boolean isNop(PipelineRegister pipelineRegister) {
		boolean result = true;
		ControlSignalsHandler controlSignalsHandler = pipelineRegister.getControlSignalsHandler();
		for (ControlSignal controlSignal : controlSignalsHandler.getData().keySet()) {
			if (controlSignal instanceof PipelineControlSignal) {
				ControlSignalValue value = controlSignalsHandler.get(controlSignal);
				result = result && (value == ControlSignalValue.FALSE || value == ControlSignalValue.INVALID);
			}
		}
		return result;
	}
	
	private void setDisplay(String display) {
		this.display = display;
		setChanged();
		notifyObservers(display);
	}
	
	public void simulate(String outFilename) throws InvalidBinaryException {
		read = new InterstageBuffer();
		write = new InterstageBuffer();
		ControlSignalsHandler branchSignals = new ControlSignalsHandler(BranchControlSignal.class);
		ControlSignalsHandler globalSignals = new ControlSignalsHandler(GlobalControlSignal.class);
		ControlSignalsHandler hazardDetectionUnitSignals = new ControlSignalsHandler(HazardDetectionUnitControlSignal.class);
		MainControlUnit mainControlUnit = new MainControlUnit(read, write);
		ArithmeticLogicUnit arithmeticLogicUnit = new ArithmeticLogicUnit(read, write);
		HazardDetectionUnit hazardDetectionUnit = new HazardDetectionUnit(read, hazardDetectionUnitSignals);
		ExForwardingUnit exForwardingUnit = new ExForwardingUnit(read);
		IdForwardingUnit idForwardingUnit = new IdForwardingUnit(write);
		StageHelper<Unit> exStageHelper = new StageHelper<>(exForwardingUnit, arithmeticLogicUnit);
		StageHelper<Unit> idStageHelper = new StageHelper<>(mainControlUnit, hazardDetectionUnit, idForwardingUnit);
		exForwardingUnit.addObserver(this);
		idForwardingUnit.addObserver(this);
		updateOutput(outFilename);
		while (true) {
			updateOutput(outFilename);
			initClockCycle(branchSignals, globalSignals, hazardDetectionUnitSignals);
			write.clear();
			if (!read.getMemWb().isEmpty()) {
				setDisplay("WB stage");
				wbStage();
			}
			if (!read.getExMem().isEmpty()) {
				setDisplay("MEM stage");
				memStage();
			}
			if (!read.getIdEx().isEmpty()) {
				setDisplay("EX stage");
				exStage(exStageHelper);
			}
			if (!read.getIfId().isEmpty()) {
				setDisplay("ID stage");
				idStage(idStageHelper, branchSignals, globalSignals);
			}
			if (memoryHandler.getProgramCounter() < memoryHandler.getInstructionMemory().size()) {
				setDisplay("IF stage");
				ifStage(globalSignals, hazardDetectionUnitSignals);
			}
			read.copyFrom(write);
			if (read.isEmpty()) {
				break;
			}
		}
		setDisplay("--- END OF SIMULATION ---");
	}
	
	private void updateOutput(String outFilename) {
		DataMemory dataMemory = memoryHandler.getDataMemory();
		InstructionMemory instructionMemory = memoryHandler.getInstructionMemory();
		RegisterFileMemory registerFileMemory = memoryHandler.getRegisterFileMemory();
		if (memoryHandler.getProgramCounter() == 0) {
			updateOutput(outFilename, instructionMemory);
		}
		updateOutput(outFilename, dataMemory);
		updateOutput(outFilename, registerFileMemory);
	}
		
	private void updateOutput(String outFilename, Memory memory) {
		BufferedWriter writer = null;
		try {
			writer = new BufferedWriter(new FileWriter(String.format("%scycle%s.%s",
					outFilename, memoryHandler.getClockCycles(), memory.getOutputFileExtension())));
			writer.write(memory.toString());
			writer.close();
		} catch (IOException e) {
			new ErrorHandler(e);
		}
	}
	
	private void wbStage() {
		MemWbPipelineRegister memWb = read.getMemWb();
		ControlSignalsHandler controlSignalsHandler = memWb.getControlSignalsHandler();
		if (!isNop(memWb)) {
			if (controlSignalsHandler.get(WbPipelineControlSignal.REG_WRITE) == ControlSignalValue.TRUE) {
				ControlSignalValue value = controlSignalsHandler.get(WbPipelineControlSignal.MEM_TO_REG);
				if (value == ControlSignalValue.FALSE) {
					memoryHandler.getRegisterFileMemory().getData()[memWb.getRd().getData()] = memWb.getAluResult();
				} else if (value == ControlSignalValue.TRUE) {
					memoryHandler.getRegisterFileMemory().getData()[memWb.getRd().getData()] = memWb.getReadData();
				}
			}
		} else {
			setDisplay("NOP in WB stage");
		}
	}
	
	private void memStage() throws InvalidBinaryException {
		ExMemPipelineRegister exMem = read.getExMem();
		MemWbPipelineRegister memWb = write.getMemWb();
		ControlSignalsHandler exMemControlSignalsHandler = exMem.getControlSignalsHandler();
		ControlSignalsHandler memWbControlSignalsHandler = memWb.getControlSignalsHandler();
		Binary8[] dataMemory = memoryHandler.getDataMemory().getData();
		memWbControlSignalsHandler.copyValueFrom(exMemControlSignalsHandler, WbPipelineControlSignal.MEM_TO_REG);
		memWbControlSignalsHandler.copyValueFrom(exMemControlSignalsHandler, WbPipelineControlSignal.REG_WRITE);
		if (!isNop(exMem)) {
			memWb.setRd(exMem.getRd());
			int memoryHandlerAddress = exMem.getAluResult().getData();
			ControlSignalValue value = exMemControlSignalsHandler.get(MemPipelineControlSignal.MEM_READ);
			if (value == ControlSignalValue.FALSE) {
				memWb.setAluResult(exMem.getAluResult());
			} else if (value == ControlSignalValue.TRUE) {
				memWb.setReadData(new Binary16(dataMemory[memoryHandlerAddress].toString() + dataMemory[memoryHandlerAddress+1].toString()));
			}
			if (exMemControlSignalsHandler.get(MemPipelineControlSignal.MEM_WRITE) == ControlSignalValue.TRUE) {
				Binary16 binary16 = exMem.getReadData2();
				dataMemory[memoryHandlerAddress] = new Binary8(binary16.subBitString(0, 8));
				dataMemory[memoryHandlerAddress+1] = new Binary8(binary16.subBitString(8, 16));
			}
		} else {
			setDisplay("NOP in MEM stage");
		}
	}
	
	private void exStage(StageHelper<Unit> stageHelper) throws InvalidBinaryException {
		IdExPipelineRegister idEx = read.getIdEx();
		ExMemPipelineRegister exMem = write.getExMem();
		ControlSignalsHandler idExControlSignalsHandler = idEx.getControlSignalsHandler();
		ControlSignalsHandler exMemControlSignalsHandler = exMem.getControlSignalsHandler();
		ExForwardingUnit exForwardingUnit = stageHelper.getInstance(ExForwardingUnit.class);
		ArithmeticLogicUnit arithmeticLogicUnit = stageHelper.getInstance(ArithmeticLogicUnit.class);
		exMemControlSignalsHandler.copyValueFrom(idExControlSignalsHandler, MemPipelineControlSignal.MEM_READ);
		exMemControlSignalsHandler.copyValueFrom(idExControlSignalsHandler, MemPipelineControlSignal.MEM_WRITE);
		exMemControlSignalsHandler.copyValueFrom(idExControlSignalsHandler, WbPipelineControlSignal.MEM_TO_REG);
		exMemControlSignalsHandler.copyValueFrom(idExControlSignalsHandler, WbPipelineControlSignal.REG_WRITE);
		if (!isNop(idEx)) {
			exForwardingUnit.use();
			Binary16 forwardA = exForwardingUnit.getForwardA();
			Binary16 forwardB = exForwardingUnit.getForwardB();
			exMem.setReadData2(forwardB);
			ControlSignalValue value = idExControlSignalsHandler.get(ExPipelineControlSignal.REG_DST);
			if (value == ControlSignalValue.FALSE) {
				exMem.setRd(idEx.getRt());
			} else if (value == ControlSignalValue.TRUE) {
				exMem.setRd(idEx.getRd());
			}
			value = idExControlSignalsHandler.get(ExPipelineControlSignal.ALU_SRC);
			if (value == ControlSignalValue.FALSE) {
				arithmeticLogicUnit.use(forwardA, forwardB);
			} else if (value == ControlSignalValue.TRUE) {
				arithmeticLogicUnit.use(forwardA, idEx.getSEImm());
			}
		} else {
			setDisplay("NOP in EX stage");
		}
	}
	
	private void idStage(StageHelper<Unit> stageHelper, ControlSignalsHandler branchSignals, ControlSignalsHandler globalSignals) {
		IfIdPipelineRegister ifId = read.getIfId();
		IdExPipelineRegister idEx = write.getIdEx();
		MainControlUnit mainControlUnit = stageHelper.getInstance(MainControlUnit.class);
		HazardDetectionUnit hazardDetectionUnit = stageHelper.getInstance(HazardDetectionUnit.class);
		IdForwardingUnit idForwardingUnit = stageHelper.getInstance(IdForwardingUnit.class);
		Binary16[] registerFile = memoryHandler.getRegisterFileMemory().getData();
		if (ifId.getInstruction().equals(new Binary16())) {
			setDisplay("NOP in ID stage");
			mainControlUnit.use(branchSignals, true);
		} else {
			Binary16 instruction = ifId.getInstruction();
			Binary instruction1 = new Binary(instruction.subBitString(4, 7));
			Binary instruction2 = new Binary(instruction.subBitString(7, 10));
			hazardDetectionUnit.use(mainControlUnit, branchSignals);
			idEx.setProgramCounterPlus2(ifId.getProgramCounterPlus2());
			idEx.setReadData1(registerFile[instruction1.getData()]);
			idEx.setReadData2(registerFile[instruction2.getData()]);
			idEx.setRs(instruction1);
			idEx.setRt(instruction2);
			idEx.setRd(new Binary(instruction.subBitString(10, 13)));
			idEx.setSEImm(new Binary16(instruction.subBitString(10, 16), BinaryExtendType.SIGN));
			idForwardingUnit.use(branchSignals);
			Binary16 forwardA = idForwardingUnit.getForwardA();
			Binary16 forwardB = idForwardingUnit.getForwardB();
			if (branchSignals.get(BranchControlSignal.JUMP) == ControlSignalValue.TRUE) {
				globalSignals.setInvalid(GlobalControlSignal.PC_SRC);
				globalSignals.setTrue(GlobalControlSignal.IF_FLUSH);
				setDisplay("Jump taken");
			} else if (branchSignals.get(BranchControlSignal.BRANCH) == ControlSignalValue.TRUE) {
				if (forwardA != null && forwardA.equals(forwardB)) {
					globalSignals.setTrue(GlobalControlSignal.PC_SRC);
					globalSignals.setTrue(GlobalControlSignal.IF_FLUSH);
					setDisplay("Branch taken");
				}
			} else if (branchSignals.get(BranchControlSignal.BRANCH_NE) == ControlSignalValue.TRUE) {
				if (forwardA != null && !forwardA.equals(forwardB)) {
					globalSignals.setTrue(GlobalControlSignal.PC_SRC);
					globalSignals.setTrue(GlobalControlSignal.IF_FLUSH);
					setDisplay("Branch taken");
				}
			}
		}
	}
	
	private void ifStage(ControlSignalsHandler globalSignals, ControlSignalsHandler hazardDetectionUnitSignals) throws InvalidBinaryException {
		IfIdPipelineRegister ifId = write.getIfId();
		int programCounter = memoryHandler.getProgramCounter();
		List<Binary8> instructionMemory = memoryHandler.getInstructionMemory().getData();
		if (hazardDetectionUnitSignals.get(HazardDetectionUnitControlSignal.IF_ID_WRITE) == ControlSignalValue.TRUE) {
			ifId.setProgramCounterPlus2(programCounter+2);
			ifId.setInstruction(new Binary16(instructionMemory.get(programCounter).toString() + instructionMemory.get(programCounter+1).toString()));
		}
		if (globalSignals.get(GlobalControlSignal.IF_FLUSH) == ControlSignalValue.TRUE) {
			ifId.setInstruction(new Binary16());
		}
		if (hazardDetectionUnitSignals.get(HazardDetectionUnitControlSignal.PC_WRITE) == ControlSignalValue.TRUE) {
			switch (globalSignals.get(GlobalControlSignal.PC_SRC)) {
				case FALSE:
					programCounter = ifId.getProgramCounterPlus2();
					break;
				case TRUE:
					programCounter = ifId.getProgramCounterPlus2() + (write.getIdEx().getSEImm().getData() * 2);
					break;
				case INVALID:
					programCounter = new Binary(read.getIfId().getInstruction().subBitString(4, 16)).getData() * 2;
					break;
			}
			memoryHandler.setProgramCounter(programCounter);
		}
	}

	@Override public void update(Observable o, Object arg) {
		setDisplay((String) arg);
	}
		
}