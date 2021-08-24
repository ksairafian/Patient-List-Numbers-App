import PySimpleGUI as sg

sg.theme('Dark Blue 3')

opening_layout = [
    [sg.Text('List Generation: open a new list or choose an existing')],
    [sg.Radio('New List', 'RADIO1', default = True)],
    [sg.Radio('Open Existing List, RADIO1', default = False)],
    [sg.OK()]
]

window = sg.Window('Welcome', opening_layout)
event, values = window.read()
window.close()