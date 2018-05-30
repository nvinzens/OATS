import xlrd
from influxdb import InfluxDBClient
from influxdb import exceptions


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
r_categories = __get_categories(r_sheet.col(4))

n_dates = __get_dates(n_sheet.col(0))
n_times = __get_times(n_sheet.col(1))
n_categories = __get_categories(n_sheet.col(4))

print (len(r_dates), len(r_times), len(r_categories))
#for index in range(len(r_dates)):
    #print (r_dates[index])


