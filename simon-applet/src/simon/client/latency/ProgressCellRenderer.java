package simon.client.latency;

import java.awt.Color;
import java.awt.Component;
import java.awt.Font;

import javax.swing.JProgressBar;
import javax.swing.JTable;
import javax.swing.table.TableCellRenderer;

public class ProgressCellRenderer implements TableCellRenderer {
	JProgressBar progressBar = new JProgressBar(0,100);

	public JProgressBar getProgressBar() {
		return progressBar;
	}

	public Component getTableCellRendererComponent(JTable table, Object value, boolean isSelected, boolean hasFocus, int row, int column) {
		int progress = (Integer) value;
		
		synchronized (progressBar) {
			progressBar.setFont(new Font(null, Font.PLAIN, 10));
			progressBar.setStringPainted(true);
			if (0<= progress && progress<=100) {
				progressBar.setString(null);
				progressBar.setValue(progress);
			} else {
				progressBar.setValue(100);
				if (progress<0) {
					progressBar.setString("error");
					progressBar.setForeground(Color.yellow);
				}
				if (progress==200) {
					progressBar.setString("wait");
					progressBar.setForeground(Color.orange);
				}
				if (progress==300) {
					progressBar.setString("done");
					progressBar.setForeground(Color.green);
				}
				if (progress==400) {
					progressBar.setString("No Points");
					progressBar.setForeground(Color.red);
				}
			}
		}
		return progressBar;
	}
}
