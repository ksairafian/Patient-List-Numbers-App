import PySimpleGUI as sg
import csv
import regex as re

# TODO: Decide on universal themes for app
sg.theme('Reddit')
sg.set_options(font = 'Cambria, 11')

# Start Opening window - decides if user is going to create a list from scratch
# or upload an existing excel file (as a CSV) into the app
new_list = True

layout = [
    [sg.Text('Welcome to Plasmid - Rounds Made Easy!')],
    [sg.Text('Would you like to start a new list, or upload an existing list?')],
    [sg.Button('New List'), sg.Button('Upload Existing List')]
        ]

window = sg.Window('Welcome to Plasmid - Rounds Made Easy', layout)

# Event loops - User clicking a button leads to either new list or csv input
while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED or event == 'Exit':
        break
    if event == 'New List':
        new_list = True
        window.close()
    elif event == 'Upload Existing List':
        new_list = False
        window.close()
window.close()
# End opening window


# Start Intermediate Window - Selecting list elements and/or uploading csv
# TODO: fix file upload to only CSV for existing patient lists
if not new_list:
    layout = [[sg.Text('Upload CSV File')],
              [sg.Input(), sg.FileBrowse(file_types=('*.csv'))],
              [sg.OK(), sg.Cancel()]
              ]

    window = sg.Window('Upload Patient List', layout)
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == 'Exit':
            break
        if event == 'OK':
            csv_file = values[0]
                # TODO - Error Checking: Prevent users from uploading non-csv files - need to stay in window (HOW?)
            if not csv_file.endswith('.csv'):
                sg.popup('Error! Upload must be in CSV file format')
            window.close()
    window.close()

if not new_list:
    names = []
    rooms = []
    ages = []
    with open(csv_file, "r") as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            rooms.append(row[0])
            names.append(row[1])
            ages.append(row[2])

# Generating a list from scratch
checked_elements = []

# declaring layout categories for future use
demographics = []
vitals = []
labs = []
misc = []

# Lists of patient elements that can be included in the rounding list
if new_list:
    ptdemographics = ['Room', 'Patient Name', 'MRN', 'Age', 'Attending', 'Consult/Primary',
                      'Reason for Admission']
else:
    ptdemographics = []
ptvitals = ['Heart Rate', 'BP', 'SpO2', 'Temperature', 'Respiratory rate']
ptlabs = ['CBC', 'BMP', 'LFTs', 'Coags', 'ABG']
ptmisc = ['Ins and Outs', 'Diet', 'Anticoagulation', 'Antibiotics']

# Creating master dictionary to assign sequential numbers to each element
# so we have an absolute reference when creating the list
# Indexing starts at 1 to match the 'values' set that will be created when the GUI window is created
master = ptdemographics + ptvitals + ptlabs + ptmisc
master_dict = {}
for i in range(1, len(master) + 1):
    master_dict[master[i - 1]] = i

# Organizes a column of related checkboxes (ie Labs, Vitals, etc)
def cb_create(header, list_header, lo):
    lo += [sg.Text(header, font=('Cambria', '14', 'bold'))],
    for i in range(0, len(list_header)):
        lo += [sg.Checkbox(list_header[i], default=False)],

# Creating the columns and displaying checkboxes
if new_list:
    cb_create('Patient Demographics', ptdemographics, demographics)
cb_create('Vitals', ptvitals, vitals)
cb_create('Labs', ptlabs, labs)
cb_create('Miscellaneous', ptmisc, misc)

if new_list:
    layout = [
        [sg.Text('List Name:'), sg.Input('')],
        [sg.Text('Number of Patients:'), sg.Input('', size = (8, 1))],
        [sg.Column(demographics), sg.Column(vitals), sg.Column(labs), sg.Column(misc), ],
        [sg.OK(), sg.Cancel()]
    ]
else:
    layout = [
        [sg.Text('List Name:'), sg.Input('')],
        [sg.Column(vitals), sg.Column(labs), sg.Column(misc), ],
        [sg.OK(), sg.Cancel()]
    ]

window = sg.Window('Select List Elements', layout)
while True:
    event, values = window.read()
    if event in (None, 'Exit'):
        break
    if event == 'OK':
        list_name = values[0]
        if new_list:
            number_of_patients = int(values[1])
            print(number_of_patients)
        else:
            # TODO: UPDATE THIS WHEN YOU MODIFY YOUR CSV INPUT
            number_of_patients = len(names)
        if len(list_name) < 1:
            sg.popup('Error! Must Enter List Name!')
            break
        for j in range(1, len(values)):
            if values[j] == True:
                checked_elements.append(j)
        window.close()
    if event == 'Cancel':
        window.close()
        break
