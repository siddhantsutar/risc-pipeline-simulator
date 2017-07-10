package com.siddhantsutar.riscpipelinesimulator.core;

import javax.swing.JTextField;

public class FileChooser {

	public FileChooser(JTextField textField) {
		FileChooserViewModel viewModel = new FileChooserViewModel();
		viewModel.setTextField(textField);
		FileChooserController controller = new FileChooserController(viewModel);
	}
	
}