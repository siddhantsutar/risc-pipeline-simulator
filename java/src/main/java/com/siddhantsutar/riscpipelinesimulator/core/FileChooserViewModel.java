package com.siddhantsutar.riscpipelinesimulator.core;

import javax.swing.JFileChooser;
import javax.swing.JTextField;

@SuppressWarnings("serial")
public class FileChooserViewModel extends JFileChooser {

	private int result;
	private JTextField textField;
	
	public int getApproveOption() {
		return JFileChooser.APPROVE_OPTION;
	}
	
	public int getResult() {
		return result;
	}
	
	public JTextField getTextField() {
		return textField;
	}
	
	public void setTextField(JTextField textField) {
		this.textField = textField;
	}
	
	@Override public void setVisible(boolean aFlag) {
		if (aFlag) {
			result = showOpenDialog(this);
		}
	}

}