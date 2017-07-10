package com.siddhantsutar.riscpipelinesimulator.core;

import java.awt.GridLayout;
import java.awt.event.ActionListener;
import javax.swing.BorderFactory;
import javax.swing.JButton;
import javax.swing.JCheckBox;
import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTextArea;
import javax.swing.JTextField;
import javax.swing.border.TitledBorder;
import org.jdesktop.xswingx.PromptSupport;

@SuppressWarnings("serial")
public class RiscPipelineSimulatorView extends JFrame {

	private JButton btnFileChooser = new JButton("..");
	private JButton btnSimulate = new JButton("Simulate");
	private JCheckBox chkDataMemory = new JCheckBox("Use default values");
	private JCheckBox chkRegisterFile = new JCheckBox("Use default values");
	private JCheckBox chkTrace = new JCheckBox("Display trace");
	private JPanel pnlColumn1 = new JPanel(new GridLayout(11, 1, 1, 1));
	private JPanel pnlColumn2 = new JPanel(new GridLayout(11, 2, 1, 1));
	private JPanel pnlColumn3 = new JPanel(new GridLayout(11, 1, 1, 1));
	private JPanel pnlColumn4 = new JPanel(new GridLayout(11, 1, 1, 1));
	private JPanel pnlMain = new JPanel(new GridLayout(1, 5, 1, 1));
	private JTextArea txtTrace = new JTextArea();
	private JScrollPane scrTrace = new JScrollPane(txtTrace);
	private JTextField txtInput = new JTextField(15);
	private JTextField txtOutput = new JTextField(15);
	private JTextField txtDataMemory1 = new JTextField(15);
	private JTextField txtDataMemory2 = new JTextField(15);
	private JTextField txtDataMemory3 = new JTextField(15);
	private JTextField txtDataMemory4 = new JTextField(15);
	private JTextField txtDataMemory5 = new JTextField(15);
	private JTextField txtDataMemory6 = new JTextField(15);
	private JTextField txtDataMemory7 = new JTextField(15);
	private JTextField txtDataMemory8 = new JTextField(15);
	private JTextField txtDataMemory9 = new JTextField(15);
	private JTextField txtDataMemory10 = new JTextField(15);
	private JTextField txtRegisterFile1 = new JTextField(15);
	private JTextField txtRegisterFile2 = new JTextField(15);
	private JTextField txtRegisterFile3 = new JTextField(15);
	private JTextField txtRegisterFile4 = new JTextField(15);
	private JTextField txtRegisterFile5 = new JTextField(15);
	private JTextField txtRegisterFile6 = new JTextField(15);
	private JTextField txtRegisterFile7 = new JTextField(15);
	private JTextField txtRegisterFile8 = new JTextField(15);

