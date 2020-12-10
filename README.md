# Table of Contents

## Background

## Install

## Usage

## Maintainers

## Contributing

## License



### Background

**surfspy.py** tool is for creating live interactive report for Australian surf spots with greater accuracy than the current centralized surf report systems for the users. With this tool you can acquire the report of weather temperature, swell height, swell direction, swell period, wind speed, wind direction, wind  rose data from Storm Glass API, and tides height data from Australia  Bureau of Meteorology (BOM) website through web scrapping.

### Install

```python
pip install -- arrow
```

```python
pip install --user pandas==1.0.3
```

```python
pip install windrose
```

```python
pip install plotly
```

> arrow, pandas, windrose, plotly libraries should be installed for this project.
>
> **Arrow** is a Python library that offers a sensible and human-friendly approach to creating, manipulating, formatting and converting dates, times and timestamps. It implements and updates the datetime type, plugging gaps in functionality and providing an intelligent module API that supports many common creation scenarios. 
>
> **pandas** is a Python package that provides fast, flexible, and expressive data structures designed to make working with structured (tabular, multidimensional, potentially heterogeneous) and time series data both easy and intuitive. 
>
> **windrose**: A [wind rose](https://en.wikipedia.org/wiki/Wind_rose) is a graphic tool used by meteorologists to give a succinct view of how wind speed and direction are typically distributed at a particular location. It can also be used to describe air quality pollution sources. The wind rose tool uses Matplotlib as a backend. Data can be passed to the package using Numpy arrays or a Pandas DataFrame.
>
> **plotly**: Python plotting library for collaborative, interactive, publication-quality graphs.



### Usage

*The ultimate goal of the project is to democratise surf reporting by creating a platform that compiles, averages and publishes data supplied from users to provide a live surf report with greater accuracy than the current centralized surf report systems.*

As for the current accomplishment, the project has accomplished:

> 1. It can be used to users to submit their subjective ratings toward a surfing spot in our sample location. Theses ratings will be submitted as reports in the project database. Ratings will be averaged based on those reports for a specific surfing spot.
>
>    ```python
>    #user name
>    userName = input("Please enter your username: ")
>    
>    # user select a location
>    loc = selectFromDict(res, 'Surf Location')
>    
>    # user selects a surf score
>    score = selectFromDict(score, 'Surf Score')
>    
>    from datetime import datetime
>    #capture data and time
>    now = datetime.now()
>    
>    print(userName + ' your surf report on: ' + now.strftime("%Y-%m-%d %H:%M:%S") + ' at ' + loc + ' you gave a score of: ' + score)
>    # above code block is an user prompt interface
>    ```

> 2.  Based on the surfing spot entered by users, location will be matched. To achieve this, a prepared files named [location.csv](https://github.com/Nnra/Python_HW/blob/Nnra-Surf-Python-Project/location.csv) was created. A peek for this file:
>
>    | location_id | location_name   | state | url_name            | Lat      | Long     |
>    | ----------- | --------------- | ----- | ------------------- | -------- | -------- |
>    | NSW_TP009   | Ballina         | NSW   | nsw-ballina         | -32.8428 | 151.3803 |
>    | NSW_TP010   | Bermagui        | NSW   | nsw-bermagui        | -32.165  | 150.9011 |
>    | NSW_TP001   | Botany Bay      | NSW   | nsw-botany-bay      | -24.2125 | 151.9032 |
>    | NSW_TP037   | Broughton I.    | NSW   | nsw-broughton-i     | -20.2744 | 148.715  |
>    | NSW_TP016   | Brunswick Heads | NSW   | nsw-brunswick-heads | -36.0806 | 146.9158 |

> 3. [Stormglass API](https://stormglass.io/) is applied to retrieve weather, swell and seaLevel data based on Lat and Long values obtained.
>
>    Key being used for the API: '0fe486ac-3acf-11eb-93d6-0242ac130002-0fe4872e-3acf-11eb-93d6-0242ac130002'
>
>    Sample code to access weather data through the API:
>
>    ```PYTHON
>    # Weather Data
>    # Get first hour of today
>    start = arrow.now().floor('day')
>    
>    # Get last hour of today
>    end = arrow.now().ceil('day')
>    
>    response = requests.get(
>      'https://api.stormglass.io/v2/weather/point',
>      params={
>        'lat': lat,
>        'lng': long,
>          ######## secondary swell ????
>        'params': ','.join(['airTemperature','swellDirection','swellHeight','swellPeriod','secondarySwellDirection','secondarySwellHeight','secondarySwellPeriod','windDirection','windSpeed']),
>        'start': start.to('UTC').timestamp,  # Convert to UTC timestamp
>        'end': end.to('UTC').timestamp  # Convert to UTC timestamp
>      },
>      headers={
>        'Authorization': '0fe486ac-3acf-11eb-93d6-0242ac130002-0fe4872e-3acf-11eb-93d6-0242ac130002'
>      }
>    )
>    # The method is similar to retrieve swell and sea level data
>    ```

> 4. Tide data as a fundamental information surfers concern on, is accessed from the official website of [Australian Government, Bureau of Meteorology](http://www.bom.gov.au/), which ensures the authority and reliability of the data source. The method to access data is <u>Web Scrapping</u>, by implementing **<u>BeautifulSoup</u>** python module. Critical part of the code to acquire data and building DataFrame consistent with our requirement is demonstrated below:
>
>    ```python
>    df_tidesID = pd.read_csv('location.csv')
>        df_tidesID.loc[df_tidesID['location_name']==loc]['location_id'].item()
>        # Parameters Use for Scraping Tides Data
>        query_id = df_tidesID.loc[df_tidesID['location_name']==loc]['location_id'].item()
>        queryDate  = "'"+date+"'"
>        # days = '2'
>        spot_url = 'http://www.bom.gov.au/australia/tides/print.php?aac={query_id}&type=tide&date={queryDate}&days={days}'.format(query_id=query_id, queryDate=queryDate, days=days)
>        
>        df_all = pd.DataFrame(columns=['Date','Type','Time','Height','Location',
>                                                      'Long','Lat','State','Local_time'])
>                                                      
>     df_all.to_csv('./tides_utc_{loc}_{date}.csv'.format(loc=loc,date=date), mode='w', header=True, index=False)
>    
>        hdr = {'User-Agent': 'Mozilla/5.0'}
>        req = Request(spot_url, headers=hdr)
>        page = urlopen(req)
>        soup_tides = BeautifulSoup(page, "lxml")
>    
>        soup_tides.find_all("td", class_="localtime")
>        local_time1 = [x.get('data-time-utc') for x in soup_tides.find_all("td", class_="localtime")]
>        # print(len(local_time1))
>        # #### Dates and Tides Info
>        dates = [h3.text.replace('\n', '') for h3 in soup_tides.find_all('h3')]
>    
>    
>        tables = soup_tides.find_all('table')
>        ths = soup_tides.find_all('th')
>        rows = list()  
>    ```

> 5. Since the primary principle of our project is user-friendly, clear data visualization must be made. <u>*Scatter Plot*</u>, <u>*Line Graph*</u>, <u>*Bar Graph*</u>, <u>*Horizontal Bar Graph*</u>, <u>*Box Plot*</u>, <u>*Windrose*</u>  and <u>*Interactive Map Plot*</u> has been  utilized to display data neatly. The interactive one is screenshooted since it is animated. 
>
>    ![airtemperature_crowdy_head_10-12-20](E:\95888\project\airtemperature_crowdy_head_10-12-20.png)
>
>    
>
>    ![windspeed_crowdy_head_10-12-20_360](E:\95888\project\windspeed_crowdy_head_10-12-20_360.png)
>
>    
>
>    ![winddirection_crowdy_head_10-12-20](E:\95888\project\winddirection_crowdy_head_10-12-20.png)
>
>    
>
>    ![windrose_crowdy_head_10-12-20](E:\95888\project\windrose_crowdy_head_10-12-20.png)
>
>    
>
>    ![swellperiod_crowdy_head_10-12-20](E:\95888\project\swellperiod_crowdy_head_10-12-20.png)
>
>    
>
>    ![tides_crowdy_head_10-12-20](E:\95888\project\tides_crowdy_head_10-12-20.png)
>
>    
>
>    ![screen_shot_2020-12-10_at_10.20.06_pm](E:\95888\project\screen_shot_2020-12-10_at_10.20.06_pm.png)

> 6. The methodology of choosing sample locations is to download rating data from [Firebase](https://firebase.google.com/?gclid=EAIaIQobChMIs4yahanD7QIV9cEWBR0IHA_pEAAYASAAEgLNT_D_BwE) 



### Maintainers

@Nnra 

@ruoyulia

@mugambiian

@BFleets

### Contributing

Feel free to dive in! Open an issue or submit PRs.

### License

MIT License
Copyright (c) 2020 Ian Mugambi, Nura Wu, Brett Fleetwood, Ruoyu Liang, Vincent Liang

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

> 1. The above copyright notice and this permission notice shall be included in all
>    copies or substantial portions of the Software.
> 2.  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
>    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
>    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
>    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
>    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
>    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
>    SOFTWARE.

