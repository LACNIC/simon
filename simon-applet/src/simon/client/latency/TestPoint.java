package simon.client.latency;

import java.net.Inet4Address;
import java.net.Inet6Address;
import java.net.InetAddress;
import java.net.UnknownHostException;
import java.util.ArrayList;
import java.util.Collections;

import org.json.simple.JSONObject;

import org.json.simple.*;

public class TestPoint {
	ArrayList<Long> samples = new ArrayList<Long>();
	int nlost = 0;

	Integer id;
	String description;
	public TestPointType testPointType = null;
	public InetAddress ip;
	public String countryCode;
	String creationTime;
	int ipVersion;

	/**
	 * Constructs from the line coming from the server
	 * 
	 * @param line
	 * @throws Exception
	 */
	public TestPoint(String line) throws Exception {
		String[] t = line.split(",");
		if (t == null)
			throw new Exception("empty record from server");
		if (t.length != 6)
			throw new Exception("Invalid record from server:" + line + "("
					+ t.length + ")");

		try {
			this.id = Integer.parseInt(t[0]);
			this.description = t[1];
			if ("ntp".equalsIgnoreCase(t[2]))
				this.testPointType = TestPointType.ntp;
			if ("tcp_dns".equalsIgnoreCase(t[2]))
				this.testPointType = TestPointType.tcp_dns;
			if ("tcp_web".equalsIgnoreCase(t[2]))
				this.testPointType = TestPointType.tcp_web;
			this.ip = InetAddress.getByName(t[3]);

			if (this.ip.getClass() == Inet4Address.class) {
				this.ipVersion = 4;
			} else if (this.ip.getClass() == Inet6Address.class) {
				this.ipVersion = 6;
			}

			this.countryCode = t[4];
			this.creationTime = t[5];
		} catch (Exception e) {
			throw new Exception("Error parsing record:" + line);
		}

	}

	public TestPoint(JSONObject jsonObject){
		id = new Integer(jsonObject.get("index").toString());
		description = jsonObject.get("description").toString();
		
		String testtype = jsonObject.get("testtype").toString();
		if ("ntp".equalsIgnoreCase(testtype)) 
			this.testPointType = TestPointType.ntp;
		if ("tcp_dns".equalsIgnoreCase(testtype)) 
			this.testPointType = TestPointType.tcp_dns;
		if ("tcp_web".equalsIgnoreCase(testtype)) 
			this.testPointType = TestPointType.tcp_web;
		
		
		String jsonIP = jsonObject.get("ip_address").toString();
		try{
			ip = InetAddress.getByName(jsonIP);
		}catch(UnknownHostException e){
			System.err.println("Couldn't resolve host " + jsonIP + "Exception: " + e);
		}
		
		countryCode = jsonObject.get("countryCode").toString();
		creationTime = jsonObject.get("date_added").toString();
		
		if (this.ip.getClass() == Inet4Address.class) {
			this.ipVersion = 4;
		} else if (this.ip.getClass() == Inet6Address.class) {
			this.ipVersion = 6;
		}
	}

	static String[] columnNames = { "Destination", "min", "median", "avg",
			"max", "samples", "losts", "stddev" };

	public int getNumSamples() {
		return this.samples.size();
	}

	public int getLost() {
		return nlost;
	}

	public long getAverage() {
		if (getNumSamples() == 0)
			return -1;
		long accum = 0;
		for (Long sample : samples) {
			accum += (long) sample;
		}
		return (accum / getNumSamples());
	}

	public long getMinimum() {
		if (getNumSamples() == 0)
			return -1;
		ArrayList<Long> myArray = samples;
		Collections.sort(myArray);
		return (myArray.get(0));
	}

	public long getMaximum() {
		if (getNumSamples() == 0)
			return -1;
		ArrayList<Long> myArray = samples;
		Collections.sort(myArray);
		Collections.reverse(myArray);
		return (myArray.get(0));
	}

	public long getMedian() {
		if (getNumSamples() == 0)
			return -1;
		ArrayList<Long> myArray = samples;
		Collections.sort(myArray);
		int arrayLength = 0;
		long arrayMedian = 0;
		int currentIndex = 0;
		arrayLength = myArray.size();
		if (arrayLength % 2 != 0) {
			currentIndex = ((arrayLength / 2) + 1);
			arrayMedian = myArray.get(currentIndex - 1);
		} else {
			int indexOne = (arrayLength / 2);
			int indexTwo = arrayLength / 2 + 1;
			long arraysSum = myArray.get(indexOne - 1)
					+ myArray.get(indexTwo - 1);
			arrayMedian = arraysSum / 2;
		}
		return arrayMedian;
	}

	public long getStdDev() {
		if (getNumSamples() == 0)
			return -1;
		if (getNumSamples() == 1)
			return 0;
		long avg = getAverage();
		double S2 = 0;
		for (Long sample : samples) {
			S2 += (sample - avg) * (sample - avg);
		}
		return (long) Math.sqrt(S2 / (getNumSamples() - 1));
	}

	public void addSample(long sample) {
		samples.add(sample);
	}

	public void addLost() {
		nlost++;
	}

	public String toString() {
		return this.ip + " -> Min: " + getMinimum() + "ms; Median: "
				+ getMedian() + "ms; Average: " + getAverage() + "ms; Max: "
				+ getMaximum() + "ms.";
	}

	public Object getCsvData() {
		return this.ip + ", " + this.getMinimum() + ", " + this.getMedian()
				+ ", " + this.getAverage() + ", " + this.getMaximum() + ", "
				+ this.getStdDev() + ", " + getNumSamples() + " "
				+ this.samples + "\n";
	}

	public int getIpVersion() {
		return ipVersion;
	}

	static public Class<?> getColumnClass(int columnIndex) {
		if (columnIndex == 0)
			return String.class;
		if (columnIndex == 1)
			return Long.class;
		if (columnIndex == 2)
			return Long.class;
		if (columnIndex == 3)
			return Long.class;
		if (columnIndex == 4)
			return Long.class;
		if (columnIndex == 5)
			return Integer.class;
		if (columnIndex == 6)
			return Integer.class;
		if (columnIndex == 7)
			return Double.class;
		return String.class;
	}

	public Object getColumn(int columnIndex) {
		/*
		 * Cambios aca IPvX
		 */
		if (columnIndex == 0)
			return this.countryCode + this.ip + " (" + this.testPointType + ")"
					+ " IPv" + String.valueOf(this.ipVersion);
		if (columnIndex == 1)
			return this.getMinimum();
		if (columnIndex == 2)
			return this.getMedian();
		if (columnIndex == 3)
			return this.getAverage();
		if (columnIndex == 4)
			return this.getMaximum();
		if (columnIndex == 5)
			return this.getNumSamples();
		if (columnIndex == 6)
			return this.getLost();
		if (columnIndex == 7)
			return this.getStdDev();
		return "?";
	}

	public boolean isOk() {
		if (testPointType == null)
			return false;
		if (getNumSamples() == 0)
			return false;
		if (getMinimum() < 0)
			return false;
		if (getMaximum() > 9999)
			return false;
		if (getStdDev() > 9999)
			return false;
		if (getAverage() < 5)
			return false; // proxy en el pc
		// Everything fine
		return true;
	}
}
