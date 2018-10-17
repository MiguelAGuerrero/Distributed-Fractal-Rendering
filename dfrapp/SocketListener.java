package dfrapp;

import java.io.IOException;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.net.SocketException;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.Arrays;
import java.util.Date;

/**
 * SocketListener is thread code that listens for the results from
 * the wrapped GUI client. 
 * 
 * It may also be used to send configurations to wrapped GUI client, but
 * this method is not invoked in the thread code and should be evoked
 * in an another thread.
 * 
 * @author Miguel
 *
 */
public class SocketListener implements Runnable
{
	/**
	 * The GUI client's port
	 */
	private int serverPort;
	
	/**
	 * The GUI client's socket address
	 */
	private InetSocketAddress endpoint; 
	
	/**
	 * The GUI clients wireless address
	 */
	private InetAddress serverAddress;
	
	/**
	 * Socket that represents the TCP connection from
	 * this GUI to the GUI Wrapped Client
	 */
	private Socket socket;
	
	/**
	 * The Controller class of the DFR as a JavaFX application
	 */
	private Controller controller;
	
	/**
	 * Timestamp used to keep track of how long it takes to complete
	 * the rendering process from time work is submitted and the time
	 * the image is displayed
	 */
	private long timestamp;
	
	public SocketListener(Controller controller, String serverAddress, int serverPort) 
	{
		this.serverPort = serverPort;
		this.controller = controller;
		
		boolean connected = false;
		
		System.out.println("Establishing client...");
		
		//timeout count for how long to establish client
		int timeoutCount = 5;
		
		while(!connected)
		{
			// Setup the server side connection data
			try 
			{
				this.serverPort = serverPort;
				this.serverAddress = InetAddress.getByName(serverAddress);
				this.endpoint = new InetSocketAddress(this.serverAddress, this.serverPort);
				socket = new Socket();
				socket.setReuseAddress(true);
				socket.connect(endpoint);
				System.out.println("Client established. Running DFR GUI Application...");
				connected = true;
				
			} 

			catch(Exception e)
			{
				timeoutCount--;
				if(timeoutCount == 0)
				{
					System.err.println("Client cannot be established locally. Exiting...");
					this.controller.close();
					return;
				}
			}
		}
	}
	
	public void close() 
	{
		try
		{
			this.socket.close();
		} 
		
		catch (IOException e)
		{
			e.printStackTrace();
		}
	}
	
	public void sendConfigurations(int imageWidth, int imageHeight, float xMin, float xMax, float yMin, float yMax, int iterations, String fractal) 
	{
		try
		{
			byte[] typeBytes = "CNFG".getBytes();
			int bytesFromInts = 28;
			int headerBytes = 8;
			int dataLength = bytesFromInts + fractal.getBytes().length;
			ByteBuffer buf = ByteBuffer.allocate(headerBytes + dataLength);
			buf.order(ByteOrder.nativeOrder());
			buf.put(typeBytes);
			buf.putInt(dataLength);
			buf.putInt(imageWidth);
			buf.putInt(imageHeight);
			buf.putFloat(xMin);
			buf.putFloat(xMax);

			buf.putFloat(yMin);
			buf.putFloat(yMax);
			buf.putInt(iterations);
			buf.put(fractal.getBytes());

			System.out.println("Sending configurations");
			this.socket.getOutputStream().write(buf.array());
			this.timestamp = new Date().getTime();
		} 
		
		catch (IOException e)
		{
			e.printStackTrace();
		}
	}
	
	private int consumeDataLength() throws IOException 
	{
		int sizeOfInt = 4;
		ByteBuffer buf = ByteBuffer.allocate(sizeOfInt);
		buf.order(ByteOrder.nativeOrder());
		this.socket.getInputStream().readNBytes(buf.array(), 0, sizeOfInt);
		
		return buf.getInt();
	}
	
	private int[][] consumePixelData(int dataLength) throws IOException 
	{
		
		int metaByteLen = 8;
		byte[] pixelData = new byte[dataLength - metaByteLen];
		this.socket.getInputStream().readNBytes(pixelData, 0, pixelData.length);
		
		ByteBuffer pixelBuf = ByteBuffer.wrap(pixelData);
		pixelBuf.order(ByteOrder.nativeOrder());
				
		byte[] meta = new byte[metaByteLen];
		this.socket.getInputStream().readNBytes(meta, 0, metaByteLen);
		ByteBuffer metaBuf = ByteBuffer.wrap(meta);
		metaBuf.order(ByteOrder.nativeOrder());
		int rows = metaBuf.getInt();
		int columns = metaBuf.getInt();
		
		int[][] pixels = new int[rows][columns];
		
		for(int i = 0; i < rows; i++)
			for(int j = 0; j < columns; j++)
			{
				pixels[i][j] = pixelBuf.getInt();
			}
		
		return pixels;
	}
	
	private void handleRSLT() throws IOException 
	{

		int dataLength = consumeDataLength();
		int[][] pixels = consumePixelData(dataLength);
		
		this.controller.sendCanvasData(pixels);
		
		auditTimeElapsed();
	}
	
	private void handleNONE() throws IOException 
	{	
		this.controller.sendWorkers(null);
		
	}
	
	private void handleUPDT() throws IOException 
	{

		int dataLength = consumeDataLength();
		System.out.println(dataLength);
		ByteBuffer buf = ByteBuffer.allocate(dataLength);
		this.socket.getInputStream().readNBytes(buf.array(), 0, dataLength);
		String ips = new String(buf.array());
		System.out.println(ips);
		String[] split = ips.split(" ");
		this.controller.sendWorkers(split);
	}
	
	private void auditTimeElapsed() 
	{
		double elapsed = new Date().getTime() - this.timestamp;
		this.controller.sendMessage("Total time: " + String.valueOf(elapsed / 1000) + "s");

	}
	public void run() 
	{
		boolean done = false;
		while(!done) 
		{
			//Expects a results message for now
			try
			{
				byte[] typeBuf = new byte[4];
				this.socket.getInputStream().readNBytes(typeBuf, 0, 4);
				String type = new String(typeBuf);
				if(type.equals("RSLT")) 
					handleRSLT();
				else if(type.equals("UPDT")) 
					handleUPDT();
				else if(type.equals("NONE")) 
					handleNONE();
			}
			
			catch(SocketException se) 
			{
				System.out.println(se.getMessage());
				done = true;
			}
			
			catch(Exception e) 
			{
				e.printStackTrace();
				done = true;
			}
		}
	}
}
