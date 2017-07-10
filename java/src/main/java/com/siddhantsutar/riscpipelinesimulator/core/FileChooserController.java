package com.siddhantsutar.riscpipelinesimulator.core;

public class FileChooserController {

	private FileChooserViewModel viewModel;
	
	public FileChooserController(FileChooserViewModel viewModel) {
		this.viewModel = viewModel;
		viewModel.setVisible(true);
		if (viewModel.getResult() == viewModel.getApproveOption()) {
			viewModel.getTextField().setText(viewModel.getSelectedFile().getAbsolutePath());
		}
	}
	
}