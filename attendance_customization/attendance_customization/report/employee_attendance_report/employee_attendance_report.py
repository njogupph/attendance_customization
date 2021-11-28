# Copyright (c) 2013, Chris and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import functools
import math
import re
import datetime
from datetime import datetime

import erpnext
import frappe
from erpnext.accounts.report.utils import get_currency, convert_to_presentation_currency
from erpnext.accounts.utils import get_fiscal_year
from frappe import _
from frappe.utils import (flt, getdate, get_first_day, add_months, add_days, formatdate, cstr, cint)
from past.builtins import cmp
from frappe.utils import (
    add_to_date,
    flt,
    get_datetime,
    get_link_to_form,
    get_time,
    time_diff,
    time_diff_in_hours,
    time_diff_in_seconds,
)


def execute(filters=None):
    return get_columns(), get_data(filters)


def get_data(filters):
    attns = []
    data = []
    attns = get_details()

    for attn in attns:
        attdate = getdate(attn.attendance_date)
        in_attendance_time = ""
        intime = get_time_in(attn.employee, attn.name)
        if intime != "":
            in_attendance_time = str(intime.strftime("%H:%M:%S"))

        else:
            in_attendance_time = ""

        out_attendance_time = ""
        outtime = get_time_out(attn.employee, attn.name)
        if outtime != "":
            out_attendance_time = str(outtime.strftime("%H:%M:%S"))
        else:
            out_attendance_time = ""
        whours = 0
        if intime != "" and outtime != "":
            whours = time_diff_in_hours(outtime, intime)

        overtime = 0
        # frappe.throw("{0}".format(attn.standard_working_hours))
        if attn.standard_working_hours == "None" or attn.standard_working_hours == "" or attn.standard_working_hours == None:
            # attn.standard_working_hours = 0
            overtime = whours - 0
        else:
            overtime = whours - attn.standard_working_hours

        row = frappe._dict(
            {
                "name": attn.name,
                "employee": attn.employee,
                "employee_name": attn.employee_name,
                "status": attn.status,
                "attendance_date": attn.attendance_date,
                "shift": attn.shift,
                "department": attn.department,
                "late_entry": attn.late_entry,
                "early_exit": attn.early_exit,
                "designation": attn.designation,
                "gender": attn.gender,
                "in_time": in_attendance_time,
                "out_time": out_attendance_time,
                "working_hours": whours,
                "weekdays": attn.weekdays,
                "overtime": overtime,
                "standard_working_hours": attn.standard_working_hours,
            })
        data.append(row)

    # data = [{
    #     "name": "HR-ATT-2021-00003-1",
    #     "employee": "NOS-00029",
    #     "employee_name": "Chris Njogu 6",
    #     "status": "Present",
    #     "designation": "Manager",
    #     "gender": "Male",
    #     "department": "HR",
    #     "shift": "Morning",
    #     "attendance_date": "15/11/2021",
    #     "in_time": "8:00",
    #     "out_time": "18:00",
    #     "working_hours": 10,
    #     "weekdays": "Monday",
    #     "overtime": 1,
    #     "standard_working_hours": 9,
    #     "late_entry": 0,
    #     "early_exit": 1,
    #     "gender": "Male"
    #
    # }]

    return data


def get_columns():
    columns = [
        {
            'label': _('ID'),
            'fieldname': 'name',
            'fieldtype': 'Link',
            'options': 'Attendance',
            'width': 150
        },
        {
            'label': _('Employee'),
            'fieldname': 'employee',
            'fieldtype': 'Link',
            'options': 'Employee',
            'width': 150
        },
        {
            'label': _('Employee Name'),
            'fieldname': 'employee_name',
            'fieldtype': 'Data',
            'width': 200
        },
        {
            'label': _('Status'),
            'fieldname': 'status',
            'fieldtype': 'Data',
            'width': 100
        },
        {
            'label': _('Designation'),
            'fieldname': 'designation',
            'fieldtype': 'Data',
            'width': 100
        },
        {
            'label': _('Gender'),
            'fieldname': 'gender',
            'fieldtype': 'Data',
            'width': 100
        },
        {
            'label': _('Department'),
            'fieldname': 'department',
            'fieldtype': 'Data',
            'width': 100
        },
        {
            'label': _('Shift'),
            'fieldname': 'shift',
            'fieldtype': 'Data',
            'width': 100
        },
        {
            'label': _('Attendance Date'),
            'fieldname': 'attendance_date',
            'fieldtype': 'Date',
            'width': 100
        },
        {
            'label': _('In Time'),
            'fieldname': 'in_time',
            'fieldtype': 'Data',
            'width': 100
        },
        {
            'label': _('Out Time'),
            'fieldname': 'out_time',
            'fieldtype': 'Data',
            'width': 100
        },
        {
            'label': _('Working Hours'),
            'fieldname': 'working_hours',
            'fieldtype': 'Int',
            'width': 100
        },
        {
            'label': _('Weekdays'),
            'fieldname': 'weekdays',
            'fieldtype': 'Data',
            'width': 100
        },
        {
            'label': _('Overtime'),
            'fieldname': 'overtime',
            'fieldtype': 'Int',
            'width': 100
        },
        {
            'label': _('Standard Working Hours'),
            'fieldname': 'standard_working_hours',
            'fieldtype': 'Int',
            'width': 100
        },
        {
            'label': _('Late Entry'),
            'fieldname': 'late_entry',
            'fieldtype': 'Check',
            'width': 100
        },
        {
            'label': _('Early Exit'),
            'fieldname': 'early_exit',
            'fieldtype': 'Check',
            'width': 100
        }
    ]

    return columns


def get_details():
    attendance = frappe.db.sql("""
                                select name,employee,employee_name,status,attendance_date,
                                     shift,department,late_entry,early_exit,designation,gender,weekdays,standard_working_hours
                                    from `tabAttendance`
                                         where docstatus =1
                                order by name desc
                                """, as_dict=True)
    return attendance


def get_time_in(employee, attendance):
    in_time = frappe.db.sql("""
                             select time
                                from `tabEmployee Checkin`
                                    where
                                        employee=%s
                                        AND log_type = "IN"
                                        and attendance = %s
                            order by time
                            limit 1
                            """, (employee, attendance), as_dict=True)
    if in_time:
        return in_time[0].time
    else:
        return ""


def get_time_out(employee, attendance):
    out_time = frappe.db.sql("""
                             select time
                                from `tabEmployee Checkin`
                                    where
                                        employee=%s
                                        AND log_type = "OUT"
                                        and attendance = %s
                            order by time desc
                            limit 1
                            """, (employee, attendance), as_dict=True)
    if out_time:
        return out_time[0].time
    else:
        return ""
