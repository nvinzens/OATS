#!/usr/bin/env python
from oats import oatsdbhelpers
import sys

def main():
    while 1:
        try:
            selection = raw_input('\nSelect 1 to create a new Case, 2 to update an existing Case, 3 to take a Case, '
                                  '4 to close a Case, '
                                  '\n 5 to show all Cases of the last Day, 6 to show the amount of open Cases, '
                                  '7 to show all Case IDs of currently open Cases'
                                  'and e to end\n')

            if selection == '1':
                new_case()
            elif selection == '2':
                update_case()
            elif selection == '3':
                take_case()
            elif selection == '4':
                close_case()
            elif selection == '5':
                cases_of_last_day()
            elif selection == '6':
                amount_open_cases()
            elif selection == '7':
                case_id_of_open()
            elif selection == 'E':
                sys.exit()
            elif selection == 'e':
                sys.exit()
            else:
                print('\nINVALID SELECTION\n')
        except KeyboardInterrupt:
            sys.exit()


def new_case():
    try:
        oatsdbhelpers.create_case(error, host, solution=None, description=None, status=Status.NEW.value, test=False)
    except Exception, e:
        print(str(e))


def update_case():
    try:
        oatsdbhelpers.update_case(case_id, solution, status=None, test=False)
    except Exception, e:
        print(str(e))


def take_case():
    try:
        oatsdbhelpers.take_case(case_id, technician, test=False)
    except Exception, e:
        print(str(e))


def close_case():
    try:
        oatsdbhelpers.close_case(case_id, test=False)
    except Exception, e:
        print(str(e))


def cases_of_last_day():
    try:
        oatsdbhelpers.show_cases_of_last_day()
    except Exception, e:
        print(str(e))


def amount_open_cases():
    try:
        print oatsdbhelpers.numb_open_cases()
    except Exception, e:
        print(str(e))


def case_id_of_open():
    try:
        oatsdbhelpers.show_open_cases_nr()
    except Exception, e:
        print(str(e))


main()