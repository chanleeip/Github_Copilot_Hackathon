#!/usr/bin/env python
import argparse
import sys
import wind_energy_output_find

import requests
import csv
import logging
from windpowerlib import ModelChain, WindTurbine, create_power_curve
import os
from pyowm.owm import OWM
from pyowm.utils import formatting,timestamps
import pandas as pd
import pvlib
from pvlib.pvsystem import PVSystem, FixedMount
from pvlib.location import Location
from pvlib.modelchain import ModelChain
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS
from datetime import date, timedelta
from matplotlib import pyplot as plt

API_KEY = '9297169f55274dfbf3f79162c9678b13'
owm = OWM(API_KEY)
from contextlib import contextmanager
import sys, os

@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout

def get_weather_forecast(city, unit, latitude=None, longitude=None):
    if city:
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&units={unit}&appid={API_KEY}'
    elif latitude is not None and longitude is not None:
        url = f'http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&units={unit}&appid={API_KEY}'
    else:
        print("Please provide either a city name or latitude and longitude.")
        return

    response = requests.get(url)
    data = response.json()

    if data['cod'] == '404':
        print("Could not find weather information for the specified location or city. Please check the input values and try again.")
        return

    city_name = data['name']
    weather_description = data['weather'][0]['description']
    temperature = data['main']['temp']
    humidity = data['main']['humidity']
    wind_speed = data['wind']['speed']

    print(f"Weather forecast for {city_name}:")
    print(f"Description: {weather_description}")
    print(f"Temperature: {temperature} {unit}")
    print(f"Humidity: {humidity}%")
    print(f"Wind Speed: {wind_speed} m/s")
def get_datasheet_for_wind(lat,long,start_date,end_date):
    with suppress_stdout():
        latitude , longitude = lat , long
        latitude = float(latitude)
        longitude = float(longitude)
        Start_date = start_date[:10]
        end_datae = end_date[:10]
        url = f"https://api.open-meteo.com/v1/forecast?start_date={Start_date}&end_date={end_datae}&latitude={latitude}&longitude={longitude}&hourly=temperature_2m,surface_pressure,windspeed_10m,windspeed_80m,temperature_80m"
        response = requests.get(url)
        dataa = response.json()

        time = dataa['hourly']['time']
        pressure = dataa['hourly']['surface_pressure']
        temperature = dataa['hourly']['temperature_2m']
        wind_speed = dataa['hourly']['windspeed_10m']
        temperature_1 = dataa['hourly']['temperature_80m']
        wind_speed_1 = dataa['hourly']['windspeed_80m']

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
    mgr = owm.weather_manager()
    observation = mgr.weather_at_coords(lat, long)
    weather = observation.weather
    print (weather.detailed_status)
def is_it_going_to_rain_tomorrow(lat,long):
    mgr = owm.weather_manager()
    three_h_forecaster = mgr.forecast_at_coords(lat,long,interval='3h')
    tomorrow = timestamps.tomorrow()  # datetime object for tomorrow
    if three_h_forecaster.will_be_rainy_at(tomorrow) == 'false':
        print('Not gonna rain Tomorrow')
    else:
        print('It''s gonna rain Tomorrow')

def current_temperature(lat,long):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&hourly=temperature_2m&timezone=Asia/Tokyo&limit=7"
    response = requests.get(url)
    data = response.json()
    temperature = data["hourly"]["temperature_2m"]
    print(str(temperature[0]) + "°C")
def get_datasheet_for_normal_machine_learning(lat,long,start_date,end_date):
    latitude , longitude = lat,long
    latitude = float(latitude)
    longitude = float(longitude)
    Start_date = start_date[:10]
    end_datae = end_date[:10]
    url = f"https://api.open-meteo.com/v1/forecast?start_date={Start_date}&end_date={end_datae}&latitude={latitude}&longitude={longitude}&hourly=temperature_2m,windspeed_10m,shortwave_radiation,direct_radiation,diffuse_radiation,direct_normal_irradiance,terrestrial_radiation"
    response = requests.get(url)

    # Parse the JSON response to a list of dictionaries
    dataa = response.json()
   # print(dataa)
    # print(dataa)
    time = dataa['hourly']['time']
    temperature = dataa['hourly']['temperature_2m']
    windspeed = dataa['hourly']['windspeed_10m']
    shortwave_radiation = dataa['hourly']['shortwave_radiation']
    diffuse_radiation = dataa['hourly']['diffuse_radiation']
    direct_normal_irradiance = dataa['hourly']['direct_normal_irradiance']
    #print(type(time))

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
def get_Normal_enerdy_predict(lat,long,start_date,end_date):
    latitude , longitude =lat,long
    latitude = float(latitude)
    longitude = float(longitude)
    Start_date = start_date
    end_datae = end_date
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
    #print( poweer)
    plt.plot(date_range, poweer, marker='o', label='Power Output')
    plt.xlabel('Date')
    plt.ylabel('Power Output (kW)')
    plt.title('Solar Power Output')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.legend()
    plt.show()
