from PySimpleGUI import PySimpleGUI as sg
import comandos

# Layouts

def janela_login():
    sg.theme("Reddit")
    layout = [
        [sg.Text('Usuário'),sg.Input(key='usuario',size=(50,1))],
        [sg.Text('Senha'),sg.Input(key='senha',password_char='*',size=(20,1))],
        [sg.Button('Entrar')],
        [sg.Text('Email ou Senha incorretos',key='mensagem_erro',visible=False,text_color='red')]
    ]
    return sg.Window('Tela de Login',layout,finalize=True)

def janela_menu():
    sg.theme("Reddit")
    layout = [
        [sg.Text('Bem Vindo:')],
        [sg.Text('',key='email_nome')],
        [sg.Button('Efetuar Compras')],
        [sg.Button('Minhas Compras')],
        [sg.Button('Logout')]
    ]
    return sg.Window('Menu',layout,finalize=True)

def janela_comprar():
    sg.theme("Reddit")
    layout = [
        [sg.Text('Bem Vindo:')],
        [sg.Text('',key='email_nome')],
        [sg.Text('Aeroporto de Origem:')],
        [sg.Combo(values=[1,2,3],key='aero_origem',size=(20,1),enable_events=True)],
        [sg.Text('Aeroporto de Destino:')],
        [sg.DD(values=[],key='aero_destino',size=(20,1))],
        [sg.Text('Numero de Passagerios:')],
        [sg.DD(values=[1,2,3,4,5,6,7,8,9,10],key='numero_passageiros',size=(20,1),default_value=1)],
        [sg.Text('Selecione uma data:')],
        [[sg.Input(key='IN', size=(20,1)), sg.Button('Date'),]],
        [sg.Button('Buscar Voos'),sg.Button('Voltar Página')]
    ]
    return sg.Window('Menu',layout,finalize=True)

def janela_listagem():
    sg.theme("Reddit")
    layout = [
        [[sg.Button('Encerrar'),sg.Button('Comprar')]],
        [sg.LB(values=[],key='lb',size=(50,25),enable_events=True)]

    ]
    return sg.Window('Menu',layout,finalize=True)

def janela_mensagem():
    layout=[
        [sg.Text('',key='tela_mensagem')],
        [sg.Button('ok')]
    ]
    return sg.Window('',layout,finalize=True)

#Inicia as janelas
janela1, janela2, janela3 = janela_login(), None, None

# Ler os eventos
while True:

    window, event, values = sg.read_all_windows()

    if event == sg.WIN_CLOSED:
        break
    
    if event == 'Date':

        date = sg.popup_get_date(close_when_chosen=True)

        if date:
            month, day, year = date
        window['IN'].update(f"{year}-{month:0>2d}-{day:0>d}")

    if event == 'Encerrar':
        janela4.close()

    if window == janela3 and event == 'Buscar_aero':

        if values['DD'] == "":
            janela3.Element("mensagem_erro_busca").update(visible=True)
        else:
            janela3.Element("mensagem_erro_busca").update(visible=False)
            destinos = comandos.rotas(values['DD'])
            janela4 = janela_listagem()
            janela4.Element('lb').update(values=destinos)

    if window == janela3 and event == 'Voltar Página':
        janela3.close()
        janela2.un_hide()

    if window == janela1 and event == 'Entrar':
        
        verifica_senha = comandos.login(window['usuario'].get(),window['senha'].get())

        if verifica_senha:
            janela2 = janela_menu()
            janela2.Element('email_nome').update(janela1.Element('usuario').get())
            janela1.close()
        else:
            window['mensagem_erro'].update(visible = True)

    if window == janela2 and event == 'Efetuar Compras':

        aero = comandos.aeroportos()

        janela2.hide()
        janela3 = janela_comprar()
        janela3.Element('email_nome').update(janela1.Element('usuario').get())
        janela3.Element('aero_origem').update(values=aero)

    if event == 'aero_origem':
        
        destinos = comandos.rotas(values['aero_origem'])

        window['aero_destino'].update(values=destinos)

    if event == 'Buscar Voos':

        numero_pass = values['numero_passageiros']

        if values['aero_origem'] == '' and values['aero_destino'] == '' and values['IN'] != '':

            sql = "Select origem,destino,valor,data,id from public.voos where data = '{0}'".format(values['IN'])
            destinos = comandos.execute_sql(sql,numero_pass)
            janela4 = janela_listagem()
            janela4.Element('lb').update(values=destinos)        

        elif values['aero_origem'] != '' and values['aero_destino'] != '' and values['IN'] == '':

            sql = "Select origem,destino,valor,data,id from public.voos where origem = '{0}' and destino = '{1}'".format(values['aero_origem'],values['aero_destino'])
            destinos = comandos.execute_sql(sql,numero_pass)
            janela4 = janela_listagem()
            janela4.Element('lb').update(values=destinos)  

        else:       
            destinos = comandos.voos(values['aero_origem'],values['aero_destino'],values['IN'])
            janela4 = janela_listagem()
            janela4.Element('lb').update(values=destinos)

    if event == 'Comprar':

        voo_id = values['lb'][0].split(":")[1]
        email = janela2.Element('email_nome').get()
        valor = values['lb'][0].split(' ')[10].split('$')[1].split(',')[0]

        token = comandos.compra(voo_id,email,valor)

        janela5 = janela_mensagem()
        mensagem = 'Parabens, compra efetua com sucesso. Id Voo:{0} e e-token:{1}'.format(voo_id,token[0])
        janela5.Element('tela_mensagem').update(mensagem)
    
    if event == 'ok':

        janela5.close()
        janela4.close()
    
    if event == 'Minhas Compras':

        sql = "select o.origem,o.destino,v.valor, o.{0}, v.id_voo from public.vendas v left join public.voos o on cast(id_voo as int) = o.id where email_cliente = '{1}'".format("data",janela2.Element('email_nome').get())
        destinos = comandos.execute_sql(sql)
        janela4 = janela_listagem()
        janela4.Element('lb').update(values=destinos) 
        janela4.Element('Comprar').update(visible=False)
    
    if event == 'Logout':

        janela2.close()
        janela1 = janela_login()

window.close()