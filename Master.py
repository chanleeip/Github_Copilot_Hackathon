from pyowm.owm import OWM
from pyowm.utils import formatting,timestamps
from geopy.geocoders import Nominatim
import requests
import matplotlib.pyplot as plt
import datetime
# import mpld3
import json
from flask import Flask, request, jsonify, session
from flask_session import Session
from flask_cors import CORS
import csv
import pandas as pd
import pvlib
from pvlib.pvsystem import PVSystem, FixedMount
from pvlib.location import Location
from pvlib.modelchain import ModelChain
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS
from datetime import date, timedelta
import wind_energy_output_find

app = Flask(__name__)
CORS(app)
app.config['SESSION_TYPE'] = 'memcached'
app.config['SECRET_KEY'] = 'super secret key'
sess = Session()
owm = OWM("9297169f55274dfbf3f79162c9678b13")
mgr = owm.weather_manager()
accu_api="L1jY2SjkhBlsbhZG7c3uAJo3iVtIlZBe"
solcast_api="pZipflSatVeWc30GUTP2TxgXL-R4iVIa"
API_KEY="89acdee0-d06d-11ed-b59d-0242ac130002-89acdf58-d06d-11ed-b59d-0242ac130002"

# city=input("city : ")
# def get_current_lat_long():
#     geolocator = Nominatim(user_agent="geoapiExercises")
#
#     # Get current location using geolocator
#     geolocator = Nominatim(user_agent="geoapiExercises")
#
#     # Get current location using geolocator
#
#     location = geolocator.geocode("")
#     lat = location.latitude
#     long = location.longitude
#
#
#     return lat, long
#
import pymongo
server = pymongo.MongoClient('mongodb+srv://chanleeip4:nithin@cluster0.ulg7ukt.mongodb.net/?retryWrites=true&w=majority')
db = server['temp_db']
tb = db['temp_tb']

def send_data_tb(lat,long):
    tb.update_one({},{"$set": {"lat": lat, "long": long}})

def get_data_tb():
    temps = tb.find_one({},{'_id':0})
    return 10,20
    return temps['lat'],temps['long']

@app.route('/sendlatlong', methods=['POST'])
def getLatLong():
    
    data = request.get_json()
    send_data_tb(data['lat'],data['long'])
    
    # print(lat, long)
    # return (lat, long)
    return 'Success'
    # return jsonify({temperature_forecasting(lat, long),
    # relative_humidity(lat, long),
    # irradiance_forecasting(lat, long),
    # dewpoint_forecasting(lat, long),
    # rain_forecasting(lat, long),
    # precipitation_forecasting(lat, long), 
    # cloudcover_forecasting(lat, long),
    # windspeed_forecasting(lat, long)})




def get_datasheet_for_wind():
    latitude , longitude = get_data_tb()
    latitude = float(latitude)
    longitude = float(longitude)    
    Start_date = "2023-04-26" 
    end_datae = "2023-05-03" 
    url = f"https://api.open-meteo.com/v1/forecast?start_date={Start_date}&end_date={end_datae}&latitude={latitude}&longitude={longitude}&hourly=temperature_2m,surface_pressure,windspeed_10m,windspeed_80m,temperature_80m"
    response = requests.get(url)
    dataa = response.json()
    print(dataa)
    time = dataa['hourly']['time']
    pressure = dataa['hourly']['surface_pressure']
    temperature = dataa['hourly']['temperature_2m']
    wind_speed = dataa['hourly']['windspeed_10m']
    temperature_1 = dataa['hourly']['temperature_80m']
    wind_speed_1 = dataa['hourly']['windspeed_80m']
    print(type(time))
    with open('weather_1.csv', 'w', newline='') as csvfile:
        fieldnames = ['variable_name','pressure', 'temperature', 'wind_speed', 'roughness_length', 'temperature_1','wind_speed_1']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # write the header row
        writer.writeheader()
        roww={'variable_name':'height','pressure':0,'temperature':2, 'wind_speed':10, 'roughness_length':0, 'temperature_1':10,'wind_speed_1':80}
        # write a row with all of the data
        writer.writerow(roww)
        for i in range(len(time)):
            row = {'variable_name': time[i], 'pressure': pressure[i]*1000, 'temperature': temperature[i]*10,
                   'wind_speed': wind_speed[i], 'roughness_length':0.15,'temperature_1':temperature_1[i],'wind_speed_1':wind_speed_1[i]}
            writer.writerow(row)



