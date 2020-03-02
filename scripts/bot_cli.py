#!/bin/env python3

import sys
import configparser
import os
import glob
import socket
import pickle
import bot_daemon
import datetime

VM_CONTEXT = str(sys.argv[1])
EXTENSION = str(sys.argv[2])
BORRAR = False

contexto = VM_CONTEXT.split('-')
if len(contexto) > 1 and contexto[1].lower() == 'delete':
    BORRAR = True

if contexto[0].lower() == 'telegram':
    ruta = '/var/spool/asterisk/voicemail/'+VM_CONTEXT+'/'+EXTENSION+'/INBOX/'

    mensajes = glob.glob(ruta+'*.txt')
    mensaje = max(mensajes, key=os.path.getctime)
    nombre, sufijo = os.path.splitext(os.path.basename(mensaje))

    config = configparser.ConfigParser()
    config.read(mensaje)
    
    fecha = datetime.datetime.fromtimestamp(int(config['message']['origtime']))
    fecha = fecha.strftime("%d/%m/%Y a las %H:%M")
    segundos = int(config['message']['duration'])
    
    texto_tg = 'Nuevo mensaje de voz:\n\n'
    texto_tg += 'De: '+config['message']['callerid']+'\n'
    texto_tg += 'Duración: '+'%d:%02d' % (segundos / 60, segundos % 60)+' segundos\n'
    texto_tg += 'Fecha: '+fecha+'\n'

    archivowav = open(ruta+nombre+'.wav', mode='rb').read()
    datos = pickle.dumps((archivowav,texto_tg))

    sock = socket.socket()
    sock.connect((bot_daemon.network_settings["bind_ip"],int(bot_daemon.network_settings["bind_port"])))
    sock.send(datos)
    sock.close()

    if BORRAR:
        os.remove(ruta+nombre+'.txt')
        os.remove(ruta+nombre+'.wav')