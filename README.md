# Features

- ##### Able to know the Current details by either entering your city name or by entering your location's latitude and longitude.
- ##### This CLI also supports simple queries like 'whether is it going to rain tomorrow' or 'Current temperature of your area ' or 'the current weather status' ..
- ##### This CLI also forecasts weather details like humidity,dedwpoint,temperature etc ..
- ##### We have also included functionalites to predict the solar energy and wind energy output of a particular area by inputting the latitude and longitude ...
- ##### Also included help funcitonality within the CLI to get help.
- ##### Easier to get the required info from the CLI itself.

# Installation
#### run requirements.txt using `pip install -r requirements.txt`

#### Clone this repository and and run the python file using the command

`$ python3 cli.py`

#### To run this CLI without python3 keyword
##### move the file to global path then run this command,
`$ chmod +x cli.py`
#### now run by
`$ cli.py`

# Documentation
- ##### To input the city use the argument `--city`
- ##### To input the longtude use the argument `--longitude`
- ##### To input the latitude use the argument `--latitude`
- ##### To input the metric to use like Celsius or fahrenheit use `--Celsius `or `--Fahrenheit`. Default is `--Celsius`
- ##### To get the forecast use the argument `--weather_forecast`
- ##### To get Current Weather Status use argument `--current_weather_status`
- ##### To check whether it is going to rain tomorrow use argument `--gonna_rain_tomorrow`
- ##### To know the Current Temperature use argument `--current_temp`
- ##### To predict the Solar Energy use the argument `--predict_solar_energy`
- ##### To forecast temperature for the next seven days use argument `--temperature_forecast`
- ##### To forecast relative humidity for the next seven days use argument `--humid_forecast`
- ##### To forecast dewpoint for the next seven days use argument `--dew_forecast`
- ##### To forecast precipitation for the next seven days use argument `--precipitation_forecast`
- ##### To forecast rain for the next seven days use argument `--rain_forecast`
- ##### To forecast cloud_cover for the next seven days use argument `--cloud_cover_forecast`
- ##### To forecast wind_speed for the next seven days use argument `--wind_speed_forecast`
- ##### To forecast irradiance for the next seven days use argument `--irradiance_forecast`
- ##### To predict Wind energy output use the argument `--wind_energy_predict`
- ##### To input the starting date for predictions use the argument `--start_date`(Format:YYYY-MM-DD HH:MM)
- ##### To input the end date for predictions use the argument `--end_date`(Format:YYYY-MM-DD HH:MM)

# General Syntax
- #### For calculating current weather status `--city< > --latitude< > --longitude< > --current_weather_status`
- #### For predicting wind energy `--city< > --latitude< > --longitude< > --start_date< > --end_date< > --wind_energy_predict`
- #### For predicting whether going to rain tomorrow ` --city < > --latitude < > --longitude< >  --gonna_rain_tomorrow`
- #### For weather Forecast ` --city < > --weather_forecast`
- #### For current Temperature ` --city< > --latitude< > --longitude< > --current_temp `
- #### For predicting solar Energy `--city< > --latitude< > --longitude< > --start_date< > --end_date< >  --predict_solar_energy` 
- #### For Temperature Forecast `--city < > --latitude< > --longitude< > --temperature_forecasting`
- #### For humidity Forecast `--city < > --latitude< > --longitude< > --humid_forecast`
- #### For dewpoint Forecast `--city < > --latitude< > --longitude< > --dew_forecast`
- #### For precipitation Forecast `--city < > --latitude< > --longitude< > --precipitation_forecast`
- #### For rainfall Forecast `--city < > --latitude< > --longitude< > --rain_forecast`
- #### For cloud cover Forecast `--city < > --latitude< > --longitude< > --cloud_cover_forecast`
- #### For wind speed Forecast `--city < > --latitude< > --longitude< > --wind_speed_forecast`
- #### For irradiance Forecast `--city < > --latitude< > --longitude< > --irradiance_forecast`

# Tech Stack
- #### Python
- #### argparse
- #### PVlib
- #### Windpowerlib
- #### OpenWeatherMap API
- #### OpenMeteo API
- #### PyOWM
-  #### Matlab



##### Offical submission to Github Copilot Hackathon 2023




