package simon.client.latency;

import java.util.ArrayList;
import java.util.Collections;

public class LatencyLocation {
	String destination;
	ArrayList<Long> samples = new ArrayList<Long> ();
	int nlost = 0;
	//long devLatency;
	//long avgLatency;
	
	static String [] columnNames = { "Destination", "min", "median", "avg", "max", "samples", "losts", "stddev"};
	
	public int getNumSamples() {
		return this.samples.size();
	}
	
	public int getLost() {
		return nlost;
	}
	
	public long getAverage() {
		if (getNumSamples()==0) return -1;	
		long accum = 0;
		for(Long sample:samples) {
			accum+= (long)sample;
		}
		return (accum/getNumSamples());
	}
	
	public long getMin() {
		if (getNumSamples()==0) return -1;	
		ArrayList<Long> myArray = samples;
        Collections.sort(myArray);
		return (myArray.get(0));
	}

	public long getMax() {
		if (getNumSamples()==0) return -1;	
		ArrayList<Long> myArray = samples;
        Collections.sort(myArray);
        Collections.reverse(myArray);
		return (myArray.get(0));
	}

	public long getMedian() {
		if (getNumSamples()==0) return -1;	
		ArrayList<Long> myArray = samples;
        Collections.sort(myArray);
        int arrayLength = 0;
        long arrayMedian = 0;
        int currentIndex = 0;
        arrayLength = myArray.size();
        if(arrayLength % 2 != 0) {    
        	currentIndex = ((arrayLength / 2) + 1);
            arrayMedian = myArray.get(currentIndex - 1);
        }
        else {    
        	int indexOne = (arrayLength / 2);
            int indexTwo = arrayLength / 2 + 1;
            long arraysSum = myArray.get(indexOne - 1) + myArray.get(indexTwo - 1);
            arrayMedian = arraysSum / 2;
        }
        return arrayMedian;
    }
	
	public double getStdDev() {
		if (getNumSamples()==0) return -1;
		if (getNumSamples()==1) return 0;
		long avg = getAverage();
		double S2 = 0;
		for(Long sample:samples) {
			S2 += (sample-avg)*(sample-avg);
		}
		// as we have a statistical distribution
		// the correct is (S2/(numsamples -1))
		// (S2/numsaples) would be correct for a population
		// ** PLESE VERIFY THAT ** I am not very good with statistics
		return  Math.sqrt(S2/(getNumSamples()-1));
	}
	
	void addSample(long sample) {
		samples.add(sample);
	}
	
	void addLost() {
		nlost ++;
	}
	
	public LatencyLocation(String site) {
		this.destination = site;
	}

	public String toString() {
		return destination + " -> Min: " + getMin() + "ms; Median: "+ getMedian() + "ms; Average: " + getAverage() + "ms; Max: " + getMax() + "ms.";
	}

	public Object getData() {
		return this.destination +  ", " + this.getMin()  + ", " + this.getMedian()  + ", " + this.getAverage()+ ", " + this.getMax()  + ", " + this.getStdDev() + ", " + getNumSamples() + " " + this.samples + "\n";
	}

	static public Class<?> getColumnClass(int columnIndex) {
		if (columnIndex==0) return String.class;
		if (columnIndex==1) return Long.class;
		if (columnIndex==2) return Long.class;
		if (columnIndex==3) return Long.class;
		if (columnIndex==4) return Long.class;
		if (columnIndex==5) return Integer.class;
		if (columnIndex==6) return Integer.class;
		if (columnIndex==7) return Double.class;
		return String.class;
	}
	
	public Object getColumn(int columnIndex) {
		if (columnIndex==0) return this.destination;
		if (columnIndex==1) return this.getMin();
		if (columnIndex==2) return this.getMedian();
		if (columnIndex==3) return this.getAverage();
		if (columnIndex==4) return this.getMax();
		if (columnIndex==5) return this.getNumSamples();
		if (columnIndex==6) return this.getLost();
		if (columnIndex==7) return this.getStdDev();
		return "?";
	}
}


