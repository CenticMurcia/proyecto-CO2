package gui;

import java.awt.EventQueue;

import javax.swing.JFrame;
import javax.swing.JButton;
import javax.swing.JLabel;
import java.awt.event.ActionListener;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.awt.event.ActionEvent;
import calidadAire.rest.App;
import java.awt.Color;
import java.awt.Font;

public class FeedBack {

	private JFrame frmHopurest;
	private JLabel lblEstado;
	private JLabel lblUltimoRegistro;
	private App appRestHopu;
	private ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);
	

	/**
	 * Launch the application.
	 */
	public static void main(String[] args) {
		EventQueue.invokeLater(new Runnable() {
			public void run() {
				try {
					FeedBack window = new FeedBack();
					window.frmHopurest.setVisible(true);
					
				} catch (Exception e) {
					e.printStackTrace();
				}
			}
		});
	}

	/**
	 * Create the application.
	 */
	public FeedBack() {
		initialize();
	}

	/**
	 * Initialize the contents of the frame.
	 */
	private void initialize() {
		// Inicio la app, prepara el runnable al que llama el Scheduler en los eventos de los botones
			appRestHopu = new App();
		
		frmHopurest = new JFrame();
		frmHopurest.setTitle("HopuRest");
		frmHopurest.setBounds(100, 100, 369, 259);
		frmHopurest.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		frmHopurest.getContentPane().setLayout(null);
		
		JButton btnIniciar = new JButton("Iniciar");
		btnIniciar.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				lblEstado.setText(appRestHopu.iniciarCaptacion());
			}
		});
		btnIniciar.setBounds(37, 29, 101, 37);
		frmHopurest.getContentPane().add(btnIniciar);
		
		lblEstado = new JLabel("Detenido");
		lblEstado.setBounds(66, 77, 63, 14);
		frmHopurest.getContentPane().add(lblEstado);
		
		JButton btnDetener = new JButton("Detener");
		btnDetener.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				lblEstado.setText(appRestHopu.detenerCaptacion());
			}
		});
		
		btnDetener.setBounds(162, 29, 101, 37);
		frmHopurest.getContentPane().add(btnDetener);
		
		JLabel lblTituloEstado = new JLabel("Estado:");
		lblTituloEstado.setBounds(20, 77, 46, 14);
		frmHopurest.getContentPane().add(lblTituloEstado);
		
		JLabel lblTituloUltimoReg = new JLabel("Último registro:");
		lblTituloUltimoReg.setBounds(20, 102, 87, 14);
		frmHopurest.getContentPane().add(lblTituloUltimoReg);
		
		lblUltimoRegistro = new JLabel(".");
		lblUltimoRegistro.setBounds(127, 102, 216, 14);
		frmHopurest.getContentPane().add(lblUltimoRegistro);
		
		JLabel lblTituloError = new JLabel("Error:");
		lblTituloError.setBounds(20, 195, 63, 14);
		frmHopurest.getContentPane().add(lblTituloError);
		
		JLabel lblErrorApp = new JLabel("NO");
		lblErrorApp.setFont(new Font("Tahoma", Font.BOLD, 11));
		lblErrorApp.setForeground(new Color(46, 139, 87));
		lblErrorApp.setBounds(83, 195, 46, 14);
		frmHopurest.getContentPane().add(lblErrorApp);
		
		JButton btnNewButton = new JButton("Limpiar y reiniciar");
		btnNewButton.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				appRestHopu.detenerCaptacion();
				appRestHopu = null;
				System.gc();
				appRestHopu = new App();
			}
		});
		btnNewButton.setBounds(185, 191, 158, 23);
		frmHopurest.getContentPane().add(btnNewButton);
		// Creo un hilo para observar el úlimo registro añadido de la App
		Runnable runnable = new Runnable() {
			@Override
			public void run() {
				lblUltimoRegistro.setText(appRestHopu.getFechaRegAnterior());
				if(appRestHopu.getError().equals("No")) {
					lblErrorApp.setForeground(new Color(46, 139, 87));
					lblErrorApp.setText(appRestHopu.getError());
				}else {
					lblErrorApp.setText(appRestHopu.getError());
					lblErrorApp.setForeground(Color.RED);					
				}
				
			}//END RUN
		};
		scheduler.scheduleAtFixedRate(runnable, 3, 25, TimeUnit.SECONDS);
		
	}
}
