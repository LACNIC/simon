package simon.client.latency;

//import java.io.IOException;
import javax.swing.SwingUtilities;
@Deprecated
public class AppletTester extends Thread {
	TestPoint sample;
	LatencyTester latencyTester;
	Applet applet;
	int num;
	AppletTester(Applet applet, LatencyTester latencyTester, TestPoint sample, int num) {
		this.applet = applet;
		this.sample = sample;
		this.latencyTester = latencyTester;
		this.num = num;
	}   
	
	public void run() {
		//System.out.println("Starting test " + sample);
        try {
        	for(int i=0; i<num; i++) {
        		if (i>0) {
        			Thread.sleep(16000); 
        		}
        		//sample = latencyTester.getLatency(sample);
       		     // System.out.println(sample);
                  SwingUtilities.invokeAndWait(new Runnable() {
      			    public void run() {
      				  applet.repaint();	
      			    }
                  });
                  // NTP servers generally have a rate limit...
                  // It would be better to put 16s here, but, in a real world
                  // it is possible to use less (about 5s, for example)
                  // At NTP.br we have a "2s between packets" limit, but a short
                  // burst of 1 packet per second is allowed.
              
        		   
        	}
        }
        catch (Exception e) {
            e.printStackTrace();
        }
        //System.out.println("Finish test " + sample);
    }
}