window.close()
# End Intermediate Windows

# Start Patient List Window
# TODO: create scroll-bar(s)
# TODO: make window autosize (if possible)
layout = []
# initializing rows for later, placeholder element to be removed after selected elements placed
if new_list:
    for i in range(0, len(checked_elements)):
        layout += [[sg.Text('')]]
else:
    # TODO: change range length to be variable with the amount of CSV elements added
    for i in range(0, len(checked_elements) + 3):
        layout += [[sg.Text('')]]

def new_row(lo, line):
    elements = []

    # TODO: finish coding in vitals, pt demographics, etc.
    # Patient Demographics for a new list
    if new_list:
        if master_dict['Room'] in checked_elements:
            room = [sg.InputText('Room', size=(5, 1))],
            elements.append(room)

        if master_dict['Patient Name'] in checked_elements:
            pt_name = [sg.InputText('Name', size =(15,1))],
            elements.append(pt_name)

        if master_dict['Age'] in checked_elements:
            age = [sg.InputText('Age/Sex', size =(4,1))],
            elements.append(age)

    # Patient Demographics for an imported list
    if not new_list:
        room = [sg.Text(str(rooms[line]))],
        elements.append(room)

        name = [sg.Text(str(names[line]))],
        elements.append(name)

        age = [sg.Text(str(ages[line]))],
        elements.append(age)

# vitals segment
    vital_bool = False
    for item in (ptvitals):
        if master_dict[item] in checked_elements:
            vital_bool = True
    if vital_bool:
        vitals = [[], [], []]
        if master_dict['BP'] in checked_elements:
            vitals[0] += sg.Input('BP', size=(7, 1)),
        if master_dict['Temperature'] in checked_elements:
            vitals[0] += sg.Input('Tmax', size=(6, 1)),
        if master_dict['Heart Rate'] in checked_elements:
            vitals[1] += sg.Input('HR', size=(7, 1)),
        if master_dict['Respiratory rate'] in checked_elements:
            vitals[1] += sg.Input('RR', size=(6, 1)),
        if master_dict['SpO2'] in checked_elements:
            vitals[2] += sg.Input('SpO2', size=(6, 1)),
        elements.append(vitals)

    if master_dict['BMP'] in checked_elements:
        bmp = [
            [sg.Input('Na', size = (4,1)), sg.Text('|'), sg.Input('Cl', size = (4,1)), sg.Text('|'), sg.Input('BUN', size = (4,1)), sg.Text('/'), sg.Input('Gluc', size = (4,1), pad=((0,0),(20,0)))],
            [sg.Input('K', size = (4,1)), sg.Text('|'), sg.Input('HCO3', size = (4,1)), sg.Text('|'), sg.Input('Cr', size = (4,1)), sg.Text('\\')],
            ]
        elements.append(bmp)

    if master_dict['CBC'] in checked_elements:
        cbc = [
            [sg.Input('WBC', size = (4,1), pad=((0,3),(20,0))), sg.Text('  \\'), sg.Input('Hgb', size = (4,1)), sg.Text('/'), sg.Input('Plt', size = (4,1), pad=((3,0),(20,0)))],
            [sg.Text("             /"), sg.Input('Hct', size = (4,1)), sg.Text('\\')],
            ]
        elements.append(cbc)

    if master_dict['LFTs'] in checked_elements:
        lft = [
            [sg.Input('AST', size = (4,1), pad=((0,3),(20,0))), sg.Text('  \\'), sg.Input('TBili', size = (4,1)), sg.Text('/'), sg.Input('ALT', size = (4,1), pad=((3,0),(20,0)))],
            [sg.Text("             /"), sg.Input('Alk Phos', size = (4,1)), sg.Text('\\')],
            ]
        elements.append(lft)

    if master_dict['Ins and Outs'] in checked_elements:
        headings = [[sg.Text('In            |        Out')], ]
        input_rows = [[sg.Input(size=(8, 1), pad=(0, 0)) for col in range(2)] for row in range(2)]
        ino = headings + input_rows
        elements.append(ino)

    for j in range(0, len(elements)):
        print(j)
        lo[line].append(sg.Frame('', elements[j], border_width=0),)

# TODO: Fix this bullshit. Need to put in number of patients somewhere earlier
for i in range(0, number_of_patients):
    print(i)
    new_row(layout, i)
    # remove placeholder elements
    del layout[i][0]

window = sg.Window(list_name, resizable=True).Layout([[sg.Column(layout, size=(300,300), scrollable=True)]])

# TODO: Create final events?
while True:
    event, values = window.read()
    if event in (None, 'Exit'):
        break
window.close()
# End List window

# TODO: Assemble PDF of inputted data?
