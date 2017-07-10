package com.siddhantsutar.riscpipelinesimulator.core;

public class Binary8 extends Binary {

	public Binary8(String data) throws InvalidBinaryException {
		super(data);
		if (data.length() != 8) {
			throw new InvalidBinaryException(8);
		}
	}
	
}