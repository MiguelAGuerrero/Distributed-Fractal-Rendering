package dfrapp;

import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.embed.swing.SwingFXUtils;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.scene.canvas.Canvas;
import javafx.scene.control.Button;
import javafx.scene.control.ComboBox;
import javafx.scene.control.MenuItem;
import javafx.scene.control.TextArea;
import javafx.scene.control.TextField;
import javafx.scene.image.Image;
import javafx.scene.image.PixelWriter;
import javafx.scene.image.WritableImage;
import javafx.scene.paint.Color;
import javafx.stage.DirectoryChooser;
import javafx.stage.FileChooser;
import javafx.stage.FileChooser.ExtensionFilter;

import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;

import javax.imageio.ImageIO;

import javafx.application.Application;

/**
 * The Controller holds the GUI logic for when actions happen. It is also
 * responsible for initializing key GUI elements.
 * 
 * The dependencies of this class are injected via FXMLLoader when
 * the application is launched
 * @author Miguel
 *
 */
public class Controller
{
	private SocketListener listener; 

	public Controller() 
	{
		this.listener = null;
	}

	@FXML
	private Canvas canvas;

	@FXML
	private TextField imageWidth;

	@FXML
	private TextField yMin;

	@FXML
	private TextField yMax;

	@FXML
	private ComboBox<String> fractal;

	@FXML
	private TextArea messages;

	@FXML
	private Button ender;

	@FXML
	private TextField xMax;

	@FXML
	private TextField xMin;

	@FXML
	private TextArea workers;

	@FXML
	private TextField imageHeight;

	@FXML
	private TextField iterations;

	@FXML
	private TextField red;

	@FXML
	private TextField blue;

	@FXML
	private TextField green;

	@FXML
	private MenuItem menuClose;

	@FXML
	private MenuItem menuSave;

	@FXML
	private MenuItem clear;
	
	private final int DEFAULT_MOD = 100;

	//Modulos to alter boundary color of Mandelbrot
	private int RMod = DEFAULT_MOD;
	private int GMod = DEFAULT_MOD;
	private int BMod = DEFAULT_MOD;

	private BufferedImage bImage;

	@FXML
	void render(ActionEvent event)
	{
		try
		{
			int imageWidth = Integer.parseInt(this.imageWidth.getText());
			int imageHeight = Integer.parseInt(this.imageHeight.getText());

			float xMin = Float.valueOf(this.xMin.getText());
			float xMax = Float.valueOf(this.xMax.getText());
			float yMin = Float.valueOf(this.yMin.getText());
			float yMax = Float.valueOf(this.yMax.getText());

			int iterations = Integer.parseInt(this.iterations.getText());
			String fractal = this.fractal.getValue();

			this.listener.sendConfigurations(imageWidth, imageHeight, xMin, xMax, yMin, yMax, iterations, fractal);
			this.ender.setDisable(true);

			//Clamp values between 1-255
			this.RMod = clampRGB(Integer.parseInt(this.red.getText()));
			this.GMod = clampRGB(Integer.parseInt(this.green.getText()));
			this.BMod = clampRGB(Integer.parseInt(this.blue.getText()));

			//Force clamp text field values
			this.red.setText(String.valueOf(RMod));
			this.green.setText(String.valueOf(GMod));
			this.blue.setText(String.valueOf(BMod));

		}

		catch(Exception e)
		{
			System.err.println(e.getMessage());
			this.ender.setDisable(false);
		}    	
	}	

	private int clampRGB(int val) 
	{
		if(val > 255)
			return 255;
		if(val < 1)
			return 1;
		return val;
	}

	@FXML
	private void initialize() 
	{
		this.fractal.getItems().addAll("MANDELBROT");

		int defaultWidth = 500;
		int defaultHeight = 3 * defaultWidth / 4;
		int defaultXmin = -1;
		int defaultXmax = 1;
		int defaultYmin = -1;
		int defaultYmax = 1;
		int defaultItrs = 256;

		this.imageWidth.setText(String.valueOf(defaultWidth));
		this.imageHeight.setText(String.valueOf(defaultHeight));
		this.xMin.setText(String.valueOf(defaultXmin));
		this.xMax.setText(String.valueOf(defaultXmax));
		this.yMin.setText(String.valueOf(defaultYmin));
		this.yMax.setText(String.valueOf(defaultYmax));
		this.iterations.setText(String.valueOf(defaultItrs));
		this.fractal.getSelectionModel().selectFirst();
	}

	public void connectToClient(String address, int port) 
	{
		this.listener = new SocketListener(this, address, port);
		Thread listenerThread = new Thread(this.listener);
		listenerThread.start();
	}

	@FXML
	public void close() 
	{
		javafx.application.Platform.exit();
	}
	
	@FXML
	public void clear() 
	{
		this.bImage = null;
		this.canvas.getGraphicsContext2D().clearRect(0, 0, this.canvas.getWidth(), this.canvas.getHeight());
	}
	
	@FXML
	public void save() 
	{
		if(this.bImage == null) 
		{
			this.sendMessage("Cannot save: no image has been rendered");
			return;
		}
		
		FileChooser fileChooser = new FileChooser();
		fileChooser.getExtensionFilters().add(new ExtensionFilter("Images", "*.png", "*.jpg", "*.bmp", "*.gif"));
		File destination = fileChooser.showSaveDialog(null);

		if(destination == null)
		{
			System.out.println("Canceled save");
		}
		else
		{
			try
			{
				System.out.println(destination.getAbsolutePath());
				ImageIO.write(bImage, "png", destination);
			}
			catch (IOException e)
			{
				e.printStackTrace();
			}
		}
	}

	public void sendMessage(String s) 
	{
		//So, for whatever reason, trying to append text to a TextArea outside
		//the FXThread causes exceptions. Run this task later on the thread.
		javafx.application.Platform.runLater(() -> this.messages.appendText(s+"\n"));
	}

	public void sendWorkers(String[] workers) 
	{
		javafx.application.Platform.runLater(() ->
		{
			this.workers.setText("");
			if(workers != null)
			{
				for(String w: workers) 
				{
					this.workers.appendText("Worker (" + w + ")\n");
				}
			}
		});
	}

	public void sendCanvasData(int[][] data) 
	{
		//Clear the canvas
		this.canvas.getGraphicsContext2D().clearRect(0, 0, this.canvas.getWidth(), this.canvas.getHeight());
		WritableImage img = new WritableImage(data.length, data[0].length);
		for(int i = 0; i < data.length; i++)
			for(int j = 0; j < data[0].length; j++)
			{
				int pixel = data[i][j];
				img.getPixelWriter().setColor(i, j, Color.rgb(
						(int)(pixel % this.RMod),
						(int)(pixel % this.GMod), 
						(int)(pixel % this.BMod)));
			}

		//Draw to an image so that it can scale with the canvas
		this.canvas.getGraphicsContext2D().drawImage(img, 0, 0);


		this.bImage = SwingFXUtils.fromFXImage(img, null);

		this.ender.setDisable(false);

	}

	public SocketListener getSocketListener()
	{
		return this.listener;
	}
}
