package simon.client.latency.testers;

//import java.io.IOException;
import java.applet.Applet;
import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.net.SocketAddress;
import java.net.SocketTimeoutException;

import javax.swing.SwingUtilities;

import org.apache.log4j.Logger;

import simon.client.latency.LatencyTester;
import simon.client.latency.NtpMessage;
import simon.client.latency.TestPoint;
import simon.client.latency.TestPointType;

public class TcpTester extends Tester {
	static Logger log = Logger.getLogger(TcpTester.class);
	//int NUM_SAMPLES=2;
	long INTERVAL = 1000;
	TestPoint testPoint;
	LatencyTester latencyTester;
	Applet applet;
	int nsamples;
	
	public TcpTester(Applet applet, LatencyTester latencyTester, TestPoint testPoint, int nsamples) {
		super.setName("TcpTester(" + testPoint.countryCode + testPoint.ip + ")");
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
				testPoint = getTcpLatency(testPoint);
				SwingUtilities.invokeAndWait(new Runnable() {
					public void run() {
						applet.repaint();
					}
				});
			}
			log.info("Finished nornally");
		} catch (Exception e) {
			log.error("Finished abnormaly:" + e);
		}
	}
	
	private TestPoint getTcpLatency(TestPoint testPoint) {
		Socket socket = null ;
		try {
			InetAddress ip = testPoint.ip;
			int port = 80;
			if (testPoint.testPointType == TestPointType.tcp_dns) port = 53;
			
			SocketAddress address = new InetSocketAddress(ip, port);
			//log.debug("address=" + address);
			long ti=System.currentTimeMillis();
			socket = new Socket();
			socket.connect(address);
			long dt=System.currentTimeMillis() - ti;
			socket.close();

			testPoint.addSample(dt);
			this.latencyTester.addCountrySamples(new Integer((int) dt));		
		} catch (Exception e) {
			log.warn(e.getMessage());
			testPoint.addLost();
		} finally {
			if (socket != null) {
				try {
					socket.close();
				} catch (IOException e) {
					log.error("error closing socket:" + e.getMessage());
				}
			}	
		}
		return testPoint;
		
	}
	
}
