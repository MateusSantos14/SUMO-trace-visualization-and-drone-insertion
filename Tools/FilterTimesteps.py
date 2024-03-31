from xml.etree import ElementTree as ET

from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString

def filter_timesteps_stream(input_xml_path, output_xml_path, max_time):
    with open(input_xml_path, 'r') as file:
        lines = []
        capture = False

        for line in file:
            if '<timestep' in line:
                time_value = float(line.split('time="')[1].split('"')[0])
                if time_value > max_time:
                    break
                capture = True
            if capture:
                lines.append(line)
            if '</timestep>' in line:
                capture = False

        # Ensure the closing tag is present for proper XML format
        if not lines[-1].strip().endswith('</fcd-export>'):
            lines.append('</fcd-export>\n')

    with open(output_xml_path, 'w') as outfile:
        outfile.writelines(lines)
        

def filter_timesteps(input_xml_path, output_xml_path, max_time):
    # Parse the input XML file
    tree = ET.parse(input_xml_path)
    root = tree.getroot()

    # Find all timestep elements
    timesteps = root.findall('timestep')

    # Loop over timestep elements in reverse order (to avoid index issues when removing)
    for timestep in reversed(timesteps):
        if float(timestep.get('time')) > max_time:
            # Remove timestep if its time attribute is greater than max_time
            root.remove(timestep)

    # Save the modified XML tree to another file
    tree.write(output_xml_path)