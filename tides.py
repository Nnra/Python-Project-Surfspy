
def tideScraper(loc, state, lat, long, date=None, days='2'):
    import urllib
    from urllib.request import urlopen, Request
    from bs4 import BeautifulSoup
    import numpy as np
    import pandas as pd
    
    if date is None:
        from datetime import date
        today = date.today()
        date = today.strftime('%d-%m-%y')
    
    df_tidesID = pd.read_csv('location.csv')
    df_tidesID.loc[df_tidesID['location_name']==loc]['location_id'].item()
    # Parameters Use for Scraping Tides Data
    query_id = df_tidesID.loc[df_tidesID['location_name']==loc]['location_id'].item()
    queryDate  = "'"+date+"'"
    # days = '2'
    spot_url = 'http://www.bom.gov.au/australia/tides/print.php?aac={query_id}&type=tide&date={queryDate}&days={days}'.format(query_id=query_id, queryDate=queryDate, days=days)
    
    df_all = pd.DataFrame(columns=['Date','Type','Time','Height','Location',
                                                  'Long','Lat','State','Local_time'])
    df_all.to_csv('./tides_utc_{loc}_{date}.csv'.format(loc=loc,date=date), mode='w', header=True, index=False)

    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = Request(spot_url, headers=hdr)
    page = urlopen(req)
    soup_tides = BeautifulSoup(page, "lxml")

    soup_tides.find_all("td", class_="localtime")
    local_time1 = [x.get('data-time-utc') for x in soup_tides.find_all("td", class_="localtime")]
    # print(len(local_time1))
    # #### Dates and Tides Info
    dates = [h3.text.replace('\n', '') for h3 in soup_tides.find_all('h3')]


    tables = soup_tides.find_all('table')
    ths = soup_tides.find_all('th')
    rows = list()
    for tr in tables:
        rows.append([tr.text.replace('\n', ',').replace('\xa0', '') ] )

    data = np.column_stack((dates, rows))

    df = pd.DataFrame(data=data, columns={'Date':dates,'2':rows})
    
    df_2 = df['2'].str.split(',', expand = True)
    df_2 = df_2.drop(columns=[0,1,2,5,6,8,9,12,13,15,16,19,20,22,23,26,27,29,30,31])

    df_3 = pd.concat([df['Date'] ,df_2], axis=1)

    df_3 = df_3.rename(columns={3: 'High_1', 4: 'High_Time_1', 7: 'High_Height_1',
                        10: 'Low_1', 11: 'Low_Time_1', 14: 'Low_Height_1',
                        17: 'High_2', 18: 'High_Time_2', 21: 'High_Height_2',
                        24: 'Low_2', 25: 'Low_Time_2', 28: 'Low_Height_2',})

    df_3 = df_3.assign(Location=loc, 
                       Long=long,
                       Lat = lat,
                       State = state)
    # df_3.to_csv(r'./raw_tides.csv', index = False, mode='a', header=True)

    # #### Reshape and add UTC local time
    # df = pd.read_csv('./temp_raw_bs4_tides.csv')
    df = df_3

    df.stack(dropna=True)

    df1 = df[['Date','High_1','High_Time_1','High_Height_1','Location','Long','Lat','State']]

    df2 = df[['Date','Low_1','Low_Time_1','Low_Height_1','Location','Long','Lat','State']]


    df3 = df[['Date','High_2','High_Time_2','High_Height_2','Location','Long','Lat','State']]


    df4 = df[['Date','Low_2','Low_Time_2','Low_Height_2','Location','Long','Lat','State']]


    df1 = df1.rename(columns = {'Date':'Date','High_1':'Type','High_Time_1':'Time','High_Height_1':'Height', 
                          4:'Location',5:'Long',6:'Lat',7:'State'})

    df2 = df2.rename(columns = {'Date':'Date','Low_1':'Type','Low_Time_1':'Time','Low_Height_1':'Height', 
                          4:'Location',5:'Long',6:'Lat',7:'State'})

    df3 = df3.rename(columns = {'Date':'Date','High_2':'Type','High_Time_2':'Time',
                                'High_Height_2':'Height', 
                          4:'Location',5:'Long',6:'Lat',7:'State'})

    df4 = df4.rename(columns = {'Date':'Date','Low_2':'Type','Low_Time_2':'Time','Low_Height_2':'Height', 
                          4:'Location',5:'Long',6:'Lat',7:'State'})

    df_time = pd.DataFrame(local_time1,
                       columns=['local_time'])

    df_time = pd.DataFrame(np.reshape(df_time.values,(int(days),4)), 
                        columns=['time1','time2','time3','time4'])

    df_time1 = pd.DataFrame(df_time['time1'].values, columns=['time'])
    df_time2 = pd.DataFrame(df_time['time2'].values, columns=['time'])
    df_time3 = pd.DataFrame(df_time['time3'].values, columns=['time'])
    df_time4 = pd.DataFrame(df_time['time4'].values, columns=['time'])
    #,df_time['time2'],df_time['time3'],df_time['time4']
    df_all_time = pd.concat([df_time1,df_time2,df_time3,df_time4])
    clean_df = pd.concat([df1,df2,df3,df4])
    clean_df['Local_time'] = df_all_time
    clean_df.dropna(inplace=True)
    clean_df.to_csv(r'./tides_utc_{loc}_{date}.csv'.format(loc=loc, date=date), index = False, mode='a', header=False)   




    # df_all = pd.read_csv("./clean_tides_utc.csv", header=None)
    # df_all.to_csv("./clean_tides_utc.csv", header=['Date','Type','Time','Height','Location',
    #                                               'Long','Lat','State','Local_time'], index=False)

    
