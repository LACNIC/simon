package simon.client.latency;

import javax.swing.event.TableModelListener;
import javax.swing.table.TableModel;

public class AllTableModel implements TableModel {

	LatencyTester[] countries;
	int nocountries;
	
	public AllTableModel(LatencyTester[] countries, int nocountries) {
		this.countries=countries;
		this.nocountries=nocountries;
	}
		
	public boolean isCellEditable(int rowIndex, int columnIndex) {
		return false;
	}
	
	public int getColumnCount() {
		return LatencyTester.columnNamesDetailed.length;
	}

	public String getColumnName(int columnIndex) {
		return LatencyTester.columnNamesDetailed[columnIndex];
	}
	
	public int getRowCount() {
		return this.nocountries;
	}

	public Class<?> getColumnClass(int columnIndex) {
		return LatencyTester.getColumnClass(columnIndex);
	}

	public Object getValueAt(int rowIndex, int columnIndex) {
		return countries[rowIndex].getColumn(columnIndex);
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
