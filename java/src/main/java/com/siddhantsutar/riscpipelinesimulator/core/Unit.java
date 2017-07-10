package com.siddhantsutar.riscpipelinesimulator.core;

public abstract class Unit {
	
	private InterstageBuffer read; //Member variable since all subclasses require this
	
	public Unit(InterstageBuffer read) {
		this.read = read;
	}
	
	public InterstageBuffer getRead() {
		return read;
	}
		
}