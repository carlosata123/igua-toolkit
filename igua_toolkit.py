#!/usr/bin/python3 import os

# sleep(15)

# how to set to autostart:
# lo mismo pero adaptado a raspi: https://www.raspberrypi-spy.co.uk/2014/05/how-to-autostart-apps-in-rasbian-lxde-desktop/
# lo que funcó para hacer autostart: editamos este file: 
# sudo nano ~/.config/lxsession/LXDE-pi/autostart
# y alli adentro ponemos lo sgte: 
# @sudo /home/pi/Desktop/igua-toolkit/run.sh
# notar que debes escribilo antes de la linea que dice "screensaver"
# luego conviene crear un bookmark en el filemanager (pcmanfm) a la carpeta .config/lxsession/LXDE-pi/

# para configurar qué redes queremos aprender u olvidar: 
# sudo nano /etc/wpa_supplicant/wpa_supplicant.conf

# para clonar la carpeta de github a local:
# git clone http://github.com/kikomayorga/igua_toolkit/


#importando modulos genericos
from time import sleep
from time import strftime 
import time
import serial
import re
import socket
REMOTE_SERVER = "www.google.com"

# configuaracion de entradas/saldas del RPI
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

button = 4				# GPIO04, pin nro 07 
valve_relay = 17		# GPIO17, pin nro 11   
button2 = 27			# GPIO27, pin nro 13
spritz_relay = 22		# GPIO22, pin nro 15
coinhibitor_relay = 23	# GPIO23, pin nro 16
UV_relay = 18			# GPIO18, pin nro 12