def find_current_weather_status(lat, long):
    observation = mgr.weather_at_coords(lat, long)
    weather = observation.weather
    return (weather.detailed_status)

# def find_current_and_today_min_max_temperature(lat,long):
#     weather = mgr.weather_at_coords(lat,long).weather
#     temp_dict_fahrenheit = weather.temperature('fahrenheit')
#     return(temp_dict_fahrenheit['temp_min'],temp_dict_fahrenheit['temp_max'])
def is_it_going_to_rain_tomorrow(lat,long):
    mgr = owm.weather_manager()
    three_h_forecaster = mgr.forecast_at_coords(lat,long,interval='3h')
    tomorrow = timestamps.tomorrow()  # datetime object for tomorrow
    return three_h_forecaster.will_be_rainy_at(tomorrow)
# def sunrise_sunset(lat,long):
#     mgr = owm.weather_manager()
#     observation = mgr.weather_at_coords(lat,long)
#     weather = observation.weather
#     sunrise_unix = weather.sunrise_time()  # default unit: 'unix'
#     sunrise_iso = weather.sunrise_time(timeformat='iso')
#     sunrise_date = weather.sunrise_time(timeformat='date')
#     sunrset_unix = weather.sunset_time()  # default unit: 'unix'
#     sunrset_iso = weather.sunset_time(timeformat='iso')
#     sunrset_date = weather.sunset_time(timeformat='date')
#     return(sunrise_iso[11:19],sunrset_iso[11:19])
def lat_long_find(city):
    try:
        geolocator = Nominatim(user_agent="MyApp")
        location = geolocator.geocode(city)
        print("The latitude of the location is: ", location.latitude)
        print("The longitude of the location is: ", location.longitude)
        latitude=location.latitude
        longitude=location.longitude

    except TypeError:
        print("Coordinates of " + city + "is not found")
def current_temperature(lat,long):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&hourly=temperature_2m&timezone=Asia/Tokyo&limit=7"
    response = requests.get(url)
    data = response.json()
    temperature = data["hourly"]["temperature_2m"]
    return temperature[0]
def get_datasheet_for_normal_machine_learning():
    latitude , longitude = get_data_tb()
    latitude = float(latitude)
    longitude = float(longitude)    
    Start_date = "2023-04-26" 
    end_datae = "2023-05-03" 
    url = f"https://api.open-meteo.com/v1/forecast?start_date={Start_date}&end_date={end_datae}&latitude={latitude}&longitude={longitude}&hourly=temperature_2m,windspeed_10m,shortwave_radiation,direct_radiation,diffuse_radiation,direct_normal_irradiance,terrestrial_radiation"
    response = requests.get(url)

    # Parse the JSON response to a list of dictionaries
    dataa = response.json()
    print(dataa)
    # print(dataa)
    time = dataa['hourly']['time']
    temperature = dataa['hourly']['temperature_2m']
    windspeed = dataa['hourly']['windspeed_10m']
    shortwave_radiation = dataa['hourly']['shortwave_radiation']
    diffuse_radiation = dataa['hourly']['diffuse_radiation']
    direct_normal_irradiance = dataa['hourly']['direct_normal_irradiance']
    print(type(time))

    # Open a new file to write the CSV data
    with open('data.csv', 'w', newline='') as csvfile:
        fieldnames = ['ghi', 'dni', 'dhi', 'temp_air', 'wind_speed']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # write the header row
        writer.writeheader()

        # write a row with all of the data
        for i in range(len(time)):
            row = {'ghi': shortwave_radiation[i], 'dni': direct_normal_irradiance[i], 'dhi': diffuse_radiation[i],
                   'temp_air': temperature[i], 'wind_speed': windspeed[i]}
            writer.writerow(row)




