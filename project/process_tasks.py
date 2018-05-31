import xlrd
import collections


def __get_hours_per_task(task_nrs, ms_string, times, tasks):
    hours_per_task = collections.OrderedDict()

    for nr in task_nrs:
        if isinstance(nr.value, float):
            ms = ms_string + str(int(nr.value))
            hours_per_task[ms] = 0
            for time, task in zip(times, tasks):
                if ms == str(task.value):
                    #print ms, time.value, task.value
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

r_sheet = wb.sheet_by_index(0)
r_tasks = r_sheet.col(5)
r_times = r_sheet.col(1)

ms_strings = ['MS9: ', 'MS8: ', 'MS7: ', 'MS6: ', 'MS5: ', 'MS4: ']
n_hours_per_tasks = collections.OrderedDict()
for index in range(3, 9):
    ms_sheet = wb.sheet_by_index(index)
    ms_task_nrs = ms_sheet.col(0)
    ms_hours_per_task = __get_hours_per_task(ms_task_nrs, ms_strings[index - 3], n_times, n_tasks)
    for key, value in ms_hours_per_task.items():
        n_hours_per_tasks.update({key: value})

r_hours_per_tasks = collections.OrderedDict()
for index in range(3, 9):
    ms_sheet = wb.sheet_by_index(index)
    ms_task_nrs = ms_sheet.col(0)
    ms_hours_per_task = __get_hours_per_task(ms_task_nrs, ms_strings[index - 3], r_times, r_tasks)
    for key, value in ms_hours_per_task.items():
        r_hours_per_tasks.update({key: value})

r_hours = collections.Counter(r_hours_per_tasks)
added_hours = collections.Counter(n_hours_per_tasks)
added_hours.update(r_hours)




print ("--------------------------------------------------")
print ("Milestones: hours per task")
sums = collections.OrderedDict()
for ms in ms_strings:
    sums[ms] = 0
for key, value in sorted(added_hours.items()):
    print (key, value)
    for ms in ms_strings:
        if ms in key:
            sums[ms] += value
print ("Sum: " + str(sum(sums.values())))
print ("--------------------------------------------------")
print ("Hours per Milestone")
sumssum = 0
for key, value in sums.items():
    print (key, value)
    sumssum += value
print ("Sum: " + str(sumssum))

# Elaboration
elab_sheet = wb.sheet_by_index(2)
elab_task_nrs = elab_sheet.col(0)
n_elab_task_hours = collections.Counter(__get_elab_hours_per_task(elab_task_nrs, n_times, n_tasks))
added_elab_hours = collections.Counter(__get_elab_hours_per_task(elab_task_nrs, r_times, r_tasks))
print ("--------------------------------------------------")
print ("Nico elab hours: " + str(sum(n_elab_task_hours.values())))
print ("Raphael elab hours: " + str(sum(added_elab_hours.values())))
added_elab_hours.update(n_elab_task_hours)
print ("--------------------------------------------------")
print ("Elaboration: hours per task")
for key, value in added_elab_hours.items():
    print (key, value)
print ("Sum: " + str(sum(added_elab_hours.values())))
print ("--------------------------------------------------")
print ("Total: " + str(sumssum + sum(added_elab_hours.values())))











