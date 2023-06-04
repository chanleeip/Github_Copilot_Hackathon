
import os
import pandas as pd
import requests
import logging
from windpowerlib import ModelChain, WindTurbine, create_power_curve

try:
    from matplotlib import pyplot as plt
except ImportError:
    plt = None


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


def plot_or_print( e126,start_date,end_date):
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
        date_range = pd.date_range(start=start_date, end=end_date, freq='H', tz='Asia/Calcutta')
        plt.plot(date_range, e126.power_output, marker='o', label='Power Output')
        plt.xlabel('Date')
        plt.ylabel('Power Output (kW)')
        plt.title('Solar Power Output')
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.legend()
        plt.show()
        pass
    else:
        print(e126.power_output)

    # plot or print power curve

def run_example(start_date,end_date):
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
    plot_or_print(e126,start_date,end_date)
    print (calculate_power_output(weather,e126))





