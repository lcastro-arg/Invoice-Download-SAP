'''
Llamada RFC a SAP:
 - Query:
    - MONAT : Periodo. Comienza en mes tres
    - GJAHR : Ejercicio
    - BLART : Clase de documento
    - BLDAT : Fecha de documento
    - XBLNR : Número de referencia del documento
'''

from pyrfc import Connection, ABAPApplicationError, ABAPRuntimeError, LogonError, CommunicationError

class SAPLogOn():

    def __init__(self, ashost, sysnr, client, usr, pss):
        self.conn = Connection(ashost= ashost, sysnr= sysnr, client= client, user= usr, passwd= pss)

    #- Para leer una tabla a partir de rfc_read_table
    def Read_table(self, table, options, fields) -> dict:
        
        # A saber: 
            # RFC_READ_TABLE tiene un límite de 512 caracteres y puede causar abap error si la tabla contiene datos tipo float.
            # Probar con BBP_RFC_READ_TABLE para resolver issue por datos tipo float, mas no resuelve límite de caracteres.
            # Si se pasa fields como [] se traen todos los campos por default.

        # Inputs:
            # TABLE = Tabla 
            # FIELDS = lista de campos a devolver. Pasar lista vacia si se desean todos los campos
            # OPTIONS = Lista de where conditions. Límite de 72 caracteres.

        # Output: 
            # Devuelve diccionario con FIELDS y DATA. Cada uno de ellos contiene una lista de diccionarios.
            # Devuelve 0 si el query no obtuvo resultados
            # Devuelve 1 si hubo un error de comunicación o ABAP

            
        # Fields a devolver
        fields = [{'FIELDNAME': x} for x in fields]

        # Where conditions 
        options = [{'TEXT': x} for x in options]
        
        # Realiza el query a tabla indicada
        try:
            result = self.conn.call('RFC_READ_TABLE',
            QUERY_TABLE = table,
            FIELDS = fields,
            DELIMITER = ',',
            OPTIONS = options,
            ROWCOUNT = 10)
        except (ABAPApplicationError, ABAPRuntimeError, LogonError, CommunicationError):
            return 1
        else:
            return result if len(result['DATA']) >= 1 else 0    # 0 --> Query sin resultados

    def procResult(self, json) -> list[dict[dict]]:
        # Devuelve diccionario de listas
        
        output = dict()
        
        for dic in json['DATA']:
            output[dic['WA'].split(',')[3]] =   {'fecha' : dic['WA'].split(',')[0],
                                                'clase' : dic['WA'].split(',')[2],
                                                'referencia' : dic['WA'].split(',')[1].strip(' ')
                                                }


        return output

if __name__ == '__main__':
    Sap = SAPLogOn(ashost= 'serverIp',
                    sysnr= '00',
                    client= 'client',
                    usr= 'username',
                    pss= 'password',
                    )

    # Example
    responseSap = Sap.Read_table(table= 'BKPF',
                        options= ["XBLNR EQ '0002A00000003' AND GJAHR EQ '2021'"],
                        fields= ['BLDAT','XBLNR', 'BLART', 'BELNR'])


    