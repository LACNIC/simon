package simon.client.latency;

import javax.swing.event.TableModelListener;
import javax.swing.table.TableModel;

public class LatencyTableModel implements TableModel {

	LatencyTester latencyTester;
	
	public LatencyTableModel(LatencyTester latencyTester) {
		this.latencyTester=latencyTester;
	}

	public void addTableModelListener(TableModelListener l) {
		// TODO Auto-generated method stub
	}

	public void removeTableModelListener(TableModelListener l) {
		// TODO Auto-generated method stub
	}

	public void setValueAt(Object value, int rowIndex, int columnIndex) {
		// TODO Auto-generated method stub
	}
	
	public boolean isCellEditable(int rowIndex, int columnIndex) {
		return false;
	}
	
	public int getColumnCount() {
		return LatencyLocation.columnNames.length;
	}

	public String getColumnName(int columnIndex) {
		return LatencyLocation.columnNames[columnIndex];
	}
	
	public int getRowCount() {
		return this.latencyTester.testPoints.size();
	}

	public Class<?> getColumnClass(int columnIndex) {
		return LatencyLocation.getColumnClass(columnIndex);
	}

	public Object getValueAt(int rowIndex, int columnIndex) {
		TestPoint sample = this.latencyTester.testPoints.get(rowIndex);
		return sample.getColumn(columnIndex);
	}
}
