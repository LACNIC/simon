package simon.client.latency;

public class Country {
	String countryCode;
	String countryName;
	
	public Country(String countryCode, String countryName) {
		this.countryCode = countryCode;
		this.countryName = countryName;
	}
	
	public String toString() {
		return this.countryName + "(" + this.countryCode + ")";
	}

	public String getCountryCode() {
		return countryCode;
	}

	public String getCountryName() {
		return countryName;
	}
}
