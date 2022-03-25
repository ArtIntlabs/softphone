#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Built with pjproject (fork py37) - https://github.com/DiscordPhone/pjproject/tree/py37

import sys
import logging
import time
from pathlib import Path
from os import environ as env
from time import sleep
from dotenv import load_dotenv


from softphone.AIL_utills import AIL_Softphone
from softphone.Softphone import Softphone
from softphone.AudioCallbacks import EchoAudioCB, SystemAudioCB, AILAudioCB

load_dotenv(dotenv_path='.env.tmpl')
Path('temp/audio/').mkdir(parents=True, exist_ok=True)
Path('temp/rec/').mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename='example.log',
    filemode='a',
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
)

common_sample_rate = 16000
max_media_ports = 64

softphone = AIL_Softphone(sample_rate=common_sample_rate, max_media_ports=max_media_ports)

softphone.set_null_sound_device()

outbound = softphone.register(
    server=env.get('SIP_OUTBOUND_HOST'),
    port=env.get('SIP_OUTBOUND_PORT'),
    username=env.get('SIP_OUTBOUND_USER'),
    password=env.get('SIP_OUTBOUND_PASS')
)

# There are some cases when you need this, read the documentation for it. It is used when having python threads.
softphone.lib.thread_register("python worker")

print("\n\nSoftphone is now ready...")

while True:
    sleep(1)  # Just wait for the call state messages for a bit.. :)
    print('\n' * 2)
    print("+-Menu-----------------+")
    print("| m  = make call (def) |")
    print("| h  = hangup call     |")
    print("| a  = answer call     |")
    print("| q  = quit            |")
    print("+----------------------+")
    # choice = input("> ")
    choice = 'm'

    if choice == 'm':
        # number = input("Number with country code 00x (ex: 0014446665555)> ")
        number = '89996914784'
        # number = '89996990691'  # Саня Г.
        sip_uri = f'sip:{number}@{env.get("SIP_OUTBOUND_HOST")}:{env.get("SIP_OUTBOUND_PORT")}'

        # TODO: make a stream for permanent speech recording
        # TODO: Check if instantiating audio_buffer without self. gives less lag.
        audio_buffer = AILAudioCB(sample_rate=common_sample_rate)

        print('\n\n\n')
        softphone.create_audio_stream(audio_buffer)  # Move this inside call maybe?
        softphone.call(outbound, sip_uri)
        print(70, 'Начинаем звонить')
        softphone.wait_for_confirmed_call()
        print(72, 'Клиент взял трубку')
        softphone.capture(file_name=f'temp/audio1/{time.ctime()}_{number}.wav')
        print(74, 'Начало записи разговора')
        softphone.playback(file_name=f'temp/SG.wav')
        softphone.wait_for_active_audio()
        print(77, 'Активация голоса оператора оператора')
        time.sleep(3)
        softphone.stop_playback()
        print(80, f'Стоп воспроизведения аудио оператора по истечении некоторого времени')
        softphone.start_listening()
        time.sleep(5)
        softphone.stop_listening()
        time.sleep(3)
        softphone.get_buffer_t(save=f'temp/rec/{time.ctime()}_{number}.wav')
        print(87, f'Записываем в файл весь аудиобуфер')
        softphone.stop_capturing()
        print(89, f'stop_capturing')
        softphone.end_call()
        print(91, f'end_call')
        softphone.destroy_audio_stream()
        print(93, f'destroy_audio_stream')
        print(94, f'Полное завершение разговора')
        exit()

    if choice == 'a':
        # TODO: Must be implemented.
        pass

    if choice == 'h':
        softphone.end_call()
        softphone.destroy_audio_stream()

    if choice == 'q':
        print('Exiting...')
        # softphone.unregister(inbound)
        softphone.unregister(outbound)
        sys.exit()

# end

# python3: ../src/pjmedia/conference.c:986: pjmedia_conf_connect_port: Assertion `conf && src_slot<conf->max_ports && sink_slot<conf->max_ports' failed.
