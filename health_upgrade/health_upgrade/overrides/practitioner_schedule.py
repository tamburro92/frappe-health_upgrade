import frappe
from frappe import _
import json
from datetime import datetime, timedelta

@frappe.whitelist()
def add_slots(docname, values):
	values = json.loads(values)
	doc = frappe.get_doc('Practitioner Schedule',docname)	

	from_date = datetime.strptime(values['from_date'], "%Y-%m-%d")
	to_date = datetime.strptime(values['to_date'], "%Y-%m-%d")
	from_h = {'hour': int(values['from_time'].split(':')[0]), 'minute': int(values['from_time'].split(':')[1])}
	to_h = {'hour': int(values['to_time'].split(':')[0]), 'minute': int(values['to_time'].split(':')[1])}
	duration = values['duration']
	added = False
	cur_date = from_date

	if duration <=0:
		frappe.throw(_("Duration can't be 0 or less"), title=_("Error"))

	while cur_date <= to_date:
		if values.get(cur_date.strftime("%A").lower(), 0) == 1:
			cur_date = datetime(cur_date.year, cur_date.month, cur_date.day, from_h['hour'], from_h['minute'])
			end_date = datetime(cur_date.year, cur_date.month, cur_date.day, to_h['hour'], to_h['minute'])
			while cur_date < end_date:
				before_date = cur_date
				cur_date += timedelta(minutes=duration)
				if cur_date <= end_date:
					added = True
					doc.append('time_slots',
				{'day': before_date.strftime('%A'),
							'hc_slot_date':before_date.strftime('%Y-%m-%d'),
							'from_time':before_date.strftime('%H:%M:%S') ,
							'to_time'   :cur_date.strftime('%H:%M:%S') ,
							'duration': duration,
							'maximum_appointments' : 0})

		cur_date += timedelta(days=1)
	doc.save()

@frappe.whitelist()
def delete_all_slots(docname):
	doc = frappe.get_doc('Practitioner Schedule',docname)
	#doc.time_slots = []
	#doc.save
	for tm in doc.get('time_slots'):
		doc.remove(tm)
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	