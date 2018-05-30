import xlrd
from oatsinflux import oatsinflux
import datetime


def __get_dates(datecol):
    dates = []
    for cell in datecol:
        if isinstance(cell.value, float):
            date = xlrd.xldate_as_datetime(cell.value, wb.datemode)
            dates.append(date)
    return dates


def __get_times(timecol):
    times = []
    for cell in timecol:
        if isinstance(cell.value, float):
          times.append(cell.value)
    return times

def __get_avg_dates(start_date, end_date):
    start_date = start_date - datetime.timedelta(days=1)
    end_date = end_date + datetime.timedelta(days=1)
    delta = end_date - start_date
    dates = []
    for index in range(delta.days):
        dates.append(start_date + datetime.timedelta(days=index))
    return dates


def __get_avg_times(dates, times):
    avg_times = []
    avg = sum(times) / float(len(times))
    for index in range(len(dates)):
        avg_times.append(avg)
    return avg_times

def __get_avg_categories(dates):
    categories = []
    for index in range(len(dates)):
        categories.append(-1)
    return categories



def __influxwrite(name, dates, times, categories):
    client = oatsinflux.connect_influx_client(dbname='timedb')
    tablename = 'oats_proj_mgmt'
    for index in range(len(dates)):
        print (dates[index], times[index], categories[index])
        point = [
            {
                "measurement": tablename,
                "tags": {
                    "name": name,
                    "category": categories[index]
                },
                "time": dates[index] + datetime.timedelta(seconds=index),
                "fields": {
                    "hours": times[index]
                }
            }
        ]
        try:
            client.write_points(point)
        except Exception as e:
            print(str(e))

    client.close()



def __get_hours(times):
    hours = 0
    for time in times:
        hours += time
    return hours



def __get_categories(categorycol):
    categories = []
    for cell in categorycol:
        if cell.value == 'I':
            categories.append(0)
        if cell.value == 'A':
            categories.append(1)
        if cell.value == 'T':
            categories.append(2)
        if cell.value == 'D':
            categories.append(3)
        if cell.value == 'P':
            categories.append(4)
    return categories


wb = xlrd.open_workbook('Zeiterfassung.xlsx')
r_sheet = wb.sheet_by_index(0)
n_sheet = wb.sheet_by_index(1)

r_dates = __get_dates(r_sheet.col(0))
r_times = __get_times(r_sheet.col(1))
r_hours = __get_hours(r_times)
print ("R hours: " + str(r_hours))
r_categories = __get_categories(r_sheet.col(4))

n_dates = __get_dates(n_sheet.col(0))
n_times = __get_times(n_sheet.col(1))
n_hours = __get_hours(n_times)
print ("N Hours: " + str(n_hours))
n_categories = __get_categories(n_sheet.col(4))

avg_dates = __get_avg_dates(n_dates[0], n_dates[-1])
avg_categories = __get_avg_categories(avg_dates)
n_avg_times = __get_avg_times(avg_dates, n_times)
r_avg_times = __get_avg_times(avg_dates, r_times)



#print (len(n_dates), len(n_times), len(n_categories))
print ("write r_data")
__influxwrite("raphael", r_dates, r_times, r_categories)
print ("r_data done")
print ("write n_data")
__influxwrite("nico", n_dates, n_times, n_categories)
print ("n_data_done")
print("write n_avg data")
__influxwrite("nico_avg", avg_dates, n_avg_times, avg_categories)
print("write r_avg data")
__influxwrite("raphael_avg", avg_dates, r_avg_times, avg_categories)