def get_datasheet_for_price_future():
    latitude , longitude = get_data_tb()
    latitude = float(latitude)
    longitude = float(longitude)
    Start_date = date.today().strftime("%Y-%m-%d") 
    end_datae = (date.today() + timedelta(days=7)).strftime("%Y-%m-%d")
    url = f"https://api.open-meteo.com/v1/forecast?start_date={Start_date}&end_date={end_datae}&latitude={latitude}&longitude={longitude}&hourly=temperature_2m,windspeed_10m,shortwave_radiation,direct_radiation,diffuse_radiation,direct_normal_irradiance,terrestrial_radiation"
    response = requests.get(url)

    # Parse the JSON response to a list of dictionaries
    dataa = response.json()
    # print(dataa)
    time = dataa['hourly']['time']
    temperature = dataa['hourly']['temperature_2m']
    windspeed = dataa['hourly']['windspeed_10m']
    shortwave_radiation = dataa['hourly']['shortwave_radiation']
    diffuse_radiation = dataa['hourly']['diffuse_radiation']
    direct_normal_irradiance = dataa['hourly']['direct_normal_irradiance']
    print(type(time))

    # Open a new file to write the CSV data
    with open('data_prices_future.csv', 'w', newline='') as csvfile:
        fieldnames = ['ghi', 'dni', 'dhi', 'temp_air', 'wind_speed']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # write the header row
        writer.writeheader()

        # write a row with all of the data
        for i in range(len(time)):
            row = {'ghi': shortwave_radiation[i], 'dni': direct_normal_irradiance[i], 'dhi': diffuse_radiation[i],
                   'temp_air': temperature[i], 'wind_speed': windspeed[i]}
            writer.writerow(row)

def get_datasheet_for_price_past():
    latitude , longitude = get_data_tb()
    latitude = float(latitude)
    longitude = float(longitude)
    Start_date = "2023-04-01"
    end_datae = "2023-04-10"
    url = f'https://archive-api.open-meteo.com/v1/archive?latitude={longitude}&longitude={latitude}&start_date={Start_date}&end_date={end_datae}&hourly=temperature_2m,shortwave_radiation,diffuse_radiation,direct_normal_irradiance,windspeed_10m&timezone=Asia/Tokyo&limit'
    response = requests.get(url)

    # Parse the JSON response to a list of dictionaries
    dataa = response.json()
    print(dataa)
    time = dataa['hourly']['time']
    temperature = dataa['hourly']['temperature_2m']
    windspeed = dataa['hourly']['windspeed_10m']
    shortwave_radiation = dataa['hourly']['shortwave_radiation']
    diffuse_radiation = dataa['hourly']['diffuse_radiation']
    direct_normal_irradiance = dataa['hourly']['direct_normal_irradiance']
    print(type(time))

    # Open a new file to write the CSV data
    with open('data_prices_past.csv', 'w', newline='') as csvfile:
        fieldnames = ['ghi', 'dni', 'dhi', 'temp_air', 'wind_speed']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # write the header row
        writer.writeheader()

        # write a row with all of the data
        for i in range(len(time)):
            row = {'ghi': shortwave_radiation[i], 'dni': direct_normal_irradiance[i], 'dhi': diffuse_radiation[i],
                   'temp_air': temperature[i], 'wind_speed': windspeed[i]}
            writer.writerow(row)

