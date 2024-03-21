import xml.etree.ElementTree as ET

def remove_existing_vehicles(root):
    """Remove all <vehicle> elements from each <timestep>."""
    for timestep in root.findall('.//timestep'):
        for vehicle in timestep.findall('vehicle'):
            timestep.remove(vehicle)

def add_new_vehicles(root, timesteps_data):
    """Add new <vehicle> elements to each <timestep> based on provided data."""
    for timestep_data in timesteps_data:
        time = timestep_data['time']
        timestep = root.find(f".//timestep[@time='{time}']")
        if timestep is None:
            timestep = ET.SubElement(root, 'timestep', attrib={'time': time})
        for vehicle_id, attributes in timestep_data['vehicles'].items():
            ET.SubElement(timestep, 'vehicle', attrib={'id': vehicle_id, **attributes})

def merge_xml_with_new_vehicles(original_xml_path, new_vehicles_data, output_xml_path):
    tree = ET.parse(original_xml_path)
    root = tree.getroot()

    # Remove existing vehicles from timesteps
    remove_existing_vehicles(root)

    # Add new vehicles from the provided data
    add_new_vehicles(root, new_vehicles_data)

    # Save the modified XML to a new file
    tree.write(output_xml_path, encoding='UTF-8', xml_declaration=True)