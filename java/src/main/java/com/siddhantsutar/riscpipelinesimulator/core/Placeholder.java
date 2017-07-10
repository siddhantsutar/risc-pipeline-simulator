package com.siddhantsutar.riscpipelinesimulator.core;

import javax.swing.JLabel;
import javax.swing.JPanel;

@SuppressWarnings("serial")
public class Placeholder extends JLabel {

	public Placeholder() {
		super();
		super.setEnabled(false);
	}
	
	public static void add(JPanel panel, int count) {
		for (int i = 0; i < count; i++) {
			panel.add(new Placeholder());
		}
	}
	
}