package com.siddhantsutar.riscpipelinesimulator.memory;

import org.apache.commons.lang3.StringUtils;

public abstract class Memory {
	
	private static final int HEX_WIDTH = 4;
	private static final int OUTPUT_COLUMN_WIDTH = 15;
	private static final char SPACE = ' ';
	private static final char ZERO = '0';
	private String outputFileExtension;
	
	public String getOutputFileExtension() {
		return outputFileExtension;
	}

	protected String integerToHexStringPrefix(int number) {
		return String.format("0x%s", StringUtils.leftPad(Integer.toHexString(number), HEX_WIDTH, ZERO));
	}
	
	private String paddedString(String string) {
		return StringUtils.rightPad(string, OUTPUT_COLUMN_WIDTH, SPACE);
	}
	
	protected String rowString(String... strings) {
		StringBuilder stringBuilder = new StringBuilder();
		for (String string : strings) {
			stringBuilder.append(paddedString(string));
		}
		String result = stringBuilder.toString().trim();
		return String.format("%s\n", result);
	}
	
	protected void setOutputFileExtension(String outputFileExtension) {
		this.outputFileExtension = outputFileExtension;
	}
	
	public abstract String toString();
	
}