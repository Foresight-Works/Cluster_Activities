from datetime import datetime

date_string1, format1 = "21 June, 2018", "%d %B, %Y"
date_string2, format2 = "Tue Feb 02 08:00:00 IST 2016", "%a %b %d %H:%M:%S %Z %Y"
print("date_string =", date_string2)
date_object = datetime.strptime(date_string2, format2)
print("date_object =", date_object)
print("type of date_object =", type(date_object))

