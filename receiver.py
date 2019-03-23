#!/usr/bin/env python
import pika
import sys
import os
UPLOAD_FOLDER = os.getcwd()+'/dl/protected/'
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
queue = "pictureWorkers"
channel.exchange_declare(exchange='Resize64', exchange_type='topic')

result = channel.queue_declare(queue = queue, durable=True)

channel.queue_bind(exchange='Resize64',queue=queue,routing_key="resize.picture")
print( "Kolejka: ---  %s " %(queue))
print(' [*] Waiting for logs. To exit press CTRL+C')

def callback(ch, method, properties, body):
    print("[RECEIVED]  %r:%r" % (method.routing_key, body))
    msg = body.decode('utf-8')
    #msg = msg.decode('utf-8')
    to_save = msg.split("/")
    to_save.insert( -1, "icons")
    path = '/'.join(to_save)
    print("Resize: %s => %s " % (msg,path))
    os.system("/usr/bin/convert "+msg+" -resize 64x64 "+path)
    
channel.basic_consume(callback,queue=queue,no_ack=True)

channel.start_consuming()
