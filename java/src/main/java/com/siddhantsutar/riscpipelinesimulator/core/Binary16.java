package com.siddhantsutar.riscpipelinesimulator.core;

import org.apache.commons.lang3.StringUtils;

public class Binary16 extends Binary {

	private static final int SIZE = 16;
	private static final char ZERO = '0';
	
	public Binary16() {
		super(StringUtils.repeat(ZERO, SIZE));
	}
	
	public Binary16(String data) throws InvalidBinaryException {
		super(data);
		if (data.length() != SIZE) {
			throw new InvalidBinaryException(SIZE);
		}
	}
	
	public Binary16(String data, BinaryExtendType binaryExtendType) {
		super(binaryExtendType == BinaryExtendType.SIGN ? StringUtils.leftPad(data, SIZE, data.charAt(0))
				: (binaryExtendType == BinaryExtendType.ZERO ? StringUtils.leftPad(data, SIZE, ZERO) : null));
	}
	
}