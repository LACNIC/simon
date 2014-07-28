package simon.client.latency;

import java.awt.Color;
import java.awt.Component;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.RenderingHints;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Set;
import java.util.Map.Entry;

import javax.swing.JComponent;
import javax.swing.JLabel;
import javax.swing.JTable;
import javax.swing.table.DefaultTableCellRenderer;
import javax.swing.table.TableCellRenderer;

import org.apache.log4j.Logger;

public class LatencyCellRenderer extends DefaultTableCellRenderer implements TableCellRenderer {
	static Logger log=Logger.getLogger(LatencyCellRenderer.class);
	
	class RttBar extends JComponent {
		ArrayList<Integer> samples ;   
		int width;
		int maxRtt=1000;
		double xscale=3.5;
	    double yscale=16;
		void setSamples(ArrayList<Integer> samples) {
			this.samples = samples;
		}
		public RttBar(int width) {
			super();
			this.width=width;
			this.xscale = ((double)width/(double)maxRtt);
		}
		public void paintComponent(Graphics g) {
	          super.paintComponent(g);
	          
	          Graphics2D g2d = (Graphics2D) g;
	          g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
		      try {
		    	 drawGrid(g2d);
	             drawPoints(g2d);
		      }
		      catch (Exception e) {
		    	 log.error(e.getMessage(),e);
		    	 //log.debug(e);
		      }
		}
		private void drawGrid(Graphics2D g) {
	    	// draw vertical lines
	    	g.setColor(new Color(224,224,224));
	    	for (int delay=0; delay<maxRtt; delay+=100) {
	    		int x=(int) (delay*xscale);
	    		g.drawLine(x, 0, x, 100 );
	    	}
	    	g.setColor(new Color(240,240,240));
	    	for (int delay=50; delay<maxRtt; delay+=100) {
	    		int x=(int) (delay*xscale);
	    		g.drawLine(x, 0, x, 100 );
	    	}
	    	/*
	    	// draw x labels (time in ms)
	    	g.setColor(Color.darkGray);
	     	for (int delay=0; delay<1000; delay+=100) {
	     		g.drawString(Integer.toString(delay), 20+(int)(delay/xscale)-5, 10);
	    	}
	     	// draw horizontal lines 
	     	g.setColor(Color.lightGray);
	     	for (int country=0; country<=ncountries; country++) {
	     		g.drawLine(15, 30+(int)(country*yscale), 310, 30+(int)(country*yscale)); 
	    	}
	     	// draw yaxis labels (country codes)
	     	g.setColor(Color.darkGray);
	     	for (int country=0; country<ncountries; country++) {
	     		g.drawString(cc[country], 0, 43+(int)(country*yscale));
	    	}
	    	*/
	    }
		
		private void drawPoints(Graphics2D g){
	    	try {
	    		Color cyan = new Color(0,100,100);
	        	Color green = new Color(0,150,0);
	        	Color yellow = new Color(200,200,0);
	        	Color orange = new Color(180,120,0);
	        	Color red = new Color(200,0,0);
	        	Color magenta = new Color(100,0,100);
	        	//Set <Entry<Integer,List<Integer>>> set = this.points.entrySet ();
	        	//Iterator <Entry<Integer,List<Integer>>> it = set.iterator ();
	        	//while (it.hasNext ()){
	        		//Entry<Integer,List<Integer>> entry = it.next ();
	        		//Iterator <Integer> itDelay = entry.getValue ().iterator ();    		
	        		//while (itDelay.hasNext ()){
	        	synchronized (samples) {
	        		for(Integer delay:samples) {
	        			//int delay = itDelay.next ();
	        			//int country = entry.getKey ();    	    		
	        		    // colors
	        			double rand = 1+ Math.sin(delay*100);
	        			g.setColor(Color.black);
	        			if (delay>=600) g.setColor(magenta);
	        			if ((delay<600) & (rand>1)) g.setColor(red);
	        			if (delay<500) g.setColor(red);
	        			if ((delay<400) & (rand>1)) g.setColor(orange);
	        			if (delay<300) g.setColor(orange);
	        			if ((delay<250) & (rand>1)) g.setColor(yellow);
	        			if (delay<200) g.setColor(yellow);
	        			if ((delay<150) & (rand>1))g.setColor(green);
	    				if (delay<100) g.setColor(green);
	    				if (delay<50) g.setColor(cyan);
	    				int x= (int) (delay*this.xscale);	    				
	    				g.drawLine(x,0,x,100);
	    				g.drawLine(x+1,0,x+1,100);
	    				//g.fillOval(20+(int)(delay/xscale),5+(int)(yscale*0)+Math.abs((int)(Math.sin(delay*100)*6)), 4, 2);
	        	     }
	        	}
	        		
	        	//}
	    	} catch (Exception e) {
	    		log.error(e.getMessage(),e);
	    		//log.debug(e);
	    	}
	    	
	    }
	};
	RttBar rttBar;
	
	public LatencyCellRenderer(int width) {
		rttBar = new RttBar(width);
	}

	public Component getTableCellRendererComponent(JTable table, Object value, boolean isSelected, boolean hasFocus, int row, int column) {
		ArrayList<Integer> samples = (ArrayList<Integer>) value;
		rttBar.setSamples(samples);
		return rttBar;

	}
}
