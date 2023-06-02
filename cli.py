#!/usr/bin/env python
import argparse
import sys

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
def get_datasheet_for_wind(lat,long):
    with suppress_stdout():
        latitude , longitude = lat , long
        latitude = float(latitude)
        longitude = float(longitude)
        Start_date = "2023-04-26"
        end_datae = "2023-05-03"
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
    print( three_h_forecaster.will_be_rainy_at(tomorrow))
def current_temperature(lat,long):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&hourly=temperature_2m&timezone=Asia/Tokyo&limit=7"
    response = requests.get(url)
    data = response.json()
    temperature = data["hourly"]["temperature_2m"]
    print( temperature[0])
def get_datasheet_for_normal_machine_learning(lat,long):
    latitude , longitude = lat,long
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
    print( poweer)
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
def get_datasheet_for_wind(lat,long):
    latitude , longitude = lat,long
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
def get_weather_data(filename="weather.csv", **kwargs):
    if "datapath" not in kwargs:
        kwargs["datapath"] = os.path.dirname(__file__)

    file = os.path.join(kwargs["datapath"], filename)

    # download example weather data file in case it does not yet exist
    if not os.path.isfile(file):
        logging.debug("Download weather data for example.")
        req = requests.get("https://osf.io/59bqn/download")
        with open(file, "wb") as fout:
            fout.write(req.content)

    # read csv file
    weather_df = pd.read_csv(
        file,
        index_col=0,
        header=[0, 1],
        date_parser=lambda idx: pd.to_datetime(idx, utc=True),
    )

    # change time zone
    weather_df.index = weather_df.index.tz_convert("Asia/Calcutta")

    return weather_df


def initialize_wind_turbines():

    enercon_e126 = {
        "turbine_type": "E-126/4200",  # turbine type as in register
        "hub_height": 135,  # in m
    }
    e126 = WindTurbine(**enercon_e126)

    # ************************************************************************
    # **** Specification of wind turbine with your own data ******************
    # **** NOTE: power values and nominal power have to be in Watt



    return e126


def calculate_power_output(weather, e126):
    r"""
    Calculates power output of wind turbines using the
    :class:`~.modelchain.ModelChain`.

    The :class:`~.modelchain.ModelChain` is a class that provides all necessary
    steps to calculate the power output of a wind turbine. You can either use
    the default methods for the calculation steps, as done for 'my_turbine',
    or choose different methods, as done for the 'e126'. Of course, you can
    also use the default methods while only changing one or two of them, as
    done for 'my_turbine2'.

    Parameters
    ----------
    weather : :pandas:`pandas.DataFrame<frame>`
        Contains weather data time series.
    my_turbine : :class:`~.wind_turbine.WindTurbine`
        WindTurbine object with self provided power curve.
    e126 : :class:`~.wind_turbine.WindTurbine`
        WindTurbine object with power curve from the OpenEnergy Database
        turbine library.
    my_turbine2 : :class:`~.wind_turbine.WindTurbine`
        WindTurbine object with power coefficient curve from example file.

    """

    # ************************************************************************
    # **** ModelChain with non-default specifications ************************
    modelchain_data = {
        "wind_speed_model": "logarithmic",  # 'logarithmic' (default),
        # 'hellman' or
        # 'interpolation_extrapolation'
        "density_model": "ideal_gas",  # 'barometric' (default), 'ideal_gas' or
        # 'interpolation_extrapolation'
        "temperature_model": "linear_gradient",  # 'linear_gradient' (def.) or
        # 'interpolation_extrapolation'
        "power_output_model": "power_coefficient_curve",  # 'power_curve'
        # (default) or 'power_coefficient_curve'
        "density_correction": True,  # False (default) or True
        "obstacle_height": 0,  # default: 0
        "hellman_exp": None,
    }  # None (default) or None
    # initialize ModelChain with own specifications and use run_model method
    # to calculate power output
    mc_e126 = ModelChain(e126).run_model(weather)
    # write power output time series to WindTurbine object
    e126.power_output = mc_e126.power_output

    # ************************************************************************
    # **** ModelChain with default parameter *********************************

    return e126.power_output.to_list()


def plot_or_print( e126):
    r"""
    Plots or prints power output and power (coefficient) curves.

    Parameters
    ----------
    my_turbine : :class:`~.wind_turbine.WindTurbine`
        WindTurbine object with self provided power curve.
    e126 : :class:`~.wind_turbine.WindTurbine`
        WindTurbine object with power curve from the OpenEnergy Database
        turbine library.
    my_turbine2 : :class:`~.wind_turbine.WindTurbine`
        WindTurbine object with power coefficient curve from example file.

    """

    # plot or print turbine power output
    if plt:
        e126.power_output.plot(legend=True)
        plt.xlabel("Time")
        plt.ylabel("Power in W")
        plt.show()
        pass
    # else:
    #     print(e126.power_output)

    # plot or print power curve

def run_example():
    r"""
    Runs the basic example.

    """
    # You can use the logging package to get logging messages from the
    # windpowerlib. Change the logging level if you want more or less messages:
    # logging.DEBUG -> many messages
    # logging.INFO -> few messages
    logging.getLogger().setLevel(logging.DEBUG)

    weather = get_weather_data("weather_1.csv")
    e126 = initialize_wind_turbines()
    calculate_power_output(weather, e126)
    plot_or_print(e126)










































def main():
    parser = argparse.ArgumentParser(description='Weather Forecast')
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('--city', type=str, help='Name of the city')
    parser.add_argument('--latitude', type=float, help='Latitude of the location')
    parser.add_argument('--longitude', type=float, help='Longitude of the location')
    parser.add_argument('--unit', type=str, default='Celsius', choices=['Celsius', 'Fahrenheit'],
                        help='Temperature unit (Celsius or Fahrenheit)')
    args = parser.parse_args()


    if args.city is None and args.latitude is None and args.longitude is None:
        parser.print_help()
        return

    # get_weather_forecast(args.city, args.unit, args.latitude, args.longitude)
    get_datasheet_for_wind(args.latitude, args.longitude)
    # find_current_weather_status(args.latitude, args.longitude)


if __name__ == '__main__':
    main()



