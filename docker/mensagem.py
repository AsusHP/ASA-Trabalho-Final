import pika
import pickle
import psycopg2
from config import host,dbname,password, port, user, host_mensagem

#Conexão com o bando de dados
conn_string = 'host = {0} dbname = {1} password = {2} port = {3} user = {4}'.format(host,dbname,password, port, user)


connection = pika.BlockingConnection(pika.ConnectionParameters(host = host_mensagem))
channel = connection.channel()

def compra(ch, method, properties, body):

    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

    data = pickle.loads(body)
    
    sql = 'INSERT INTO public.vendas (email_cliente, id_voo, valor) VALUES(%s, %s,%s)'
    dados = (data[1],data[0],data[2])

    cursor.execute(sql,dados)
    conn.commit()
    cursor.close()
    conn.close()

    print('Venda registrada')

    return

#Criar Exchange
channel.exchange_declare(exchange='ex_comandos',exchange_type='direct')

#Criar Filas
channel.queue_declare(queue= 'comando_compra')

#Cria as Bind
channel.queue_bind(exchange='ex_comandos', queue='comando_compra', routing_key='tag_compra')

#Consumir a fila
channel.basic_consume(queue='comando_compra',on_message_callback=compra,auto_ack=True)

print('Iniciando Consumo')

channel.start_consuming()