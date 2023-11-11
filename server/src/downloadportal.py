from pathlib import Path

from bs4 import BeautifulSoup
import requests
import pandas as pd

from config import settings


meses = {
    'Janeiro': '01',
    'Fevereiro': '02',
    'Março': '03',
    'Abril': '04',
    'Maio': '05',
    'Junho': '06',
    'Julho': '07',
    'Agosto': '08',
    'Setembro': '09',
    'Outubro': '10',
    'Novembro': '11',
    'Dezembro': '12',
}

url = f'https://portal.auxiliadorapredial.com.br/LoginSenha.aspx?cpfcnpj={settings.cpf}&nome={settings.nome}'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.17 (KHTML, like Gecko)  Chrome/24.0.1312.57 Safari/537.17',
}

def get_aspx_data(bso):
  viewstate = bso.select("#__VIEWSTATE")[0]['value']
  viewstategen = bso.select("#__VIEWSTATEGENERATOR")[0]['value']
  eventvalidation = bso.select("#__EVENTVALIDATION")[0]['value']
  return {
      '__VIEWSTATE': viewstate,
      '__VIEWSTATEGENERATOR': viewstategen,
      '__EVENTVALIDATION': eventvalidation,
  }


def get_period_buttons(tag):
    return 'id' in tag.attrs and 'rptPeriodo_linkButton' in tag['id']


with requests.Session() as s:
    r = s.get(url, headers=headers)
    bso = BeautifulSoup(r.text, "html5lib")
    data = get_aspx_data(bso)
    form_data = {
        **data,
        '__EVENTTARGET':'',
        '__EVENTARGUMENT':'',
        'txtSenha': settings.senha,
        'btnEntrar': 'Entrar',
        'txtLarguraTela': '1920',
    }
    r = s.post(url, data=form_data, headers=headers)

    bso = BeautifulSoup(r.text, "html5lib")
    data = get_aspx_data(bso)

    form_data = {
        **data,
        '__EVENTTARGET':'',
        '__EVENTARGUMENT':'',
        'grdPerfis$ctl02$btnSelecionar': 'Acessar+Perfil',
    }
    r = s.post('https://portal.auxiliadorapredial.com.br/SelecionaPerfil.aspx', data=form_data, headers=headers)
    r = s.get('https://portal.auxiliadorapredial.com.br/Extrato.aspx', headers=headers)
    bso = BeautifulSoup(r.text, "html5lib")
    periodos = bso.find_all(get_period_buttons)
    for periodo in periodos:
        link = periodo['href'].split('"')[1]
        mes, ano = periodo.text.split('/')
        mes = meses[mes]
        file_dst = Path(f'{settings.dest_path}/{ano}_{mes}.xlsx')
        if not file_dst.exists():
            # print(f"{periodo['id']}: {periodo.text} - {link}")

            data = get_aspx_data(bso)
            form_data = {
                **data,
                '__EVENTTARGET': link,
                '__EVENTARGUMENT': '',
            }
            r = s.post('https://portal.auxiliadorapredial.com.br/Extrato.aspx', data=form_data, headers=headers)
            bso = BeautifulSoup(r.text, "html5lib")
            tabela_extrato = bso.find('table')
            df = pd.read_html(str(tabela_extrato), thousands='.', decimal=',')
            df[0].to_excel(file_dst, index=False)
            print(f'{periodo.text} salvo em {file_dst}')
        else:
            print(f'{file_dst} já existe.')
        
