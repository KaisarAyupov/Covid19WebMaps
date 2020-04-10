import requests, re
from bs4 import BeautifulSoup
import pandas as pd 
import folium
from folium.plugins import Draw

r=requests.get("https://www.coronavirus2020.kz/ru")
c=r.content
soup=BeautifulSoup(c,"html.parser")
all=soup.find_all("div",{"class":"city_cov"})
covid_19 = (all[0].text).replace('\t\t',' ').replace('\n',', ').replace(' – ',': ')
l = covid_19.split(',')
data_cov=pd.DataFrame(l)
##print(df)

# dropping null value columns to avoid errors 
data_cov.dropna(inplace = True)
# new data frame with split value columns 
new = data_cov[0].str.split(":", n = 1, expand = True) 
# making separate first name column from new data frame 
data_cov["City"]= new[0]
# making separate last name column from new data frame 
data_cov["covid19"]= new[1] 
# Dropping old Name columns 
data_cov.drop(columns =[0], inplace = True)
##print(data)
##columns = data.columns
# df display 
covid19 = data_cov.iloc[1:-1]
#Create a DataFrame object
geocovid19 = pd.DataFrame(covid19)
print(geocovid19['covid19'].sum())
class_id = pd.Series([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18])
xdd = pd.Series([0, 71.43696,76.942934,69.531221,69.901514,58.596482,77.928852,52.083663,81.494236,72.139875,50.673668,70.99457,64.01718,63.641641,53.971744,76.242826,69.266071,68.449423])
ydd = pd.Series([0, 51.143885,43.215482,42.346375,51.787224,48.604025,44.980398,47.476414,48.798196,44.31766,49.792786,48.223676,51.601806,45.194056,44.112844,52.070653,53.856356,43.221283])
geocovid19['class_id'] = class_id
geocovid19['xdd'] = xdd
geocovid19['ydd'] = ydd

geocovid19.to_csv('covid_stat.txt', index=False)

############################################## Create Map

data = pd.read_csv("covid_stat.txt")
lat = list(data["ydd"])
lon = list(data["xdd"])
cov = list(data["covid19"])
def color_producer(elevation):
    if elevation < 10:
        return 'green'
    elif 10 <= elevation < 100:
        return 'orange'
    else:
        return 'red'

def radius_producer(amount):
    if amount < 10:
        return 5
    elif 10 <= amount < 100:
        return 15
    else:
        return 30
map = folium.Map(location=[46.42, 68.474], zoom_start=5)
tooltip = 'Click me!'

covpnt = folium.FeatureGroup(name="Зарегистрированных случаев")

for lt, ln, co in zip(lat, lon, cov):
    covpnt.add_child(folium.CircleMarker(location=[lt, ln], radius = radius_producer(co), popup= "Зарегистрировано:"+str(co)+"чел.",
    fill_color=color_producer(co), fill=True, tooltip=tooltip, color = 'grey', fill_opacity=0.7))

covpol = folium.FeatureGroup(name="Подтверждённые случаи на территории", show=False)

covpol.add_child(folium.GeoJson(data=open(r'adm1pol.json', encoding='utf-8-sig').read(),
style_function=lambda x: {'fillColor':'green' if x['properties']['covid19'] <= 1
else 'orange' if 2 <= x['properties']['covid19'] < 50 else 'red' if 50 <= x['properties']['covid19'] < 100 else 'blue'}))

import datetime
x = datetime.datetime.now()

info_cov=soup.find_all("span",{"class":"number_cov marg_med"})[0].get_text()
recovered=soup.find_all("div",{"class":"recov_bl"})[0]
covid_rec = recovered.text
cov=soup.find_all("div",{"class":"city_cov"})[1]
city_cov = cov.text
deaths = [i.text for i in soup.select('.deaths_bl span')]
deaths_al=soup.find_all("div",{"class":"city_cov"})[2].get_text()
legend_html = """
<div style="position: fixed; 
     bottom: 50px; left: 50px; max-width: 400px; height: auto; 
     border:2px solid grey; z-index:9999; padding: 5px; background-color: white;
     "> <p class="text-uppercase" style="margin: 0px;">Зарегистрированных случаев: """ + info_cov +"""</p>
<div class="row" style="font-size:smaller;" >
  <div class="col-sm-6">
    <div class="card border-success">
      <div class="card-body text-success">
        <h5 class="card-title">""" + covid_rec +"""</h5>
        """ + city_cov + """
      </div>
    </div>
  </div>
  <div class="col-sm-6">
    <div class="card">
      <div class="card-body text-warning">
        <h5 class="card-title">Летальных случаев:""" + deaths[1] +"""</h5>
        """ + deaths_al + """
      </div>
    </div>
  </div>
</div>
<p class="text-muted" style="font-size:x-small;">Data comes from <a href="https://www.coronavirus2020.kz/"> coronavirus2020.kz</a></p>
</div>"""
draw = Draw()

draw.add_to(map)
map.get_root().html.add_child(folium.Element(legend_html))

map.add_child(covpnt)
map.add_child(covpol)
map.add_child(folium.LayerControl())

map.save("index.html")
