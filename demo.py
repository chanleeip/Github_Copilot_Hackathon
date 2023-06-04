import pandas as pd
import pvlib
from pvlib.pvsystem import PVSystem, FixedMount
from pvlib.location import Location
from pvlib.modelchain import ModelChain
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS
import requests
import csv
def get_datasheet_for_normal_machine_learning():
    latitude , longitude = 10,20
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
    latitude , longitude = 10,20
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
    print(poweer)
get_Normal_enerdy_predict()