def get_pv_output_for_past_days():
    latitude , longitude = get_data_tb()
    latitude = float(latitude)
    longitude = float(longitude)
    Start_date = "2023-04-01 00:00"
    end_datae = "2023-04-10 23:00"
    temperature_model_parameters = TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']
    sandia_modules = pvlib.pvsystem.retrieve_sam('SandiaMod')
    cec_inverters = pvlib.pvsystem.retrieve_sam('cecinverter')
    sandia_module = sandia_modules['Canadian_Solar_CS5P_220M___2009_']
    cec_inverter = cec_inverters['ABB__MICRO_0_25_I_OUTD_US_208__208V_']
    location = Location(latitude=latitude, longitude=longitude)
    system = PVSystem(surface_tilt=20, surface_azimuth=180, module_parameters=sandia_module,inverter_parameters=cec_inverter, temperature_model_parameters=temperature_model_parameters)
    mc = ModelChain(system, location)
    weather = pd.read_csv('data_prices_past.csv')
    start_date = Start_date
    end_date = end_datae
    date_range = pd.date_range(start=start_date, end=end_date, freq='H', tz='Asia/Calcutta')
    dfg = pd.DataFrame(index=date_range)
    df = pd.DataFrame(weather)
    df.index = dfg.index
    mc.run_model(df)
    power_output = mc.results.dc['v_mp'] * mc.results.dc['i_mp'] / 1000
    poweer = power_output.tolist()
    total_output_per_day=sum(poweer) * 24 / len(poweer)
    return total_output_per_day

def get_pv_output_for_future_days():
    latitude , longitude = get_data_tb()
    latitude = float(latitude)
    longitude = float(longitude)
    Start_date = "2023-04-26 00:00"
    end_datae = "2023-05-03 23:00"
    temperature_model_parameters = TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']
    sandia_modules = pvlib.pvsystem.retrieve_sam('SandiaMod')
    cec_inverters = pvlib.pvsystem.retrieve_sam('cecinverter')
    sandia_module = sandia_modules['Canadian_Solar_CS5P_220M___2009_']
    cec_inverter = cec_inverters['ABB__MICRO_0_25_I_OUTD_US_208__208V_']
    location = Location(latitude=latitude, longitude=longitude)
    system = PVSystem(surface_tilt=20, surface_azimuth=180, module_parameters=sandia_module,
                      inverter_parameters=cec_inverter, temperature_model_parameters=temperature_model_parameters)
    mc = ModelChain(system, location)
    weather = pd.read_csv('data_prices_future.csv')
    start_date = Start_date
    end_date = end_datae
    date_range = pd.date_range(start=start_date, end=end_date, freq='H', tz='Asia/Calcutta')
    dfg = pd.DataFrame(index=date_range)
    df = pd.DataFrame(weather)
    df.index = dfg.index
    mc.run_model(df)
    power_output = mc.results.dc['v_mp'] * mc.results.dc['i_mp'] / 1000
    poweer = power_output.tolist()
    total_power_per_day_future=sum(poweer) * 24 / len(poweer)
    return total_power_per_day_future

@app.route('/energy',methods=['GET'])
def get_Normal_enerdy_predict():
    get_datasheet_for_normal_machine_learning()
    latitude , longitude = get_data_tb()
    latitude = float(latitude)
    longitude = float(longitude)
    Start_date = "2023-04-26 00:00"
    end_datae = "2023-05-03 23:00"
    temperature_model_parameters = TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']
    sandia_modules = pvlib.pvsystem.retrieve_sam('SandiaMod')
    cec_inverters = pvlib.pvsystem.retrieve_sam('cecinverter')
    sandia_module = sandia_modules['Canadian_Solar_CS5P_220M___2009_']
    cec_inverter = cec_inverters['ABB__MICRO_0_25_I_OUTD_US_208__208V_']
    location = Location(latitude=latitude, longitude=longitude)
    system = PVSystem(surface_tilt=20, surface_azimuth=180, module_parameters=sandia_module,inverter_parameters=cec_inverter, temperature_model_parameters=temperature_model_parameters)
    mc= ModelChain(system, location)
    weather = pd.read_csv('data.csv')
    start_date = Start_date
    end_date = end_datae
    date_range = pd.date_range(start=start_date, end=end_date, freq='H', tz='Asia/Calcutta')
    dfg = pd.DataFrame(index=date_range)
    df = pd.DataFrame(weather)
    df.index = dfg.index
    mc.run_model(df)
    power_output = mc.results.dc['v_mp'] * mc.results.dc['i_mp'] / 1000
    poweer = power_output.tolist()
    return poweer

