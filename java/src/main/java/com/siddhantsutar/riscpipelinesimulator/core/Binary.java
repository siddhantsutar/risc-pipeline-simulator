package com.siddhantsutar.riscpipelinesimulator.core;

public class Binary {

	private String binaryString;
	private int data;
	
	public Binary(String binaryString) {
		this.binaryString = binaryString;
		this.data = Integer.parseInt(binaryString, 2);
	}

	public int getData() {
		return data;
	}

	public String subBitString(int start, int end) {
		return binaryString.substring(start, end);
	}
	
	public String toFormattedString() {
		StringBuilder result = new StringBuilder();
		for (int i = 0; i < binaryString.length(); i += 4) {
			int end = i + 4;
			if (end > binaryString.length()) {
				end = binaryString.length();
			}
			result.append(binaryString.substring(i, end));
			result.append(' ');
		}
		return result.toString().trim();
	}

	@Override public boolean equals(Object o) {
		if (o == null || getClass() != o.getClass()) {
			return false;
		}
		Binary obj = (Binary) o;
		return binaryString.equals(obj.binaryString); 
	}

	@Override public String toString() {
		return binaryString;
	}

}