	public RiscPipelineSimulatorView() {
		setDefaultCloseOperation(EXIT_ON_CLOSE);
		setLocationRelativeTo(null);
		setTitle("RISC Pipeline Simulator");
		txtTrace.setEditable(false);
		txtTrace.setLineWrap(true);
		PromptSupport.setPrompt("Input .mips file", txtInput);
		PromptSupport.setPrompt("Output directory", txtOutput);
		PromptSupport.setPrompt("Register 1 value", txtRegisterFile1);
		PromptSupport.setPrompt("Register 2 value", txtRegisterFile2);
		PromptSupport.setPrompt("Register 3 value", txtRegisterFile3);
		PromptSupport.setPrompt("Register 4 value", txtRegisterFile4);
		PromptSupport.setPrompt("Register 5 value", txtRegisterFile5);
		PromptSupport.setPrompt("Register 6 value", txtRegisterFile6);
		PromptSupport.setPrompt("Register 7 value", txtRegisterFile7);
		PromptSupport.setPrompt("Register 8 value", txtRegisterFile8);
		PromptSupport.setPrompt("Data 1 value", txtDataMemory1);
		PromptSupport.setPrompt("Data 2 value", txtDataMemory2);
		PromptSupport.setPrompt("Data 3 value", txtDataMemory3);
		PromptSupport.setPrompt("Data 4 value", txtDataMemory4);
		PromptSupport.setPrompt("Data 5 value", txtDataMemory5);
		PromptSupport.setPrompt("Data 6 value", txtDataMemory6);
		PromptSupport.setPrompt("Data 7 value", txtDataMemory7);
		PromptSupport.setPrompt("Data 8 value", txtDataMemory8);
		PromptSupport.setPrompt("Data 9 value", txtDataMemory9);
		PromptSupport.setPrompt("Data 10 value", txtDataMemory10);
	    TitledBorder title = BorderFactory.createTitledBorder("Register File");
	    title.setTitleJustification(TitledBorder.CENTER);
	    title.setTitlePosition(TitledBorder.TOP);
	    pnlColumn3.setBorder(title);
	    title = BorderFactory.createTitledBorder("Data Memory");
	    title.setTitleJustification(TitledBorder.CENTER);
	    title.setTitlePosition(TitledBorder.TOP);
	    pnlColumn4.setBorder(title);
	    title = BorderFactory.createTitledBorder("Simulation Trace");
	    title.setTitleJustification(TitledBorder.CENTER);
	    title.setTitlePosition(TitledBorder.TOP);
	    scrTrace.setBorder(title);
	    
	    pnlColumn1.add(txtInput);
	    pnlColumn1.add(txtOutput);
	    pnlColumn1.add(chkTrace);
	    pnlColumn1.add(btnSimulate);
	    
	    pnlColumn2.add(btnFileChooser);
	    Placeholder.add(pnlColumn2, 21);
		
		pnlColumn3.add(txtRegisterFile1);
		pnlColumn3.add(txtRegisterFile2);
		pnlColumn3.add(txtRegisterFile3);
		pnlColumn3.add(txtRegisterFile4);
		pnlColumn3.add(txtRegisterFile5);
		pnlColumn3.add(txtRegisterFile6);
		pnlColumn3.add(txtRegisterFile7);
		pnlColumn3.add(txtRegisterFile8);
		Placeholder.add(pnlColumn3, 2);
		pnlColumn3.add(chkRegisterFile);
		
		pnlColumn4.add(txtDataMemory1);
		pnlColumn4.add(txtDataMemory2);
		pnlColumn4.add(txtDataMemory3);
		pnlColumn4.add(txtDataMemory4);
		pnlColumn4.add(txtDataMemory5);
		pnlColumn4.add(txtDataMemory6);
		pnlColumn4.add(txtDataMemory7);
		pnlColumn4.add(txtDataMemory8);
		pnlColumn4.add(txtDataMemory9);
		pnlColumn4.add(txtDataMemory10);
		pnlColumn4.add(chkDataMemory);
				
		pnlMain.add(pnlColumn1);
		pnlMain.add(pnlColumn2);
		pnlMain.add(pnlColumn3);
		pnlMain.add(pnlColumn4);
		pnlMain.add(scrTrace);
		this.add(pnlMain);
		this.pack();
	}
	
	public void addRiscPipelineSimulatorListener(ActionListener listener) {
		btnFileChooser.addActionListener(listener);
		btnSimulate.addActionListener(listener);
		chkRegisterFile.addActionListener(listener);
		chkDataMemory.addActionListener(listener);
	}
	
	public JButton getBtnFileChooser() {
		return btnFileChooser;
	}
	
	public JButton getBtnSimulate() {
		return btnSimulate;
	}

	public JCheckBox getChkDataMemory() {
		return chkDataMemory;
	}
	
	public JCheckBox getChkRegisterFile() {
		return chkRegisterFile;
	}

	public JCheckBox getChkTrace() {
		return chkTrace;
	}
	
	public JTextField getTxtInput() {
		return txtInput;
	}
	
	public JTextField getTxtOutput() {
		return txtOutput;
	}
	
	public JTextField[] getArrayTxtDataMemory() {
		return new JTextField[]{
				txtDataMemory1,
				txtDataMemory2,
				txtDataMemory3,
				txtDataMemory4,
				txtDataMemory5,
				txtDataMemory6,
				txtDataMemory7,
				txtDataMemory8,
				txtDataMemory9,
				txtDataMemory10
		};
	}
	
	public JTextField[] getArrayTxtRegisterFile() {
		return new JTextField[]{
				txtRegisterFile1,
				txtRegisterFile2,
				txtRegisterFile3,
				txtRegisterFile4,
				txtRegisterFile5,
				txtRegisterFile6,
				txtRegisterFile7,
				txtRegisterFile8
		};
	}
	
	public void setTxtTrace(String text) {
		txtTrace.append(String.format("%s\n", text));
	}

}