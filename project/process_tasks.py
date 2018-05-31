import xlrd
import collections


def __get_hours_per_task(task_nrs, ms_string, times, tasks):
    hours_per_task = collections.OrderedDict()

    for nr in task_nrs:
        if isinstance(nr.value, float):
            ms = ms_string + str(int(nr.value))
            hours_per_task[ms] = 0
            for time, task in zip(times, tasks):
                # print 'MS7: ' + str(int(nr.value)), str(task.value)
                if ms in str(task.value):
                    # print nr, time.value
                    hours_per_task[ms] += time.value
    return hours_per_task


def __get_elab_hours_per_task(task_nrs, times, tasks):
    hours_per_task = collections.OrderedDict()

    for nr in task_nrs:
        if isinstance(nr.value, float):
            task_number = int(nr.value)
            hours_per_task[task_number] = 0
            for time, task in zip(times, tasks):
                if task.value == task_number:
                    hours_per_task[task_number] += time.value
    return  hours_per_task

wb = xlrd.open_workbook('Zeiterfassung.xlsx')
# TODO: r_sheet etc.
n_sheet = wb.sheet_by_index(1)
n_tasks = n_sheet.col(5)
n_times = n_sheet.col(1)

ms_strings = ['MS9: ', 'MS8: ', 'MS7: ', 'MS6: ', 'MS5: ', 'MS4: ']
n_hours_per_task = collections.OrderedDict()
for index in range(3, 9):
    ms_sheet = wb.sheet_by_index(index)
    ms_task_nrs = ms_sheet.col(0)
    ms_hours_per_task = __get_hours_per_task(ms_task_nrs, ms_strings[index - 3], n_times, n_tasks)
    for key, value in ms_hours_per_task.items():
        n_hours_per_task.update({key: value})

#for key, value in n_hours_per_task.items():
#    print key, value

# Elaboration
elab_sheet = wb.sheet_by_index(2)
elab_task_nrs = elab_sheet.col(0)
n_elab_task_hours = __get_elab_hours_per_task(elab_task_nrs, n_times, n_tasks)
sum = 0
for key, value in n_elab_task_hours.items():
    sum += value
    print key, value









