import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

def create_xml_with_timesteps(file_path, num_timesteps):
    # Create root element
    root = ET.Element('fcd-export', {
        'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'xsi:noNamespaceSchemaLocation': 'http://sumo.dlr.de/xsd/fcd_file.xsd'
    })

    # Add specified number of timesteps
    for i in range(num_timesteps+1):
        # Calculate the timestep time value (for example, incrementing by 2.0)
        time_value = f"{i:.2f}"
        ET.SubElement(root, 'timestep', {'time': time_value})

    # Create tree structure
    tree = ET.ElementTree(root)

    # Convert the tree to a string
    xml_str = ET.tostring(root, encoding='utf-8')

    # Use minidom to format the XML with line breaks and indentation
    dom = minidom.parseString(xml_str)
    pretty_xml_str = dom.toprettyxml(indent="    ")

    # Write the pretty XML to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(pretty_xml_str)

    print(f"Formatted XML with {num_timesteps} timesteps created at {file_path}")

# Example usage:
create_xml_with_timesteps('scenario1.xml', 200)
create_xml_with_timesteps('scenario2.xml', 200)