wind_energy_output_find.run_example()

@app.route('/priceprediction',methods=['GET'])
def price_prediction():
    get_datasheet_for_price_future()
    get_datasheet_for_price_past()
    prev=get_pv_output_for_past_days()
    fut=get_pv_output_for_future_days()
    diff=abs(prev-fut)
    percentage = ((fut - prev) / prev) * 100
    final_price=0
    if prev>fut:
        final_price=3.5-(diff*3.5)
    else:
        final_price = 3.5+(diff * 3.5)

    return [percentage,final_price]

#graph forecasting weather
@app.route('/temperature',methods=['GET'])
def temperature_forecasting():
    lat,long = get_data_tb()
    print(lat,long)
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&hourly=temperature_2m&timezone=Asia/Tokyo&limit=7"
    response = requests.get(url)
    data = response.json()
    temp_data = data["hourly"]["temperature_2m"]
    temp_hour=data["hourly"]["time"]
    print(temp_hour)
    # plt.plot(temp_hour,temp_data)
    # plt.xlabel('Time (hours)')
    # plt.ylabel('Temperature (°C)')
    # plt.title('7-Day-s Temperature Forecast')
    # plt.show()
    # print(temp_data)
    return temp_data

@app.route('/humidity',methods=['GET'])
def relative_humidity():
    lat,long = get_data_tb()
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&hourly=relativehumidity_2m&timezone=Asia/Tokyo&limit=7"
    response = requests.get(url)
    data = response.json()
    humidity_data_yaxis=data["hourly"]["relativehumidity_2m"]
    humidity_data_xaxix=data["hourly"]["time"]
    # plt.plot(humidity_data_xaxix,humidity_data_yaxis)
    # plt.xlabel('Time (hours)')
    # plt.ylabel('Relative Humidity (%)')
    # plt.title('7-Day Relative-Humidity Forecast')
    # plt.show()
    # print(lat, long)
    return humidity_data_yaxis

@app.route('/dewpoint',methods=['GET'])
def dewpoint_forecasting():
    lat,long = get_data_tb()
    url= f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&hourly=dewpoint_2m&timezone=Asia/Tokyo&limit=7"
    response = requests.get(url)
    data = response.json()
    dew_point_yaxis= data["hourly"]["dewpoint_2m"]
    dew_point_xaxis=data["hourly"]["time"]
    # plt.plot(dew_point_xaxis,dew_point_yaxis)
    # plt.xlabel('Time (hours)')
    # plt.ylabel('dewpoint (°C)')
    # plt.title('7-Day Dewpoint Forecast')
    # plt.show()
    return dew_point_yaxis

@app.route('/precipitation',methods=['GET'])
def precipitation_forecasting():
    lat,long = get_data_tb()
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&hourly=precipitation&timezone=Asia/Tokyo&limit=7"
    response = requests.get(url)
    data = response.json()
    humidity_data_yaxis = data["hourly"]["precipitation"]
    humidity_data_xaxis=data["hourly"]["time"]
    # plt.plot(humidity_data_xaxis,humidity_data_yaxis)
    # plt.xlabel('Time (hours)')
    # plt.ylabel('Precipitation Over a Hour (mm)')
    # plt.title('7-Day Precipitaion Forecast')
    # plt.show()
    return humidity_data_yaxis

@app.route('/rain',methods=['GET'])
def rain_forecasting():
    lat,long = get_data_tb()
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&hourly=rain&timezone=Asia/Tokyo&limit=7"
    response = requests.get(url)
    data = response.json()
    rain_data_yaxis = data["hourly"]["rain"]
    rain_data_xaxis=data["hourly"]["time"]
    # plt.plot(rain_data_xaxis,rain_data_yaxis)
    # plt.xlabel('Time (hours)')
    # plt.ylabel('Rain (mm)')
    # plt.title('7-Day Rain Forecast')
    # plt.show()
    return rain_data_yaxis

