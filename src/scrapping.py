#Take data from the university web site
#Fill in the form to access the page with the tables.
from bs4 import BeautifulSoup
import requests
import time
import re
from schec import NRC

params1 = {
    'elegido': '0029',
    'periodo': '202310',
    'nivel': 'PR'
}
params2 ={
    'valida': 'OK',
    'nrc': '2894',
    'BtnNRC': 'Buscar',
    'datos_periodo': '202310',
    'nom_periodo': 'Primer Semestre 2023',
    'datos_nivel': 'PR',
    'nom_nivel': 'Pregrado'

}

#URL all  NRC for department
url_departaments = "https://guayacan02.uninorte.edu.co/4PL1CACI0N35/registro/programas.php"
#URL for  obtain information from an nrc
url_nrcinfo = "https://guayacan02.uninorte.edu.co/4PL1CACI0N35/registro/resultado_nrc1.php"


"""""
response2 = requests.post(url_departaments,data=params1)
soup2 = BeautifulSoup(response2.text,"lxml")
print(soup2.prettify())

"""
response = requests.post(url_nrcinfo, data=params2)
soup = BeautifulSoup(response.text,"lxml")
nrcdiv = soup.find('div')


#Modeling data from an nrc scraping:
all_p = nrcdiv.find_all('p')

#NRCNAME
name = all_p[0].get_text()


#NRCCODE
third_p = all_p[2]
nrc = third_p.get_text(separator="|").split("|")[5].strip()


#QUOTAS
five_p = all_p[4]
quotas = five_p.get_text(separator="|").split("|")[3]


#BLOCKS
#--Extract information from all table rows except for the first one
blocks =[]
table = nrcdiv.find('table')
table_colums = table.find_all('tr')
table_colums = table_colums [1:]
for colum in table_colums:
    all_td = colum.find_all('td')
    block = [td.get_text(strip=True) for td in all_td]
    block = block[2:]
    blocks.append(block)


#TEACHER
five_p = all_p[5]
text = five_p.get_text();
text = text.replace("Profesor(es):", "").strip()
text = re.sub(r"([a-z])([A-Z])", r"\1-\2", text)
teachers = text.split("-")


pepe = NRC(name,int(nrc),blocks,int(quotas),teachers)
pepe.show_nrc()
