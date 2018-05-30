import xlrd

def __get_hours_per_task(task_nrs, ms_string):
    hours_per_task = {}

    for nr in task_nrs:
        if isinstance(nr.value, float):
            ms = ms_string + str(int(nr.value))
            hours_per_task[ms] = 0
            for time, task in zip(n_times, n_tasks):
                # print 'MS7: ' + str(int(nr.value)), str(task.value)
                if ms in str(task.value):
                    # print nr, time.value
                    hours_per_task[ms] += time.value
    return hours_per_task


wb = xlrd.open_workbook('Zeiterfassung.xlsx')

n_sheet = wb.sheet_by_index(1)
n_tasks = n_sheet.col(5)
n_times = n_sheet.col(1)

ms7_sheet = wb.sheet_by_index(5)
ms7_task_nrs = ms7_sheet.col(0)

ms7_hours_per_task = __get_hours_per_task(ms7_task_nrs, 'MS7: ')

for key, value in ms7_hours_per_task.items():
    print key, value

