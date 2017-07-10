package com.siddhantsutar.riscpipelinesimulator.core;

@SuppressWarnings("serial")
public class InvalidBinaryException extends Exception {

	public InvalidBinaryException(int length) {
		super(String.format("Invalid %s bit binary.", length));
	}
	
}