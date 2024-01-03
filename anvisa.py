import requests
import json
import time
import datetime
import os


class Anvisa:
    # Constants
    WAIT_TIME = float(0.4)
    URL = str('https://consultas.anvisa.gov.br/api/fila')
    HEADER = {'Authorization': 'Guest'}

    def getFromEndpoint(self, endpoint):
        time.sleep(Anvisa.WAIT_TIME)

        uri = f'{Anvisa.URL}{endpoint}'
        response = requests.request(
            'GET',
            uri,
            headers = Anvisa.HEADER
        )

        return json.loads(response.text)

    def extractAllToExcel(self, portais: list):
        for portal in portais:
            for area in self.getFromEndpoint(f'/area{portal}'):
                for filaOuLista in self.getFromEndpoint(f'/{area["id"]}/{portal}'):
                    for subFilaOuSubLista in self.getFromEndpoint(f'/{filaOuLista["id"]}/sub{portal}'):
                        tableEndpoint = f'/?filter%5Barea%5D={area["id"]}'
                        tableEndpoint += f'&filter%5Bfila%5D={filaOuLista["id"]}'
                        tableEndpoint += f'&filter%5Bsubfila%5D={subFilaOuSubLista["id"]}'

                        tableData = self.getFromEndpoint(tableEndpoint)

                        filtros = {"area": area["descricao"]}
                        filtros[portal] = filaOuLista["descricao"]
                        filtros[f'sub{portal}'] = subFilaOuSubLista["descricao"]

                        self.addTableDataToExcel(
                            portal,
                            tableData,
                            filtros
                        )

    def removeFileNameSpecCharact(self, fileName: str):
        fileName = fileName.replace('\\', '')
        fileName = fileName.replace('/', '')
        fileName = fileName.replace(':', '')
        fileName = fileName.replace('*', '')
        fileName = fileName.replace('?', '')
        fileName = fileName.replace('<', '')
        fileName = fileName.replace('>', '')
        fileName = fileName.replace('|', '')
        
        return fileName

    def addTableDataToExcel(self, portal: str, table, *arg):
        filtro1 = arg[0]["area"] if "area" in arg[0] else ""
        filtro2 = arg[0]["fila"] if "fila" in arg[0] else arg[0]["lista"]
        filtro3 = arg[0]["subfila"] if "subfila" in arg[0] else arg[0]["sublista"]

        if table:
            dtGeracaoFila = table[0]["dtGeracaoFila"]
        else:
            dtGeracaoFila = '--'

        csvHeader = f'Resultado da Consulta de {portal} de Análise\n'
        csvHeader += 'Filtros Utilizados\n'
        csvHeader += f'Área de Interesse: {filtro1}\n'
        csvHeader += f'{portal.title()}: {filtro2}\n'
        csvHeader += f'Sub {portal}: {filtro3}\n'
        csvHeader += f'Data e hora da última atualização da base de dados: {dtGeracaoFila}\n'
        csvHeader += f'Data e horário da exportação: {datetime.datetime.now()}\n\n'

        csvHeader += f'Data de Entrada;Processo;Expediente;Código de Assunto;Descrição do Assunto\n'

        fileName = f'{filtro1}_{filtro2}_{filtro3}'
        fileName = f'{self.removeFileNameSpecCharact(fileName)}.csv'

        path = f'./{portal}'
        
        if not os.path.exists(path):
            os.mkdir(path)

        with open(f'./{portal}/{fileName}', 'w', encoding='utf-8') as arquivo:
            arquivo.write(csvHeader)
            for linha in table:
                linhaCsv = f'{linha["dtEntrada"]};{linha["nuProcesso"]};{linha["nuExpediente"]};{linha["codAssunto"]};{linha["dsAssunto"]}\n'
                arquivo.write(linhaCsv)

        print(fileName)


if __name__ == '__main__':
    anvisa = Anvisa()
    anvisa.extractAllToExcel(['fila', 'lista'])