package simon.client.latency;

import java.awt.Color;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.RenderingHints;

import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.Map.Entry;
import java.util.Iterator;

import javax.swing.JComponent;
import javax.swing.JLabel;

import org.apache.log4j.Logger;

@Deprecated
public class Graph extends JComponent{
	
	private static final long serialVersionUID = 1L;
	static Logger log = Logger.getLogger(Graph.class);
	
    int stop;
    int noPoints = 0;
    private Map<Integer,List<Integer>> points;
    double xscale=3.5;
    double yscale=16;
    String cc[];
    int ncountries=0;
    
    public Graph(Country[] countries) {
    	super();
       	points = new HashMap<Integer,List<Integer>>();
       	this.cc = new String[countries.length];
       	for(Country country:countries) {
       		this.cc[this.ncountries++] = country.countryCode;
       	}
    }

    public void paintComponent(Graphics g) {
          super.paintComponent(g);
          Graphics2D g2d = (Graphics2D) g;
          g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
	      drawGrid(g2d);
	      try {
            drawPoints(g2d);
	      }
	      catch (Exception e) {
	    	  e.printStackTrace();
	      }
	}
    
    private void drawGrid(Graphics2D g) {
    	// draw vertical lines
    	g.setColor(Color.darkGray);
    	for (int delay=0; delay<1100; delay+=100) {
    		g.drawLine(20+(int)(delay/xscale), 15, 20+(int)(delay/xscale), 370 );
    	}
    	g.setColor(Color.lightGray);
    	for (int delay=50; delay<1000; delay+=100) {
    		g.drawLine(20+(int)(delay/xscale), 25, 20+(int)(delay/xscale), 370 );
    	}
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
    }
    
    private void drawPoints(Graphics2D g){
    	try {
    		Color cyan = new Color(0,100,100);
        	Color green = new Color(0,150,0);
        	Color yellow = new Color(200,200,0);
        	Color orange = new Color(180,120,0);
        	Color red = new Color(200,0,0);
        	Color magenta = new Color(100,0,100);
        	Set <Entry<Integer,List<Integer>>> set = this.points.entrySet ();
        	Iterator <Entry<Integer,List<Integer>>> it = set.iterator ();
        	while (it.hasNext ()){
        		Entry<Integer,List<Integer>> entry = it.next ();
        		Iterator <Integer> itDelay = entry.getValue ().iterator ();    		
        		while (itDelay.hasNext ()){
        			int delay = itDelay.next ();
        			int country = entry.getKey ();    	    		
        		    // colors
        			double rand = 1+ Math.sin(delay*100);
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
    				g.fillOval(20+(int)(delay/xscale),36+(int)(yscale*country)+Math.abs((int)(Math.sin(delay*100)*6)), 4, 2);
        	     }
        	}
    	} catch (Exception e) {
    		log.error(e.getCause());
    		log.debug(e);
    	}
    	
    }
    
	void addSample(int country, long delay) throws InterruptedException {
	       if (points.get(country)==null) {
	        	points.put(country, new LinkedList<Integer>());
	        }
	        points.get(country).add((int)delay);
	}

}