GPIO.setup(button, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(button2, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(valve_relay, GPIO.OUT)
GPIO.setup(spritz_relay, GPIO.OUT)
GPIO.setup(coinhibitor_relay, GPIO.OUT)
GPIO.setup(UV_relay, GPIO.OUT)

#para carriots
from urllib.request import urlopen, Request
from time import mktime, sleep
from datetime import datetime
from json import dumps

class Client (object):
    api_url = "http://api.carriots.com/streams"
    api_read_url = "http://api.carriots.com/streams/IGUA01@kikomayorga.kikomayorga/"

    def __init__(self, api_key=None, client_type='json'):
        self.client_type = client_type
        self.api_key = api_key
        self.content_type = "application/vnd.carriots.api.v2+%s" % self.client_type
        self.headers = {'User-Agent': 'Raspberry-Carriots',
                        'Content-Type': self.content_type,
                        'Accept': self.content_type,
                        'Carriots.apikey': self.api_key}
        self.data = None
        self.response = None

    def send(self, data):
        self.data = dumps(data).encode('utf8')
        request = Request(Client.api_url, self.data, self.headers)     
        self.response = urlopen(request)
        return self.response
        
def rc_time(pipin):
    measurement = 0
    GPIO.setup(pipin, GPIO.OUT)
    GPIO.output(pipin, GPIO.LOW)
    sleep(0.1)

    GPIO.setup(pipin, GPIO.IN)

    while GPIO.input(pipin) == GPIO.LOW:
        measurement += 1

    return measurement
    
    
#fin para carriots

# declaramos una función que la usaremos mas adelante para 
# validar conexion disponible

def is_connected():
    try:
        host = socket.gethostbyname(REMOTE_SERVER)
        s = socket.create_connection((host, 80), 2)
        return True
    except:
        pass
    return False

ser = serial.Serial('/dev/ttyACM0',9600,timeout = 0)
ser2 =  serial.Serial('/dev/ttyACM2',9600,timeout = None)
ser3 =  serial.Serial('/dev/ttyACM1',9600,timeout = None, parity = serial.PARITY_NONE, xonxoff = False, rtscts = False, stopbits = serial.STOPBITS_ONE, bytesize = serial.EIGHTBITS)

#modulos custom
from igua_display import startdisplay, refreshdisplay 
from igua_display import display_bienvenida_linear, display_bienvenida_pwyw
from igua_display import display_acumula_pwyw, display_acumula_linear
from igua_display import display_servidos_lt, display_agradece 

# import flowmeter
# import valve

#from display + coinacceptor

last = 0.0
running = 1


solesacumulados = 0   			#transaction-wise accumulator
ferrosacumulados = 0  			#transaction-wise accumulator
cuenta_de_ciclos = 0				#transactions counter on eeprom	

process_id = 0                  #
modo_maquina = 0  # 1: pay what you want , 0: linear mode
button_state = 0
now = 0
now_1 = 0

#setup
startdisplay()
		
#main loop

#para carriots
device = "IGUA01@kikomayorga.kikomayorga"  # Replace with the id_developer of your device
# device = "IGUA_FEST_1@kikomayorga.kikomayorga"
# device = "IGUA_FEST_1@kikomayorga.kikomayorga"
# device = "IGUA_FEST_1@kikomayorga.kikomayorga"
# device = "IGUA_FEST_1@kikomayorga.kikomayorga"
# device = "IGUA_FEST_CHANCHA@kikomayorga.kikomayorga"
# device = "IGUA_FEST_DMD@kikomayorga.kikomayorga"  
apikey = "13f622d642b12cc336fa6bfde36e1561c6ac7eea19bd88d7c32246d0fca45691"  # Replace with your Carriots apikey
client_carriots = Client(apikey)

# ejemplo de curl "para traer todos los ulktimos streams"
# curl --header carriots.apikey:13f622d642b12cc336fa6bfde36e1561c6ac7eea19bd88d7c32246d0fca45691 http://api.carriots.com/streams/?device=IGUA01@kikomayorga.kikomayorga

#para carriots




#para lcd
def lcd_bienvenida_linear(now):
	if  now == 0:
		ser3.write('mAs agua pura...   para Todos!!!'.encode())
	elif now == 1:
		ser3.write('cuida tu salud..y la del planeta'.encode())
	elif now == 2:
		ser3.write('mejor agua y... menos plAstico!!'.encode())
	elif now == 3:
		ser3.write('f/aguaigua      http://igua.pe  '.encode())
	elif now == 4:
		ser3.write('hola mundo!!!   hola igua!!!    '.encode())
	elif now == 5:
		ser3.write('agua igua,      salud!          '.encode())
	
	return 1

def lcd_bienvenida_pwyw(now):
	if  now == 0:
		ser3.write('mAs agua pura...   para Todos!!!'.encode())
	elif now == 1:
		ser3.write('cuida tu salud..y la del planeta'.encode())
	elif now == 2:
		ser3.write('mejor agua y... menos plAstico!!'.encode())
	elif now == 3:
		ser3.write('f/aguaigua      http://igua.pe  '.encode())
	elif now == 4:
		ser3.write('hola mundo!!!   hola igua!!!    '.encode())
	elif now == 5:
		ser3.write('agua igua,      salud!          '.encode())
	
	return 1

def lcd_acumula_linear(solesacumulados):
	ser3.write(('tu saldo: S/. ' + str(format(solesacumulados, '.2f'))).encode())
	return 1
	
def lcd_acumula_pwyw(solesacumulados):
	ser3.write(('tu aporte: S/. ' + str(format(solesacumulados, '.2f'))).encode())	
		
def lcd_servidos_lt(servidos_lt,diff):
	global button
	button_state = GPIO.input(button)
	if button_state == GPIO.LOW:
		ser3.write(('tienes: ' + str(format(servidos_lt/1000, '.3f')) + ' l  ' + '                ' ).encode())	
	if button_state == GPIO.HIGH:
		ser3.write(('tienes: ' + str(format(servidos_lt/1000, '.3f')) + ' l  ' + '          ... ' + str(format(diff, '.0f')) + 's').encode())	
	
	
def lcd_agradece():
	ser3.write('gracias!!!! igua ague pe ! '.encode())	

def inicializaGPIO():
	set_valve(0)
	set_UV(1)	
	
def set_valve(valor):
	if valor == 0:
		GPIO.output(valve_relay, 1)
		GPIO.output(spritz_relay, 0)
	if valor == 1:
		GPIO.output(valve_relay, 0)
		GPIO.output(spritz_relay, 1)
		
def set_UV(valor):
	if valor == 0:
		GPIO.output(UV_relay, 0)
	if valor == 1:
		GPIO.output(UV_relay, 1)
		
def set_accepting(valor):
	if valor == 0:
		GPIO.output(coinhibitor_relay, 1)
	if valor == 1:
		GPIO.output(coinhibitor_relay, 0)
	
		
def send_to_carriots():  #send collected data to carriots
	global device
	global servidolitros
	global solesacumulados
	timestamp = int(mktime(datetime.utcnow().timetuple()))
	timestamp = int(mktime(datetime.utcnow().timetuple()))
	solesstring = str(solesacumulados)
	data = {"protocol": "v2", "device": device, "at": timestamp, "data": {"colectado soles": solesacumulados, "servido litros": format(servidos_lt/1000, '.3f')}}
	print(data)
	if is_connected() == True:
		carriots_response = client_carriots.send(data)
		print('conexion ok!')
		print(carriots_response.read())
	else:
		print('no connectivity available')
		
		
inicializaGPIO()

#MAIN LOOP	
while 1 == 1:
	
	if process_id == 0:  #espera monedas
		set_accepting(0)
		ferrosacumulados = 0
		now_1 = now
		now = time.time()
		now = int((now/2)%6)
		if now != now_1:
			if modo_maquina == 0:
				display_bienvenida_linear(now)
				lcd_bienvenida_linear(now)
			if modo_maquina == 1:
				display_bienvenida_pwyw(now)
				lcd_bienvenida_pwyw(now)  # cuidado CUIDADO!!!!
	
    #leer aceptador de monedas
		before = int(time.time())
		
		bytesToRead = ser.inWaiting()
		if bytesToRead > 0:
			now = int(time.time())
			process_id = 1
			
	#acepta monedas
	elif process_id == 1:
		set_UV(0)
		set_accepting(0)
		secondcycle = 0   #variable que inicializa el pid2
		bytesToRead = ser.inWaiting()
		if bytesToRead > 0:
			sleep(0.5)
			bytesToRead = ser.inWaiting()
			# print("bytes to read: ", bytesToRead)
			# string_igua = str(ser.readline(),'utf-8')
			string_igua = ser.read(2)		
			ferros = int(string_igua)
			ferrosacumulados = ferrosacumulados + ferros
			solesacumulados = ferrosacumulados / 10.0
			if modo_maquina == 0:
				display_acumula_linear(solesacumulados)
				lcd_acumula_linear(solesacumulados)
			if modo_maquina == 1:
				display_acumula_pwyw(solesacumulados)
				lcd_acumula_pwyw(solesacumulados)
			before = int(time.time()) 
		
		#TIMEOUT 
		now = int(time.time())
		diff = now - before

		if diff > 10:
			process_id = 2
			cuenta_de_ciclos = cuenta_de_ciclos + 1
			# print("van n monedas:", cuenta_de_ciclos)
			# print("pasaremos al prcid 2")
			diff = 0
			before = int(time.time()) 
				
		
		#tap_button pressed
		button_state = GPIO.input(button)
		if button_state == GPIO.LOW:
			diff = 0
			print ("switching to PID2")
			time.sleep(0.5)	
			latch = 1
			servidos_lt = 0
			precio = 0.5
			servidos_total = 0
			counter_al_inicio = 0		           
			secondcycle = 0
			set_valve(1) #habilitar valvula
			process_id = 2
		else:
			process_id = 1
			# print ("button is NOT PRESSED")	
		
	
	# habilitada vavula y muestra litros
	elif process_id == 2:
		set_accepting(1)
		print("estoy en el PID2")
		ser2.flushInput()
		sleep(0.1)
		hora_actual = int(time.time())
		hora_de_re_inicio_servida = hora_actual
		ser2.flushInput()
						
		if modo_maquina == 0:
			litros_servir = 1000 * (solesacumulados / precio) 
		if modo_maquina == 1:
			litros_servir = 1000
		
		while process_id == 2:

			#verifica timeout
			hora_actual = int(time.time())
			tiempo_desde_inicio_servida = hora_actual - hora_de_re_inicio_servida
			
			bytesToRead = ser2.inWaiting()
			
			if bytesToRead > 4:  #cada vez que recibe la cuenta desde arduino-flujometro
				ser2.flushInput()
				print('(hemos quemado bytes retrasantes) ')
				
			if bytesToRead > 0:  #cada vez que recibe la cuenta desde arduino-flujometro
				sleep(0.1)     #esperamos a que llegue todo el mensaje 
				print("ahora voy a leer e imprimir lo que recibo.... ")
				try:
					string_igua = str(ser2.readline(),'utf-8')
				except ValueError:
					print('utf error')
				string_igua = str(string_igua).lstrip('r')
				string_igua = str(string_igua).strip('\n\r')
				string_igua = str(string_igua).strip('\r\n')
				print('entonces el valor sería: ')
				print(string_igua)
				
				if secondcycle == 0:
						try:
							counter_al_inicio = int(string_igua)
						except ValueError:
							print('value error')
							
				secondcycle = 1  #flag que indica que ya se corrio una vuelta de inicializon			
				try:
					servidos_total = int(string_igua)
				except ValueError:
					print('string error')
			
			if secondcycle == 1:     #a partir de la segunda corrida, muestro la cuenta regresiva
				servidos_lt = 0.9 * ((servidos_total - counter_al_inicio) * 2640)/2000
				display_servidos_lt((litros_servir - servidos_lt),10 - tiempo_desde_inicio_servida)
				lcd_servidos_lt((litros_servir - servidos_lt),10 - tiempo_desde_inicio_servida)
				# print("mande el comando al display")
				
			# el boton resetea el tiempo maximo y enciende la válvula
			button_state = GPIO.input(button)
			if button_state == GPIO.LOW: 
				hora_de_re_inicio_servida = int(time.time())
				# print ("button is LOW - OR PRESSED")
				# time.sleep(0.05)
				set_valve(1)
				
			# el boton libre cierra la valvula
			if button_state == GPIO.HIGH:
				set_valve(0)
				# print('se solto boton')

			if (servidos_lt - litros_servir) > 0:  # si se pasa del limite a servir
				print ("se pasó del volumen a servir")
				set_valve(0)
				send_to_carriots()
				process_id = 3
					
			if tiempo_desde_inicio_servida > 10:     #si se demora mucho en re-servir		
				print ("se acabó el tiempo_desde_inicio_de_servida")
				set_valve(0)   #cerrando la valvula
				send_to_carriots()
				process_id = 3
				
					

	# deshabilita vavula y agradece
	elif process_id == 3:
		#ser2.write(0)  # deshabilitar valvula
		sleep(0.5)
		display_agradece()
		lcd_agradece()
		before = int(time.time()) 
		# print("before: ", before)
		while process_id==3:
			now = int(time.time())
			# print("now: ", now)	
			diff = now - before
			# print("diff: ", diff)
			if diff > 3:
				set_UV(1)
				process_id = 0
	
	


# todo: rfid
	
