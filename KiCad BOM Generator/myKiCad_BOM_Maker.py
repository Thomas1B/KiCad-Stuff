'''
Custom KiCad BOM Maker.

Modified from pre-written plugin.
'''


"""
    @package
    Output: CSV (comma-separated)
    Grouped By: Value, Footprint, DNP
    Sorted By: Ref
    Fields: Ref, Qnty, Value, Cmp name, Footprint, Description

    Command line:
    python "pathToFile/KiCad_BOM_Maker.py" "%I" "%O.csv"
"""

# Import the KiCad python helper module and the csv formatter

# A helper function to filter/convert a string read in netlist
# currently: do nothing




import kicad_netlist_reader
import kicad_utils
import csv
import sys
import os
def fromNetlistText(aText):
    return aText


def make_new_path(path):
    # makes path of last dir and filename
    folder, filename = os.path.split(path)
    folder = folder.split('\\')[-1]
    return '\\'.join([folder, filename])


# Generate an instance of a generic netlist, and load the netlist tree from
# the command line option. If the file doesn't exist, execution will stop
net = kicad_netlist_reader.netlist(sys.argv[1])

# Open a file to write to, if the file cannot be opened output to stdout
# instead
try:
    name, ext = os.path.splitext(sys.argv[2])
    sys.argv[2] = f'{name} KiCad BOM{ext}'
    f = kicad_utils.open_file_writeUTF8(sys.argv[2], 'w')
except IOError:
    e = "Can't open output file for writing: " + sys.argv[2]
    print(__file__, ":", e, sys.stderr)
    f = sys.stdout

# Create a new csv writer object to use as the output formatter
out = csv.writer(f, lineterminator='\n', delimiter=',',
                 quotechar='\"', quoting=csv.QUOTE_ALL)

part_type_count = len(net.groupComponents())

# Output a set of rows for a header providing general information
out.writerow(['Project:', make_new_path(net.getSource())])
out.writerow(['Date:', net.getDate().split(' ')[0]])
out.writerow(['Tool:', net.getTool()])
out.writerow(['BOM Generator:', make_new_path(sys.argv[0])])
out.writerow([])
out.writerow(['Total Component Count:', len(net.components)])
out.writerow(['Component Type Count:', part_type_count])
out.writerow([
    'Ref',
    'Qnty',
    'Value',
    'Description',
    'Cmp name',
    'Footprint'
])
out.writerow([])


# Get all of the components in groups of matching parts + values
# (see ky_generic_netlist_reader.py)
grouped = net.groupComponents()

# Output all of the component information
for count, group in enumerate(grouped, 1):
    refs = ""

    # Add the reference of every component in the group and keep a reference
    # to the component so that the other data can be filled in once per group
    for component in group:
        if refs != "":
            refs += ", "
        refs += fromNetlistText(component.getRef())
        c = component

    description = c.getDescription()
    if all(s in description for s in ['script', 'generated']):
        description = description.split(',')[:-1]
        description = [d.strip() for d in description]
        description = ", ".join(description)

    # Fill in the component groups common data
    out.writerow([f"Component: {count}/{part_type_count}:"])
    out.writerow([
        refs,
        len(group),  # quantity
        fromNetlistText(c.getValue()),
        description,
        fromNetlistText(c.getPartName()),
        fromNetlistText(c.getFootprint())
    ])
    out.writerow([])

    # Removing XML File
    path = os.path.splitext(sys.argv[2])[0].strip(' BOM')
    xml_path = f'{path}.xml'
    if os.path.exists(xml_path):
        os.remove(xml_path)
