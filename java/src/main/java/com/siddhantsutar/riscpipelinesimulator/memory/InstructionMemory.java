package com.siddhantsutar.riscpipelinesimulator.memory;

import com.siddhantsutar.riscpipelinesimulator.core.Binary16;
import com.siddhantsutar.riscpipelinesimulator.core.Binary8;
import com.siddhantsutar.riscpipelinesimulator.core.ErrorHandler;
import com.siddhantsutar.riscpipelinesimulator.core.InvalidBinaryException;
import java.util.ArrayList;
import java.util.List;

public class InstructionMemory extends Memory {

	private static final String OUTPUT_FILE_EXTENSION = "instruction_memory";
	private static final int START_ADDRESS = 4096;
	private List<Binary8> data;
	
	public InstructionMemory() {
		data = new ArrayList<>();
		setOutputFileExtension(OUTPUT_FILE_EXTENSION);
	}
	
	public List<Binary8> getData() {
		return data;
	}
	
	public int size() {
		return data.size();
	}
	
	@Override public String toString() {
		StringBuilder result = new StringBuilder();
		result.append(rowString("Address", "Hex Value", "Binary Value"));
		for (int i = 0; i < data.size(); i += 2) {
			Binary16 binary16;
			try {
				binary16 = new Binary16(String.format("%s%s", data.get(i).toString(), data.get(i+1).toString()));
				result.append(rowString(integerToHexStringPrefix(START_ADDRESS+i),
						integerToHexStringPrefix(binary16.getData()),
						binary16.toFormattedString()));
			} catch (InvalidBinaryException e) {
				new ErrorHandler(e);
			}
		}
		return result.toString();
	}
	
}