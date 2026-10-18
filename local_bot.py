days = {
    'monday.txt':    "ПОНЕДЕЛЬНИК", 
    'tuesday.txt':   "ВТОРНИК", 
    'wednesday.txt': "СРЕДА", 
    'thursday.txt':  "ЧЕТВЕРГ", 
    'friday.txt':    "ПЯТНИЦА",
    'saturday.txt':  "СУББОТА"
}

dz_filename = "local_homework.txt"

dz_list = {}

for filename in days:
    dz_list[days[filename]] = open("homework/" + filename, encoding="utf-8", mode="r").read().rstrip()


dz_text = ""
for day_name in dz_list:
    raw_dz_for_the_day = dz_list[day_name].split("\n\n")
    dz_for_the_day = []
    
    for segment in raw_dz_for_the_day:
        if segment.rstrip()[-1] != "-":
            dz_for_the_day.append(segment)
    
    if len(dz_for_the_day) > 1: 
        for segment in dz_for_the_day:
            dz_text += segment + "\n\n"
    # dz_text += +"\n\n"

with open(dz_filename, encoding="utf-8", mode="w") as dz_file:
    dz_file.write(dz_text.rstrip())

print("\n<Local Botik>: Done!\n")