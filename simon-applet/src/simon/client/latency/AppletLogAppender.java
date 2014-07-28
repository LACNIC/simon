package simon.client.latency;

import javax.swing.JTextArea;

import org.apache.log4j.Appender;
import org.apache.log4j.WriterAppender;
import org.apache.log4j.spi.LoggingEvent;

public class AppletLogAppender extends WriterAppender implements Appender {

	JTextArea jtext;
	AppletLogAppender(JTextArea jtext) {
		this.jtext = jtext;
	}
	
	public void append(LoggingEvent event) {
		String text = this.jtext.getText();
		text+= event.getMessage()+"\n";
		this.jtext.setText(text);
		this.jtext.repaint();
	}
}
