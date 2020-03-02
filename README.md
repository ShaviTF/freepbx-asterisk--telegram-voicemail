# Descripción

Este trabajo está basado en el trabajo realizado por sHaggYcaT (https://github.com/sHaggYcaT/telegram_freepbx_bot) y utiliza parte de su código (concretamente el módulo de bot), pero se ha diseñado un nuevo cliente y una nueva manera de integrarlo de forma que no se sacrifique la funcionalidad del envío de correo electrónico nativa de Asterisk.
Este documento está enfocado a la instalación y utilización del sistema con FreePBX, pero es fácilmente portable a otras distribuciones basadas en Asterisk.

# Preparación

Partimos de la base que ya se posee una distribución de FreePBX instalada y que ya tienes creado el bot de telegram y tienes el correspondiente token y el ID del grupo correspondiente. Si no tienes esa parte y no sabes como hacerlo, te dejo un enlace de un tutorial donde se explica.

https://plexadictos.wordpress.com/2018/03/15/crear-un-bot-y-un-grupo-en-telegram-para-obtener-el-token-y-el-group-id/


- Comprobamos la version o versiones de Python que tienes instaladas (no solo la que está activa)

	  ls -ls /usr/bin/python*
   
	(salida en mi caso:)
	0 lrwxrwxrwx. 1 root root     7 ene 12 23:30 /usr/bin/python -> python2
	0 lrwxrwxrwx. 1 root root     9 ene 12 23:30 /usr/bin/python2 -> python2.7
	8 -rwxr-xr-x. 1 root root  7216 jun 20  2019 /usr/bin/python2.7
	12 -rwxr-xr-x. 2 root root 11376 dic  5  2018 /usr/bin/python3.6
	12 -rwxr-xr-x. 2 root root 11376 dic  5  2018 /usr/bin/python3.6m

	(en mi caso tengo instalada la versión de python 2.7 que me viene con la distro de FreePBX la versión 3.6 que instalé yo manualmente)
	
	Si no tienes instalado Python, lo instalamos:
	
	  yum update
	  yum install python36
	
	* Aunque los scripts están preconfigurados para funcionar con la versión 3.6 de Python, debería funcionar igual con otras versiones, pero habrá que modificar algunos archivos como se detallará mas adelante
 
- Comprobamos si tenemos instalado pip para la versión de Python que vayamos a emplear

	por ejemplo en mi caso voy a usar python 3.6 pero la versión activa de sistema es la 2.7, por lo que ejecuto:
  
	  python3.6 -m pip -V
  
	(salida:) pip 9.0.1 from /usr/lib/python3.6/site-packages (python 3.6)
	
	si no tengo pip instalado, lo instalamos:
	
	  yum update
	  yum install python36-pip
	
- Comprobamos si tenemos instalado virtualenv
	
	  virtualenv --version
	
	(salida:) virtualenv 20.0.4 from /usr/lib/python2.7/site-packages/virtualenv/__init__.pyc
	
	* En este caso da igual sobre que versión de python esté instalada porque a la hora de crear el entorno virtual, podemos especificar que versión de Python queremos utilizar.
	
	si no está instalado, lo instalamos
	
	  pip install virtualenv
	
- Creamos una carpeta para la aplicación, en mi caso /opt/telegram-voicemail

	* se puede usar la ruta que se desee, pero si se pone una ruta diferente a la del ejemplo, habrá que modificarla en los scripts como se detallará mas adelante.
	
- Copiamos la carpeta scripts y el archivo freepbxbot.ini en la carpeta creada

# Instalación del servicio de publicación "freepbxtgbot"

- Creamos el entorno virtual. En este caso especificaremos el comando -p para indicar que versión queremos emplear de python, si solo tenemos una no hará falta ponerlo

	dentro de la carpeta /opt/telegram-voicemail, ejecutamos:

	  virtualenv -p /usr/bin/python3.6 VirtualEnv
  
- Actualizamos los scripts

	(freepbxbot.ini) 
  
		Actualizamos los valores de "token" y chat_id" con los valores correspondientes a nuestro bot y chat id
		
	(freepbxtgbot.service)
	
	Cambiamos las rutas para que correspondan con las que hemos empleado, tanto en 
		
		WorkingDirectory (la ruta ha la carpeta scripts), como en 
		ExecStart (Las rutas de la versión de python en nuestro carpeta VirtualEnv, como la ruta hacia el script bot_daemon.py)

	(bot_cli.sh)
		Actualizar las rutas correspondientes
		
		
- Creamos un enlace simbólico hacia freepbxbot.ini en /etc

	  ln -s /etc/freepbxbot.ini /opt/telegram-voicemail/freepbxbot.ini
	
- Creamos un enlace simbólico hacia freepbxtgbot.service en /usr/lib/systemd/system

	  ln -s /usr/lib/systemd/system/freepbxtgbot.service /opt/telegram-voicemail/scripts/freepbxtgbot.service
	
- Ahora instalamos el servicio freepbxtgbot

	  systemctl enable freepbxtgbot
	
	y lo iniciamos
	
	  systemctl start freepbxtgbot
	
	Si todo ha ido bien llegados a este punto, deberíamos ver publicado un mensaje en nuestro grupo de telegram indicando que el bot se ha iniciado correctamente.
	

# Instalación del cliente bot_cli.sh

  Este proceso se puede hacer tanto desde el interface de freepbx, como modificando el archivo voicemail.conf de asterisk directamente. En este ejemplo lo haremos modificando el archivo directamente porque de esta manera la explicación sirve para cualquier versión de Asterisk y no solo para FreePBX

  - Editamos el archivo /etc/asterisk/voicemail.conf y añadimos la siguiente línea en la sección [general]

		externnotify=/opt/telegram_voicemail/scripts/bot_cli.sh

  - Reiniciamos Asterisk

		systemctl restart asterisk

# Funcionamiento

  En teoría ya tenemos listo todo, ahora solo debemos indicar a FreePBX (o mas bien a Asterisk) que correos de voz deben publicarse en telegram.

  Para hacer esto, vamos a la extensión cuyos buzones queramos publicar y en la configuración de su buzón realizamos los siguientes pasos:

  1- Habilitamos (si no lo está ya) el envío de los buzones de voz al correo electrónico (para ello nos va a obligar a introducir una cuenta de correo electrónico, si no queremos realmente enviar estos buzones a ningún correo, poner una cuenta inventada, por ejemplo, noexiste@hotmail.com)

  2- Desactivamos (si está activada) la opción de borrar los mensajes del buzón tras enviarlos por correo electrónico.

  3- Modificamos el "contexto" del buzón de voz.

   En este punto tenemos dos opciones.

   Si queremos que se envíen los buzones a telegram y además conservarlos en la bandeja de entrada del buzón, ponemos como contexto

	telegram

   Si queremos que los mensajes se borren del buzón una vez publicados en telegram, ponemos como contexto

	telegram-delete

  Y listo, esto es todo, todos los mensajes que estén en estos contextos serán publicados en el grupo de telegram y si se deséa y se ha configurado, además serán enviados a sus correspondientes buzones de correo.

	
  