@app.route('/cloudcover',methods=['GET'])
def cloudcover_forecasting():
    lat,long = get_data_tb()
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&hourly=cloudcover&timezone=Asia/Tokyo&limit=7"
    response = requests.get(url)
    data = response.json()
    cloud_cover_yaxis = data["hourly"]["cloudcover"]
    cloud_cover_xaxis=data["hourly"]["time"]
    # plt.plot(cloud_cover_xaxis,cloud_cover_yaxis)
    # plt.xlabel('Time (hours)')
    # plt.ylabel('CLoud Cover (%)')
    # plt.title('7-Day CloudCover Forecast')
    # plt.show()
    return cloud_cover_yaxis

@app.route('/windspeed',methods=['GET'])
def windspeed_forecasting():
    lat,long = get_data_tb()
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&hourly=windspeed_10m&timezone=Asia/Tokyo&limit=7"
    response = requests.get(url)
    data = response.json()
    wind_speed_xaxis = data["hourly"]["windspeed_10m"]
    wind_speed_yaxis=data["hourly"]["time"]
    print(wind_speed_xaxis)
    # plt.plot(wind_speed_xaxis,wind_speed_yaxis)
    # plt.xlabel('Time (hours)') 
    # plt.ylabel('Windspeed (km/h)')
    # plt.title('7-Day WindSpeed Forecast')
    # plt.show()
    # print(lat, long, wind_speed_xaxis)
    return wind_speed_xaxis

@app.route('/irradiance',methods=['GET'])
def irradiance_forecasting():
    lat,long = get_data_tb()
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&hourly=direct_normal_irradiance&timezone=Asia/Tokyo&limit=7"
    response = requests.get(url)
    data = response.json()
    irradnce_yaxis = data["hourly"]["direct_normal_irradiance"]
    irradnce_xaxis=data["hourly"]["time"]
    # plt.plot(irradnce_xaxis,irradnce_yaxis)
    # plt.xlabel('Time (hours)')
    # plt.ylabel('Irradiance (W/m^2)')
    # plt.title('7-Day Irradiance Forecast')
    # plt.show()
    return irradnce_yaxis


def get_datasheet_for_wind():
    latitude , longitude = get_data_tb()
    latitude = float(latitude)
    longitude = float(longitude)    
    Start_date = "2023-04-26" 
    end_datae = "2023-05-03" 
    url = f"https://api.open-meteo.com/v1/forecast?start_date={Start_date}&end_date={end_datae}&latitude={latitude}&longitude={longitude}&hourly=temperature_2m,surface_pressure,windspeed_10m,windspeed_80m,temperature_80m"
    response = requests.get(url)
    dataa = response.json()
    print(dataa)
    time = dataa['hourly']['time']
    pressure = dataa['hourly']['surface_pressure']
    temperature = dataa['hourly']['temperature_2m']
    wind_speed = dataa['hourly']['windspeed_10m']
    temperature_1 = dataa['hourly']['temperature_80m']
    wind_speed_1 = dataa['hourly']['windspeed_80m']
    print(type(time))
    with open('weather_1.csv', 'w', newline='') as csvfile:
        fieldnames = ['variable_name','pressure', 'temperature', 'wind_speed', 'roughness_length', 'temperature_1','wind_speed_1']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # write the header row
        writer.writeheader()
        roww={'variable_name':'height','pressure':0,'temperature':2, 'wind_speed':10, 'roughness_length':0, 'temperature_1':10,'wind_speed_1':80}
        # write a row with all of the data
        writer.writerow(roww)
        for i in range(len(time)):
            row = {'variable_name': time[i], 'pressure': pressure[i]*1000, 'temperature': temperature[i]*10,
                   'wind_speed': wind_speed[i], 'roughness_length':0.15,'temperature_1':temperature_1[i],'wind_speed_1':wind_speed_1[i]}
            writer.writerow(row)

@app.route('/windenergy',methods=['GET'])
def temp():
    get_datasheet_for_wind()
    return wind_energy_output_find.run_example()



if __name__ == '__main__':

    app.run(debug=True)