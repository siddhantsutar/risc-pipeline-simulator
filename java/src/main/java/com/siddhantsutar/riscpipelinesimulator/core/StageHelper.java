package com.siddhantsutar.riscpipelinesimulator.core;

import com.google.common.collect.ClassToInstanceMap;
import com.google.common.collect.MutableClassToInstanceMap;

public class StageHelper<B> {
	
	private ClassToInstanceMap<B> map;

	public <T extends B> StageHelper(T... args) {
		map = MutableClassToInstanceMap.create();
		for (int i = 0; i < args.length; i++) {
			map.put((Class<? extends B>) args[i].getClass(), args[i]);
		}
	}

	public <T extends B> T getInstance(Class<T> clazz) {
		return map.getInstance(clazz);
	}

}