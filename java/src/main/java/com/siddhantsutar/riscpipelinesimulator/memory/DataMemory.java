package com.siddhantsutar.riscpipelinesimulator.memory;

import com.siddhantsutar.riscpipelinesimulator.core.Binary16;
import com.siddhantsutar.riscpipelinesimulator.core.Binary8;
import com.siddhantsutar.riscpipelinesimulator.core.ErrorHandler;
import com.siddhantsutar.riscpipelinesimulator.core.InvalidBinaryException;

public class DataMemory extends Memory {

	private static final String NOT_A_NUMBER = "NaN";
	private static final String OUTPUT_FILE_EXTENSION = "data_memory";
	private static final int SIZE = 64;
	private Binary8[] data;
	
	public DataMemory() {
		data = new Binary8[SIZE];
		setOutputFileExtension(OUTPUT_FILE_EXTENSION);
	}
	
	public Binary8[] getData() {
		return data;
	}
	
	@Override public String toString() {
		StringBuilder result = new StringBuilder();
		result.append(rowString("Address", "Hex Value", "Binary Value"));
		for (int i = 0; i < data.length; i += 2) {
			if (data[i] == null) {
				result.append(rowString(NOT_A_NUMBER, NOT_A_NUMBER, NOT_A_NUMBER));
			} else {
				try {
					Binary16 binary16 = new Binary16(String.format("%s%s", data[i].toString(), data[i+1].toString()));
					result.append(rowString(integerToHexStringPrefix(i),
							integerToHexStringPrefix(binary16.getData()),
							binary16.toFormattedString()));
				} catch (InvalidBinaryException e) {
					new ErrorHandler(e);
				}
			}
		}
		return result.toString();
	}
	
}