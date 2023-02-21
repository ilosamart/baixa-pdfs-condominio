from csv import DictReader
from datetime import date, timedelta
import sys

import pandas as pd

from config import settings


def get_ipca():
    ipca_acumulado = {}
    ipca = []

    with open('/home/fabio/OneDrive/Condomínio Aconcágua/Índices//ipca-mes-a-mes.csv', 'rt') as file:
        ipca_csv = DictReader(file, delimiter=';',
                              fieldnames=('mes_ano', 'valor'))
        next(ipca_csv)
        acumulado = 1
        for ipca_mes in reversed(list(ipca_csv)):
            try:
                acumulado = acumulado * (1+float(ipca_mes['valor'])/100)
                ipca.append({
                    **ipca_mes,
                    'acumulado': acumulado,
                })
                ipca_acumulado[ipca_mes['mes_ano']] = acumulado
            except ValueError:
                continue
    return ipca_acumulado, ipca


def valor_presente():
    ipca_acumulado, ipca = get_ipca()
    data_analise = date(year=2013, month=11, day=1)
    hoje = date.today()

    while data_analise < hoje:
        data_analise = date(year=data_analise.year,
                            month=data_analise.month, day=1)
        file_name = f'{settings.dest_path}/{data_analise.year}_{str(data_analise.month).rjust(2, "0")}.xlsx'
        try:
            dados_mes = pd.read_excel(file_name, decimal=',', thousands='.')
            try:
                saldo = float(dados_mes.iloc[-1]['Saldo'])
            except ValueError:
                saldo = float(dados_mes.iloc[-1]['Saldo'].replace(' ', '').replace('.', '').replace(',', '.'))
            try:
                valor_presente = saldo * ipca_acumulado[f'{str(data_analise.month).rjust(2, "0")}/{data_analise.year}']
            except KeyError:
                valor_presente = saldo
            print(f'{data_analise},{saldo},{valor_presente}')
        except FileNotFoundError:
            print('Arquivo não encontrado', file_name, file=sys.stderr)
        data_analise += timedelta(days=32)

if __name__ == '__main__':
    valor_presente()
