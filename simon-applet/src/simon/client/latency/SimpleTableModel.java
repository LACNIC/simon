package simon.client.latency;

import javax.swing.event.TableModelListener;
import javax.swing.table.TableModel;

public class SimpleTableModel implements TableModel {

	LatencyTester[] countryLatencyTester;
	int nocountries;
	
	public SimpleTableModel(LatencyTester[] countries, int nocountries) {
		this.countryLatencyTester=countries;
		this.nocountries=nocountries;
	}
		
	public boolean isCellEditable(int rowIndex, int columnIndex) {
		return false;
	}
	
	public int getColumnCount() {
		return LatencyTester.columnNamesSimple.length;
	}

	public String getColumnName(int columnIndex) {
		return LatencyTester.columnNamesSimple[columnIndex];
	}
	
	public int getRowCount() {
		return this.nocountries;
	}

	public Class<?> getColumnClass(int columnIndex) {
		return LatencyTester.getColumnClassSimple(columnIndex);
	}

	public Object getValueAt(int rowIndex, int columnIndex) {
		return countryLatencyTester[rowIndex].getColumnSimple(columnIndex);
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
}
