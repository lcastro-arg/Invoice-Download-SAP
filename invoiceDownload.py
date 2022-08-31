'''
Bajar las facturas de Mis comprobantes - AFIP.
Baja un .xlsx a la carpeta default del browser (\Downloads)
'''
#Selenium - Web Scraping
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service

#Uso general
import sys
import time
import datetime
import os
import shutil


#--- Paths --------------------------------------------------------'
PATH = 'C:\\Program Files (x86)\\chromedriver.exe'
SRC  = 'C:\\Users\\user\\Downloads\\Mis Comprobantes Recibidos - CUIT 30540080298.xlsx'
DST = 'C:\\Users\\user\\OneDrive - rioplatense.com\\Proyectos\\Administración\\'

#--- Classes ----------------------------------------------------------'
class Afip():
    url_afip = 'https://auth.afip.gob.ar/contribuyente_/login.xhtml'
    today          = datetime.datetime.today()
    fourWeeksBefore = (today - datetime.timedelta(weeks=4))

    def __init__(self, user : str, password : str, fecha_desde = fourWeeksBefore, fecha_hasta = today):
        self.driver = webdriver.Chrome(PATH)
        self.username = user
        self.password = password
        self.fecha_desde = fecha_desde.strftime('%d/%m/%Y') if type(fecha_desde) != str else fecha_desde
        self.fecha_hasta = fecha_hasta.strftime('%d/%m/%Y') if type(fecha_hasta) != str else fecha_hasta

    def LogIn(self) -> None:

        self.driver.get(self.url_afip)

        #-- Esperar que cargue la página
        while True:
            if self.driver.title == 'Acceso con Clave Fiscal - AFIP':
                break
            else:
                time.sleep(1)

        user = self.driver.find_element(By.ID,'F1:username')
        user.clear()
        user.send_keys(self.username)
        user.send_keys(Keys.RETURN)

        #-- Esperar que aparezca el campo password
        try:
            password = WebDriverWait(self.driver, 15).until(
                                EC.presence_of_element_located((By.ID, "F1:password")))
        except:
            print('Se colgó afip cargando password')
            self.driver.quit()   # Se colgó afip
            sys.exit()
        else:
            password.clear()
            password.send_keys(self.password)
            password.send_keys(Keys.RETURN)

    def misComprobantes(self) -> None:
        
        #-- Buscar e ingresar a Mis comprobantes

        myServices = WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/main/section/div/ul/li[3]/a/span')))
        myServices.click()

        try:
            bodies = WebDriverWait(self.driver, 15).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'bold')))
        except  TimeoutException:
            print('Se colgo AFIP cargando Mis Comprobantes')
            self.driver.quit()
            sys.exit()
        else:     
            #Para evitar el XPATH y que sea usable por otro usuario
            for body in bodies:
                if 'Mis Comprobantes' in body.text:
                    body.click() 
                    break 
                    
        #-- Capturar new tab
        for i in range(10):
            try:
                self.driver.switch_to.window(self.driver.window_handles[1]) # Capturar pop up
            except IndexError:
                time.sleep(1)
            else:
                break
        
        #-- Ingresar a comprobantes Recibidos
        bodies = WebDriverWait(self.driver, 15).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'panel-body')))
        for body in bodies:
            if 'Recibidos' in body.text:
                body.click()
                break
        
        #-- Filtrar fechas a buscar
        fecha_desde_hasta = WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.ID, 'fechaEmision')))
        fecha_desde_hasta.clear()
        fecha_desde_hasta.send_keys(f"{self.fecha_desde} - {self.fecha_hasta}")
        buscar = WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.ID, 'buscarComprobantes')))
        buscar.click()
        
        # Los resultados demoran unos segundos...

        time.sleep(30)
        buttons = WebDriverWait(self.driver, 60).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'button')))
        for button in buttons:
            if 'Excel' in button.text:
                button.click()
                time.sleep(10)   #Esperar a que termine de bajar el archivo.
                break
        
    def closeAfip(self):
        self.driver.quit()

# ----------- Main -------------------------------------------
if __name__ == '__main__':
    afip = Afip(user= 'cuit', password= 'password')
    afip.LogIn()
    afip.misComprobantes()
    afip.closeAfip()

    if os.path.exists(SRC):
        shutil.move(SRC,DST)


    sys.exit()