def tideCalculator(loc, date=None):
    import numpy as np
    import pandas as pd
    
    if date is None:
        from datetime import date
        today = date.today()
        date = today.strftime('%d-%m-%y')

    df = pd.read_csv('./tides_utc_{loc}_{date}.csv'.format(loc=loc, date=date))
    sorted_df = df.sort_values(by=['Location','Local_time'], ascending=True)
    sorted_df['Local_time_end'] = np.nan
    # Set the value for end time column
    sorted_df['Local_time_end'][:-1] = sorted_df['Local_time'][1:]
    # sorted_df['Height_end'][:-1] = sorted_df['Height'][1:]
    # reset dataframe index
    sorted_df = sorted_df.reset_index(drop=True)
    sorted_df['Local_time_end'].iloc[-1] = sorted_df['Local_time'].iloc[-1][:10] + 'T24:00:00+11:00'
    # Start time End time in hour
    sorted_df['Start_Time'] =  pd.Series(sorted_df['Local_time']).str[11:13]
    sorted_df['End_Time'] =  pd.Series(sorted_df['Local_time_end']).str[11:13]
    #### Edit End time if-else endtime 00 to 24
    sorted_df['End_Time'].replace(to_replace = '00', value = '24', inplace=True)

    # Change to numeric in order to calculate time range
    sorted_df['Start_Time'] = pd.to_numeric(pd.Series(sorted_df['Start_Time']), downcast='integer')
    sorted_df['End_Time'] = pd.to_numeric(pd.Series(sorted_df['End_Time']), downcast='integer')


    # Check if end time > start time
    for i in range(len(sorted_df)):
        start_time = pd.to_numeric(pd.Series(sorted_df['Start_Time']), downcast='integer')
        end_time = pd.to_numeric(pd.Series(sorted_df['End_Time']), downcast='integer')
        if (end_time[i]-start_time[i] < 0):
            sorted_df['End_Time'][i] += 24

    # Calculate range to create new time list with every hours
    sorted_df['new_time'] = [list(range(x,y)) for x , y in zip(sorted_df.Start_Time,sorted_df.End_Time)]

    ## Create New Height End column for tides
    sorted_df['Height_end'] = np.nan
    sorted_df['Height_end'][:-1] = sorted_df['Height'][1:]

    # if there is no other tides data, set last row as 0.5
    sorted_df['Height_end'].iloc[-1] = '0.50 m'
    sorted_df['Start_Height'] = pd.Series(sorted_df['Height']).str[:-1]
    sorted_df['End_Height'] = pd.Series(sorted_df['Height_end']).str[:-1]

    # Covert to numeric in order to calculate tides difference
    sorted_df['Start_Height'] = pd.to_numeric(pd.Series(sorted_df['Start_Height']), downcast='integer')
    sorted_df['End_Height'] = pd.to_numeric(pd.Series(sorted_df['End_Height']), downcast='integer')

    ### Tides Formula
    height_list = []
    for i in range(len(sorted_df)):
        a = []
        for j in range(len(sorted_df['new_time'][i])):
            a.append(sorted_df['Start_Height'][i] + j*(sorted_df['End_Height'][i]-sorted_df['Start_Height'][i])/((len(sorted_df['new_time'][i])-1)))
        height_list.append(a)               

    sorted_df['Height_Change'] = height_list

    # explode Time list
    df_1 = sorted_df
    df_1 = df_1.drop(columns=['Height_Change'])
    df_time = df_1.explode('new_time')

    # explode Height list
    df_1 = sorted_df
    df_1 = df_1.drop(columns=['new_time'])
    df_height = df_1.explode('Height_Change')
    # Combine time and height after exploded columns
    df_time['Height_Change'] = df_height['Height_Change']

    # Convert to float type in order to plot data
    df_time['Height_Change'] = pd.to_numeric(pd.Series(df_time['Height_Change']), downcast='float')
    
    ####### Plotting Tides Data
    # libraries
    import numpy as np
    import seaborn as sns
    import matplotlib.pyplot as plt
    sns.set_style("whitegrid")

    # Color palette
    blue, = sns.color_palette("muted", 1)

    # Create data
    X = np.arange(0,23)
    Y = df_time['Height_Change'][:23]

    x = X
    y = Y

    # Plot tides data
    fig, ax = plt.subplots()
    ax.plot(x, y, color=blue, lw=3)
    ax.fill_between(x, 0, y, alpha=.3)
    ax.set_title("Tides Height Change at {loc} on {date}".format(loc=loc, date=date))
    ax.set_xlabel('24 Hours Tides Change'
                    #'Tides hour start from '
                  #+ timelist[0][:10] + ' ' + timelist[0][11:16]
               #df['time'].values[0][:10] + ' ' + df['time'].values[0][11:16]
              )
    ax.set_ylabel('Tides Height (m)')
    ax.set(xlim=(0, len(x) - 1), ylim=(0, None), xticks=x)
    plt.savefig('tides_{loc}_{date}.png'.format(loc=loc, date=date), dpi=100)
    fig.show()
    