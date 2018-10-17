package dfrapp;
	
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.List;
import java.util.function.Consumer;

import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.stage.Stage;
import javafx.scene.Parent;
import javafx.scene.Scene;

/**
 * Main class for the DFR GUI. Because the main application logic is written
 * in Python, the GUI has to rely on IPC to get data from the Python Process.
 * To do this, the DFR GUI uses TCP connections as a transfer protocol.
 * @author Miguel
 *
 */
public class Main extends Application
{
	private Process clientProcess;
	private Controller controller;
	
	public interface Action
	{
		public void action();
	}
	
	@Override
	public void start(Stage primaryStage)
	{
		try 
		{
			//GUI elements are contained in an FXML file to get separate
			//application logic from GUI elements.
			FXMLLoader loader = new FXMLLoader(getClass().getResource("DFRApp.fxml"));
	        Parent root = loader.load();
	        controller = loader.getController(); 
	        primaryStage.setTitle("Distributed Fractal Rendering");
	        primaryStage.setScene(new Scene(root));
	        
	    	
	    	//Close the sockets and the client process when the 
	        //GUI is closed
			primaryStage.setOnCloseRequest((e) ->
			{
				this.controller.getSocketListener().close();
				clientProcess.destroy();
				System.out.println("finalizing");
			});
			
			
			//Run the python code and attempt to connect to it
			//via a TCP socket
	    	runClient(controller);
	    	
	    	
	        primaryStage.show();
		}
		
		catch(Exception e)
		{
			e.printStackTrace();
		}
		

	}
	
	public static void main(String[] args)
	{
		launch(args);
	}
	
	private void runClient(Controller c) throws InterruptedException 
	{
		
		Parameters params = this.getParameters();
		List<String> args = params.getUnnamed();
		
		//These are the ports and address with which 
		//to establish the client connection
		String path = args.get(0);
		String address = args.get(1);
		int port = Integer.parseInt(args.get(2));
		
		
		//It is safer to surround the path with "" since the path may involve spaces
		String command = String.format("python -u \"%s\" %s %d", path, address, port);
		System.out.println(command);
		try 
		{
			//Run the python code to get the client up
			clientProcess = Runtime.getRuntime().exec(command);
			
			//Listen to the input streams of the process to know
			//what the client would be printing out to console
			StreamGobbler error = new StreamGobbler(clientProcess.getInputStream(), (s) -> this.controller.sendMessage(s));
			StreamGobbler input = new StreamGobbler(clientProcess.getErrorStream(), (s) -> System.err.println(s));
			error.start();
			input.start();
			
			//Destroy the client and the socket when the application shuts down
			//abruptly
			Runtime.getRuntime().addShutdownHook(new Thread(() -> 
			{
				this.controller.getSocketListener().close();
				clientProcess.destroy();
			}));
		} 
		
		catch (IOException e)
		{
			e.printStackTrace();
		};
		
		//Have the controller connect to the client process so that
		//it has the socket through which to send configurations
		//of a fractal. For now, the default is localhost
		String wrapperAddr = "127.0.0.1";
		int wrapperPort = 1000;
		this.controller.connectToClient(wrapperAddr, wrapperPort);
	}
	
	/**
	 * A class to redirect the output of another process into this process.
	 * This is needed to understand what the client, which is written in Python,
	 * is outputting to console.
	 * 
	 * Taken from https://stackoverflow.com/questions/1732455/redirect-process-output-to-stdout
	 * @author Miguel
	 *
	 */
	private class StreamGobbler extends Thread
	{
		private InputStream is;
		private Consumer<String> consumer;
		
		public StreamGobbler(InputStream is, Consumer<String> consumer)
		{
			this.is = is;
			this.consumer = consumer;
		}
		
		public void run() 
		{
			 try
			 {
		            InputStreamReader isr = new InputStreamReader(is);
		            BufferedReader br = new BufferedReader(isr);
		            String line = null;
		            
		            //Redirect output to the controller's messages box
		            while ( (line = br.readLine()) != null)
		            {
		            	consumer.accept(line);
		            }
			 } 
			 
			 catch (IOException ioe)
			 {
		            ioe.printStackTrace(); 
		     }	 
		}
	}
}
