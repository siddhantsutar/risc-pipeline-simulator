package com.siddhantsutar.riscpipelinesimulator.memory;

import com.siddhantsutar.riscpipelinesimulator.core.Binary16;

public class RegisterFileMemory extends Memory {

	private static final String OUTPUT_FILE_EXTENSION = "register_file_memory";
	private Binary16[] data;

	public RegisterFileMemory(Binary16[] data) {
		this.data = data;
		setOutputFileExtension(OUTPUT_FILE_EXTENSION);
	}

	public Binary16[] getData() {
		return data;
	}

	@Override public String toString() {
		StringBuilder result = new StringBuilder();
		result.append(rowString("Address", "Hex Value", "Binary Value"));
		for (int i = 0; i < data.length; i++) {
			result.append(rowString(String.format("$%s", i),
					integerToHexStringPrefix(data[i].getData()),
					data[i].toFormattedString()));
		}
		return result.toString();
	}

}