def temperature_forecasting(lat,long):
    lat,long = lat,long
    print(lat,long)
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&hourly=temperature_2m&timezone=Asia/Tokyo&limit=7"
    response = requests.get(url)
    data = response.json()
    temp_data = data["hourly"]["temperature_2m"]
    temp_hour=data["hourly"]["time"]
    # print(temp_hour)
    plt.plot(temp_hour,temp_data)
    plt.xlabel('Time (hours)')
    plt.ylabel('Temperature (°C)')
    plt.title('7-Day-s Temperature Forecast')
    plt.show()
def relative_humidity(lat,long):
    lat,long = lat,long
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&hourly=relativehumidity_2m&timezone=Asia/Tokyo&limit=7"
    response = requests.get(url)
    data = response.json()
    humidity_data_yaxis=data["hourly"]["relativehumidity_2m"]
    humidity_data_xaxix=data["hourly"]["time"]
    plt.plot(humidity_data_xaxix,humidity_data_yaxis)
    plt.xlabel('Time (hours)')
    plt.ylabel('Relative Humidity (%)')
    plt.title('7-Day Relative-Humidity Forecast')
    plt.show()
    # print(lat, long)lat,lo
def dewpoint_forecasting(lat,long):
    lat,long = lat,long
    url= f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&hourly=dewpoint_2m&timezone=Asia/Tokyo&limit=7"
    response = requests.get(url)
    data = response.json()
    dew_point_yaxis= data["hourly"]["dewpoint_2m"]
    dew_point_xaxis=data["hourly"]["time"]
    plt.plot(dew_point_xaxis,dew_point_yaxis)
    plt.xlabel('Time (hours)')
    plt.ylabel('dewpoint (°C)')
    plt.title('7-Day Dewpoint Forecast')
    plt.show()
def precipitation_forecasting(lat,long):
    lat,long = lat,long
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&hourly=precipitation&timezone=Asia/Tokyo&limit=7"
    response = requests.get(url)
    data = response.json()
    humidity_data_yaxis = data["hourly"]["precipitation"]
    humidity_data_xaxis=data["hourly"]["time"]
    plt.plot(humidity_data_xaxis,humidity_data_yaxis)
    plt.xlabel('Time (hours)')
    plt.ylabel('Precipitation Over a Hour (mm)')
    plt.title('7-Day Precipitaion Forecast')
    plt.show()
def rain_forecasting(lat,long):
    lat,long = lat,long
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&hourly=rain&timezone=Asia/Tokyo&limit=7"
    response = requests.get(url)
    data = response.json()
    rain_data_yaxis = data["hourly"]["rain"]
    rain_data_xaxis=data["hourly"]["time"]
    plt.plot(rain_data_xaxis,rain_data_yaxis)
    plt.xlabel('Time (hours)')
    plt.ylabel('Rain (mm)')
    plt.title('7-Day Rain Forecast')
    plt.show()
def cloudcover_forecasting(lat,long):
    lat,long = lat,long
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&hourly=cloudcover&timezone=Asia/Tokyo&limit=7"
    response = requests.get(url)
    data = response.json()
    cloud_cover_yaxis = data["hourly"]["cloudcover"]
    cloud_cover_xaxis=data["hourly"]["time"]
    plt.plot(cloud_cover_xaxis,cloud_cover_yaxis)
    plt.xlabel('Time (hours)')
    plt.ylabel('CLoud Cover (%)')
    plt.title('7-Day CloudCover Forecast')
    plt.show()
def windspeed_forecasting(lat,long):
    lat,long =lat,long
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&hourly=windspeed_10m&timezone=Asia/Tokyo&limit=7"
    response = requests.get(url)
    data = response.json()
    wind_speed_xaxis = data["hourly"]["windspeed_10m"]
    wind_speed_yaxis=data["hourly"]["time"]
    print(wind_speed_xaxis)
    plt.plot(wind_speed_xaxis,wind_speed_yaxis)
    plt.xlabel('Time (hours)')
    plt.ylabel('Windspeed (km/h)')
    plt.title('7-Day WindSpeed Forecast')
    plt.show()
    # print(lat, long, wind_speed_xaxis)
