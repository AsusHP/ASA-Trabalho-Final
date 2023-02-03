import psycopg2
import pika
import pickle
from config import host,dbname,password, port, user, host_mensagem

import pika
import pickle

#Conexão com o bando de dados
conn_string = 'host = {0} dbname = {1} password = {2} port = {3} user = {4}'.format(host,dbname,password, port, user)
conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

def login(email,senha_ide):

    sql = "SELECT senha FROM public.usuarios WHERE email = '{0}'".format(email)

    cursor.execute(sql)

    senha_db = cursor.fetchall()

    if len(senha_db) == 0:
        return False
    else:
        return (senha_ide == senha_db[0][0])

def aeroportos():

    aero = []    
    sql = "SELECT distinct origem FROM public.rotas order by origem"

    cursor.execute(sql)

    aeroportos = cursor.fetchall()

    for a in aeroportos:
        
        aero.append(a[0])

    return aero

def rotas(origem):
    destinos = []

    sql = "SELECT destino FROM public.rotas where origem = '{0}'".format(origem)

    cursor.execute(sql)

    consulta = cursor.fetchall()

    for i in consulta:

        destinos.append(i[0])

    return destinos

def execute_sql(sql,numero_pass=1):
    voos = []

    cursor.execute(sql)

    consulta = cursor.fetchall()

    for i in consulta:
        
        a = '{0}    -->    {1} - R${2},00 em {3} - id:{4}'.format(i[0],i[1],i[2]*numero_pass,i[3],i[4])
        voos.append(a)
    
    return voos

def voos(origem,destino,data):

    voos = []
    sql = "Select origem,destino,valor from public.voos where data = '{0}' and origem = '{1}' and destino = '{2}'".format(data,origem,destino)
    cursor.execute(sql)
    consulta = cursor.fetchall()

    for i in consulta:
        
        a = '{0}    -->    {1} - R${2},00'.format(i[0],i[1],i[2])

        voos.append(a)
    
    return voos

def voos_data(data):

    voos = []
    sql = "Select origem,destino,valor from public.voos where data = '{0}'".format(data)
    cursor.execute(sql)
    consulta = cursor.fetchall()

    for i in consulta:
        
        a = '{0}    -->    {1} - R${2},00'.format(i[0],i[1],i[2])

        voos.append(a)
    
    return voos

def compra(id_voo,email_compra,valor):

    #Conexão com a mensageria
    connection = pika.BlockingConnection(pika.ConnectionParameters(host = host_mensagem))
    channel = connection.channel()

    body = [id_voo,email_compra,valor]

    data = pickle.dumps(body)

    channel.basic_publish(exchange='ex_comandos', body=data, routing_key='tag_compra')
    channel.close()
    connection.close()

    sql = 'SELECT max(id) FROM public.vendas'

    cursor.execute(sql)
    consulta = cursor.fetchall()

    return [consulta[0][0]]
