package com.siddhantsutar.riscpipelinesimulator.core;

public class ArithmeticLogicUnit extends Unit {

	private ArithmeticLogicControlUnit arithmeticLogicControlUnit;
	private InterstageBuffer write;
	
	public ArithmeticLogicUnit(InterstageBuffer read) {
		super(read);
	}
	
	public ArithmeticLogicUnit(InterstageBuffer read, InterstageBuffer write) {
		this(read);
		arithmeticLogicControlUnit = new ArithmeticLogicControlUnit(read);
		this.write = write;
	}

	public void use(Binary16 binary1, Binary16 binary2) throws InvalidBinaryException {
		int result = 0;
		int decimal1 = binary1.getData();
		int decimal2 = binary2.getData();
		if (binary1.toString().charAt(0) == '1') {
			decimal1 = decimal1 - (1 << 16);
		}
		if (binary2.toString().charAt(0) == '1') {
			decimal2 = decimal2 - (1 << 16);
		}
		Binary operation = arithmeticLogicControlUnit.use();
		switch (operation.toString()) {
			case "100":
				result = decimal1 + decimal2;
				break;
			case "101":
				result = decimal1 & decimal2;
				break;
			case "110":
				result = decimal1 | decimal2;
				break;
			case "111":
				result = decimal1 < decimal2 ? 1 : 0;
				break;
			case "000":
				result = decimal1 ^ decimal2;
				break;
			case "001":
				result = decimal1 << getRead().getIdEx().getRt().getData();
				break;
			case "010":
				result = decimal1 >> getRead().getIdEx().getRt().getData();
				break;
			case "011":
				result = decimal1 - decimal2;
				break;
		}
		write.getExMem().setAluResult(new Binary16(Integer.toBinaryString(result), BinaryExtendType.ZERO));
	}
	
}