def irradiance_forecasting(lat,long):
    lat,long = lat,long
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&hourly=direct_normal_irradiance&timezone=Asia/Tokyo&limit=7"
    response = requests.get(url)
    data = response.json()
    irradnce_yaxis = data["hourly"]["direct_normal_irradiance"]
    irradnce_xaxis=data["hourly"]["time"]
    plt.plot(irradnce_xaxis,irradnce_yaxis)
    plt.xlabel('Time (hours)')
    plt.ylabel('Irradiance (W/m^2)')
    plt.title('7-Day Irradiance Forecast')
    plt.show()
    # return irradnce_yaxis
def get_datasheet_for_wind(lat,long,start_date,end_date):
    latitude , longitude = lat,long
    latitude = float(latitude)
    longitude = float(longitude)
    Start_date = start_date[:10]
    end_datae = end_date[:10]
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

c=0


def main():
    global c
    parser = argparse.ArgumentParser(description='Weather Forecast')
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('--city', type=str, help='Name of the city')
    parser.add_argument('--latitude', type=float, help='Latitude of the location')
    parser.add_argument('--longitude', type=float, help='Longitude of the location')
    parser.add_argument('--unit', type=str, default='Celsius', choices=['Celsius', 'Fahrenheit'],
                        help='Temperature unit (Celsius or Fahrenheit)')
    parser.add_argument('--weather_forecast',action='store_true',help='Weather forecast of the city')
    parser.add_argument('--current_weather_status', action='store_true', help='current weather status')
    parser.add_argument('--gonna_rain_tomorrow', action='store_true', help='check whether gonna rain tomorrow')
    parser.add_argument('--current_temp', action='store_true', help='current temperature find')
    parser.add_argument('--predict_solar_energy', action='store_true', help='predict solar energy')
    parser.add_argument('--temperature_forecast', action='store_true', help='temperature forecast')
    parser.add_argument('--humid_forecast', action='store_true', help='humidity forecast')
    parser.add_argument('--dew_forecast', action='store_true', help='dewpoint forecast')
    parser.add_argument('--precipitation_forecast', action='store_true', help='precipitation forecast')
    parser.add_argument('--rain_forecast', action='store_true', help='rain forecast')
    parser.add_argument('--cloud_cover_forecast', action='store_true', help='cloud cover forecast')
    parser.add_argument('--wind_speed_forecast', action='store_true', help='wind speed forecast')
    parser.add_argument('--irradiance_forecast', action='store_true', help='irradiance forecast')
    parser.add_argument('--wind_energy_predict', action='store_true', help='wind energy predict')
    parser.add_argument('--start_date', type=str, help='start date in this format YYYY-MM-DD HH:MM')
    parser.add_argument('--end_date', type=str, help='end date in this format YY-MM-DD HH:MM')
    args = parser.parse_args()


    if args.city is None and args.latitude is None and args.longitude is None:
        parser.print_help()
        return
    if args.current_weather_status:
        find_current_weather_status(args.latitude, args.longitude)
        c=1
    if args.wind_energy_predict:
        get_datasheet_for_wind(args.latitude, args.longitude,args.start_date,args.end_date)
        wind_energy_output_find.run_example(args.start_date,args.end_date)
        c=1
    if args.gonna_rain_tomorrow:
        is_it_going_to_rain_tomorrow(args.latitude, args.longitude)
        c=1
    if args.weather_forecast:
        get_weather_forecast(args.city, args.unit, args.latitude, args.longitude)
        c=1
    if args.current_temp:
        current_temperature(args.latitude, args.longitude)
        c = 1
    if args.predict_solar_energy:
        get_datasheet_for_normal_machine_learning(args.latitude, args.longitude,args.start_date,args.end_date)
        get_Normal_enerdy_predict(args.latitude, args.longitude,args.start_date,args.end_date)
        c = 1
    if args.temperature_forecast:
        temperature_forecasting(args.latitude, args.longitude)
    if args.humid_forecast:
        relative_humidity(args.latitude, args.longitude)
        c = 1
    if args.dew_forecast:
        dewpoint_forecasting(args.latitude, args.longitude)
        c = 1
    if args.precipitation_forecast:
        precipitation_forecasting(args.latitude, args.longitude)
        c = 1
    if args.rain_forecast:
        rain_forecasting(args.latitude, args.longitude)
        c = 1
    if args.cloud_cover_forecast:
        cloudcover_forecasting(args.latitude, args.longitude)
        c = 1
    if args.wind_speed_forecast:
        windspeed_forecasting(args.latitude, args.longitude)
        c = 1
    if args.irradiance_forecast:
        irradiance_forecasting(args.latitude, args.longitude)
        c = 1
    else:
        if c==0:
            print("please enter a valid argument")


if __name__ == '__main__':
    main()



