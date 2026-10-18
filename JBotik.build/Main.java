import javax.swing.*;
import javax.swing.border.*;
import javax.imageio.ImageIO;

import java.awt.event.*;
import java.util.*;
import java.io.*;
import java.awt.*;

public class Main extends JFrame {

	public static int WIDTH = 910, HEIGHT = 800;
	
	public static myPanel panel;
	public static String currentFilepath; // current filepath of the working file
	
	public enum day {
		MONDAY   ("Пн", "homework/monday.txt"), 
		TUESDAY  ("Вт", "homework/tuesday.txt"), 
		WEDNESDAY("Ср", "homework/wednesday.txt"), 
		THURSDAY ("Чт", "homework/thursday.txt"), 
		FRIDAY   ("Пт", "homework/friday.txt"), 
		SATURDAY ("Сб", "homework/saturday.txt");
		
		String name;
		String filepath;
		
		day(String name, String filepath) {
			this.name = name;
			this.filepath = filepath;
		}
		
	}

	public static String readFile(String filepath) {
		try (Scanner scanner = new Scanner(new File(filepath))) {
			String text = "";
			while (scanner.hasNextLine())
				text += scanner.nextLine() + "\n";
			return text.trim();
		} catch (Exception e) {
			System.out.println("Something went wrong while reading the file on the path: \"" + filepath + "\"\n" + e);
			return null;
		}
	}

	public static void saveToFile(String filepath) {
		try (FileWriter fileWriter = new FileWriter(filepath)) {
			fileWriter.write(Main.panel.textArea.getText());
		} catch (Exception e) {
			System.out.println("Something went wrong while writing to the file on the path: \"" + filepath + "\"\n" + e);
		}
	}
	
	public Main() {
		super("JBotik");
		setSize(WIDTH, HEIGHT);
		setResizable(false);
		setLocationRelativeTo(null);
		
		// Setting icons
		String[] iconsPaths = {"/icons/icon16.png", "/icons/icon32.png", "/icons/icon48.png", "/icons/icon64.png"};
		ArrayList<Image> icons = new ArrayList<>();
		for (String iconPath : iconsPaths) {
			try {
				icons.add(ImageIO.read(Main.class.getResource(iconPath)));
			} catch (Exception e) {
				System.out.println("Something went wrong while reading the icon on the path: \"" + iconPath + "\"\n" + e.getMessage());
			}
		}
		setIconImages(icons);

		// Getting the bounds without borders
		setVisible(true);
		WIDTH = getContentPane().getWidth();
		HEIGHT = getContentPane().getHeight();

		// Adding panel
		panel = new myPanel();
		add(panel);

		setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setVisible(true);
	}

    public static void main(String args[]) {
        System.out.println(">> JBotik <<");
        new Main();
    }

}

class myPanel extends JPanel {

	public TextArea textArea = new TextArea();

	public myPanel() {
		super();
		setFocusable(true);
		setLayout(null);
		
		// Buttons to view the homework for specific days
		for (int i = 0; i < 6; i++) 
			add(new DayButton(Main.day.values()[i], Main.WIDTH / 6 * i, 0));
		
		// Button to show the whole homework
		add(new FullButton());
		
		add(textArea);
	}
}

class DayButton extends JButton implements ActionListener, MouseListener {
	
	public Font font = new Font("Consolas", Font.PLAIN, 18);
	public String filepath;
	public int dayIndex = 0;
	
	public DayButton(Main.day day, int x, int y) {
		super();
		filepath = day.filepath;
		
		// Text
		setFont(font);
		setText(day.name);
		
		// Bounds and styling
		setBounds(x, y, Main.WIDTH/6, Main.HEIGHT/20);
		setBackground(Color.LIGHT_GRAY);
		setFocusPainted(false);
		setContentAreaFilled(false);
		setOpaque(true);
		setBorder(new CompoundBorder(new LineBorder(Color.BLACK), new EmptyBorder(0, 0, 0, 0)));
		
		// Listeners
		addActionListener(this);
		addMouseListener(this);
	}
	
	@Override
	public void actionPerformed(ActionEvent e) {
		Main.panel.textArea.setText(Main.readFile(filepath));
		Main.currentFilepath = filepath;
	}

	@Override
	public void mousePressed(MouseEvent e) {
		setBackground(Color.GRAY);
	}

	@Override
	public void mouseEntered(MouseEvent e) {}

	@Override
	public void mouseReleased(MouseEvent e) {
		setBackground(Color.LIGHT_GRAY);
	}

	@Override
	public void mouseExited(MouseEvent e) {}

	@Override
	public void mouseClicked(MouseEvent e) {}
	
}

class FullButton extends JButton implements ActionListener, MouseListener {

	public Font font = new Font("Consolas", Font.PLAIN, 18);
	
	public FullButton() {
		super();
		// Text
		setFont(font);
		setText("Всё");

		// Bounds and styling
		setBounds(0, Main.HEIGHT/20, Main.WIDTH, Main.HEIGHT/20);
		setBackground(Color.LIGHT_GRAY);
		setBorder(new CompoundBorder(new LineBorder(Color.BLACK), new EmptyBorder(0, 0, 0, 0)));
		setFocusPainted(false);
		setContentAreaFilled(false);
		setOpaque(true);

		// Listeners
		addActionListener(this);
		addMouseListener(this);
	}

	@Override
	public void actionPerformed(ActionEvent e) {
		String fullHomework = "";
		for (Main.day day : Main.day.values()) {
			fullHomework += Main.readFile(day.filepath) + "\n\n";
		}
		Main.panel.textArea.setText(fullHomework.trim());
		Main.currentFilepath = "";
	}

	@Override
	public void mousePressed(MouseEvent e) {
		setBackground(Color.GRAY);
	}

	@Override
	public void mouseEntered(MouseEvent e) {}

	@Override
	public void mouseReleased(MouseEvent e) {
		setBackground(Color.LIGHT_GRAY);
	}

	@Override
	public void mouseExited(MouseEvent e) {}

	@Override
	public void mouseClicked(MouseEvent e) {};

}

class TextArea extends JScrollPane {

	public Font font = new Font("Consolas", Font.PLAIN, 18);
	public static JTextPane textView = new JTextPane();
	
	public TextArea() {
		
		super(textView);
	
		int gap = 10;
		setBounds(gap, Main.HEIGHT/20*2 + gap, Main.WIDTH - 2 * gap, Main.HEIGHT/20*18 - 2 * gap);
		
		textView.setFont(font);
		
		textView.addKeyListener(new KeyListener() {
			@Override
			public void keyPressed(KeyEvent e) { }

			@Override
			public void keyReleased(KeyEvent e) {
				if (!Main.currentFilepath.isEmpty()) {
					Main.saveToFile(Main.currentFilepath);
				}
			}

			@Override
			public void keyTyped(KeyEvent e) { }
		});
		
	}

	public void setText(String s) { textView.setText(s); }
	public String getText() { return textView.getText(); }

}