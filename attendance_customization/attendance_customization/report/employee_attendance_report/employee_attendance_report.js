// Copyright (c) 2016, Chris and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Employee Attendance Report"] = {
"filters": [
		{
			"fieldname":"employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee"
		},
		{
			"fieldname": "leave_type",
			"label": __("Leave Type"),
			"fieldtype": "Link",
			"options": "Leave Type"
		},

	]
};
