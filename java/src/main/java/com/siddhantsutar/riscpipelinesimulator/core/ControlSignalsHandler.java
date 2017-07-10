package com.siddhantsutar.riscpipelinesimulator.core;

import java.util.HashMap;
import java.util.Map;

public class ControlSignalsHandler {

	private Map<ControlSignal, ControlSignalValue> data;
	
	@SafeVarargs
	public <T extends ControlSignal> ControlSignalsHandler(Class<? extends T>... args) {
		this(ControlSignalValue.NONE, args);
	}
	
	// <? extends T> because of the special case of generic varargs of type Class; otherwise, just <T> works
	@SafeVarargs
	public <T extends ControlSignal> ControlSignalsHandler(ControlSignalValue value, Class<? extends T>... args) {
		data = new HashMap<>();
		for (int i = 0; i < args.length; i++) {
			for (T each : args[i].getEnumConstants()) {
				data.put(each, value);
			}
		}
	}
	
	public void copyValueFrom(ControlSignalsHandler controlSignalsHandler, ControlSignal controlSignal) {
		data.put(controlSignal, controlSignalsHandler.get(controlSignal));
	}
	
	public ControlSignalValue get(ControlSignal controlSignal) {
		return data.get(controlSignal);
	}
	
	public Map<ControlSignal, ControlSignalValue> getData() {
		return data;
	}
	
	public boolean isEmpty() {
		for (ControlSignalValue value : data.values()) {
			if (value != ControlSignalValue.NONE) {
				return false;
			}
		}
		return true;
	}
	
	public void put(ControlSignal controlSignal, ControlSignalValue value) {
		data.put(controlSignal, value);
	}
	
	public void setFalse(ControlSignal controlSignal) {
		data.put(controlSignal, ControlSignalValue.FALSE);
	}
	
	public void setInvalid(ControlSignal controlSignal) {
		data.put(controlSignal, ControlSignalValue.INVALID);
	}
	
	public void setTrue(ControlSignal controlSignal) {
		data.put(controlSignal, ControlSignalValue.TRUE);
	}
	
}