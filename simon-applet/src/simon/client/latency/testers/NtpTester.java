package simon.client.latency.testers;

//import java.io.IOException;
import java.applet.Applet;
import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.SocketTimeoutException;

import org.apache.log4j.Logger;

import simon.client.latency.LatencyTester;
import simon.client.latency.NtpMessage;
import simon.client.latency.TestPoint;

public class NtpTester extends Tester {
	static Logger log = Logger.getLogger(NtpTester.class);
	//int NUM_SAMPLES=2;
	long INTERVAL=16000;
	TestPoint testPoint;
	LatencyTester latencyTester;
	Applet applet;
	int nsamples;
	 // with something about 200 servers, 5 samples
    // appear to be a very reasonable amount...
    // we are getting a sample each 16s per server,
    // what gives us a total time of 1.5 min.
    // it is ok, isn't it?
	
	public NtpTester(Applet applet, LatencyTester latencyTester, TestPoint testPoint, int nsamples) {
		super.setName("NtpTester(" + testPoint.countryCode + testPoint.ip + ")");
		this.applet = applet;
		this.testPoint = testPoint;
		this.latencyTester = latencyTester;
		this.nsamples=nsamples;
	}  
	
	public void run() {
		log.info("Starting");
		try {
			for (int i = 0; i < nsamples; i++) {
				if (i > 0) {
					Thread.sleep(INTERVAL);
				}
				testPoint = getUDPLatency(testPoint);
				applet.repaint();
				/*SwingUtilities.invokeAndWait(new Runnable() {
					public void run() {
						applet.repaint();
					}
				});*/
				// NTP servers generally have a rate limit...
				// It would be better to put 16s here, but, in a real world
				// it is possible to use less (about 5s, for example)
				// At NTP.br we have a "2s between packets" limit, but a short
				// burst of 1 packet per second is allowed.

			}
			log.info("Finished nornally");
		} catch (Exception e) {
			log.error("Finished abnormaly:" + e);
		}
	}
	
	private TestPoint getUDPLatency(TestPoint testPoint) throws IOException, InterruptedException {
		// wait a bit (the same amount between tests)...
		// I think it could help not to create local buffers for the sent packets,
		// that could cause some delay and imprecision
		// It should give the user the feeling of a continuous testing...
		int time = 1 + (int)(Math.random() * 16000);
		Thread.sleep(time); 
		// Send request
		long rtt;
		DatagramSocket socket = new DatagramSocket();
		InetAddress address = testPoint.ip;
		byte[] buf = new NtpMessage().toByteArray();

		try {	
			socket.setSoTimeout(2000); // wait (max) two seconds for a response
			// Transmits
			DatagramPacket packet = new DatagramPacket(buf, buf.length, address, 123);
			NtpMessage.encodeTimestamp(packet.getData(), 40, (System.nanoTime()/1000000000.0) + 2208988800.0);	
			long ti=System.currentTimeMillis();
			socket.send(packet);
			// Get response
			packet = new DatagramPacket(buf, buf.length);
			socket.receive(packet);	
		    rtt=System.currentTimeMillis()-ti;
		    double destinationTimestamp = (System.nanoTime()/1000000000.0) + 2208988800.0;	
		    /*
		    Testing to see if we avoid the ~1800ms times. 
		    // We only need to calculate RTT...
		    // The local time not need to be accurate to do it!
		    NtpMessage msg = new NtpMessage(packet.getData());
		    Double dt = 1000*((destinationTimestamp-msg.originateTimestamp) - (msg.transmitTimestamp-msg.receiveTimestamp));
		    rtt = dt.longValue();	
		    */	 
		}
		catch (SocketTimeoutException e) {
			log.warn(e.getMessage());
			rtt = -1;
			testPoint.addLost();
		}  
		finally {
			if (socket != null) {
				socket.close();
			}
		}
	
		if (rtt != -1) {
			testPoint.addSample(rtt);
			this.latencyTester.addCountrySamples(new Integer((int)rtt));
		}
		return testPoint;	      
	}
	
}
