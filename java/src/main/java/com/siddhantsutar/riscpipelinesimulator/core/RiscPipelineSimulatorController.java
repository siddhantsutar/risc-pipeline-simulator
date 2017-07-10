package com.siddhantsutar.riscpipelinesimulator.core;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.util.Observable;
import java.util.Observer;
import javax.swing.JCheckBox;
import javax.swing.JTextField;

public class RiscPipelineSimulatorController implements Observer {

	private RiscPipelineSimulatorView view;
	private RiscPipelineSimulatorModel model;

	public RiscPipelineSimulatorController(RiscPipelineSimulatorView view, RiscPipelineSimulatorModel model) {
		this.view = view;
		this.model = model;
		view.addRiscPipelineSimulatorListener(new RiscPipelineSimulatorListener());
	}

	private void setTextFields(JCheckBox checkBox, Binary[] defaultValues, JTextField[] arrayTxt) {
		if (checkBox.isSelected()) {
			int i = 0;
			for (JTextField textField : arrayTxt) {
				textField.setText(defaultValues[i++].toString());
				textField.setEditable(false);
			}
		} else {
			for (JTextField textField : arrayTxt) {
				textField.setEditable(true);
			}
		}
	}
	
	@Override public void update(Observable o, Object arg) {
		if (view.getChkTrace().isSelected()) {
			view.setTxtTrace((String) arg);
		}
	}

	class RiscPipelineSimulatorListener implements ActionListener {

		@Override public void actionPerformed(ActionEvent arg0) {
			Object source = arg0.getSource();
			JCheckBox chkRegisterFile = view.getChkRegisterFile();
			JCheckBox chkDataMemory = view.getChkDataMemory();
			try {
				if (source == view.getBtnFileChooser()) {
					FileChooser fileChooser = new FileChooser(view.getTxtInput());
				} else if (source == view.getBtnSimulate()) {
					view.getChkTrace().setEnabled(false);
					JTextField[] arrayTxtRegisterFile = view.getArrayTxtRegisterFile();
					JTextField[] arrayTxtDataMemory = view.getArrayTxtDataMemory();
					Binary16[] registerFile = new Binary16[arrayTxtRegisterFile.length];
					Binary8[] dataMemory = new Binary8[arrayTxtDataMemory.length];
					for (int i = 0; i < registerFile.length; i++) {
						registerFile[i] = new Binary16(arrayTxtRegisterFile[i].getText());
					}
					for (int i = 0; i < dataMemory.length; i++) {
						dataMemory[i] = new Binary8(arrayTxtDataMemory[i].getText());
					}
					model.initMemory(view.getTxtInput().getText(), registerFile, dataMemory);
					model.simulate(view.getTxtOutput().getText());
					view.getChkTrace().setEnabled(true);
				} else if (source == chkDataMemory) {
					setTextFields(chkDataMemory, model.getDefaultDataMemoryValues(), view.getArrayTxtDataMemory());
				} else if (source == chkRegisterFile) {
					setTextFields(chkRegisterFile, model.getDefaultRegisterFileValues(), view.getArrayTxtRegisterFile());
				}
			} catch (InvalidBinaryException e) {
				new ErrorHandler(e);
			}
		}

	}

}