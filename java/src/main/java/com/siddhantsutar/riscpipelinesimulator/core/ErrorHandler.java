package com.siddhantsutar.riscpipelinesimulator.core;

import javax.swing.JOptionPane;

public class ErrorHandler {

	public ErrorHandler(Exception e) {
		JOptionPane.showMessageDialog(null, String.format("%s: %s", e.getClass().getName(), e.getMessage()), "Error", JOptionPane.INFORMATION_MESSAGE);
	}
	
}