import xml.etree.ElementTree as ET
from math import cos, radians

from pyproj import Proj, transform

def longitude_to_utm_zone(longitude):
    """
    Calculate the UTM zone number from longitude.
    
    Parameters:
    - longitude: Longitude in decimal degrees.
    
    Returns:
    - int: UTM zone number.
    """
    return int((longitude + 180) / 6) + 1

def latlon_to_utm(lat, lon):
    """
    Convert latitude and longitude to UTM coordinates.
    Parameters:
    - lat: Latitude.
    - lon: Longitude.
    
    Returns:
    - x, y: UTM coordinates
    """
    #Calculate zone
    zone = longitude_to_utm_zone(lon)
    # Define the projection for WGS84
    wgs84 = Proj(proj='latlong', datum='WGS84')
    
    # Define the UTM projection based on the zone number
    utm = Proj(proj='utm', zone=zone, datum='WGS84')
    
    # Transform coordinates
    x, y = transform(wgs84, utm, lon, lat)
    
    return x, y

def latlon_to_xy(lat, lon, min_lat, min_lon):
    """ Convert latitude and longitude to Cartesian coordinates (x, y). """
    R = 6378137  # Earth’s radius in meters
    dLat = radians(lat - min_lat)
    dLon = radians(lon - min_lon)
    x = R * dLon * cos(radians(min_lat))
    y = R * dLat
    return x, y

def convert_coordinates(input_xml_path, output_xml_path):
    # Load and parse the XML data
    tree = ET.parse(input_xml_path)
    root = tree.getroot()

    # Namespace management for correct output
    namespaces = {
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }
    # Registering the namespace under the prefix 'xsi'
    ET.register_namespace('xsi', namespaces['xsi'])

    # Initialize minimum latitude and longitude values
    min_lat = float('inf')
    min_lon = float('inf')

    # Find the minimum latitude and longitude to use as a reference point
    for vehicle in root.findall('.//vehicle', namespaces):
        x = float(vehicle.get('x'))
        y = float(vehicle.get('y'))
        if x < min_lon:
            min_lon = x
        if y < min_lat:
            min_lat = y

    # Convert coordinates and update the attributes
    for vehicle in root.findall('.//vehicle', namespaces):
        x = float(vehicle.get('x'))
        y = float(vehicle.get('y'))
        x_m, y_m = latlon_to_xy(y, x, min_lat, min_lon)
        vehicle.set('x', str(round(x_m, 2)))
        vehicle.set('y', str(round(y_m, 2)))

    # Write the modified XML with correct declaration and encoding
    tree.write(output_xml_path, xml_declaration=True, encoding='utf-8', default_namespace=None)

    print(f"Conversion complete and saved to '{output_xml_path}'")

def convert_coordinates2(input_xml_path, output_xml_path):
    # Load and parse the XML data
    tree = ET.parse(input_xml_path)
    root = tree.getroot()

    # Namespace management for correct output
    namespaces = {
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }
    # Registering the namespace under the prefix 'xsi'
    ET.register_namespace('xsi', namespaces['xsi'])

    # Initialize minimum latitude and longitude values
    min_lat = float('inf')
    min_lon = float('inf')

    # Find the minimum latitude and longitude to use as a reference point
    for vehicle in root.findall('.//vehicle', namespaces):
        x = float(vehicle.get('x'))
        y = float(vehicle.get('y'))
        if x < min_lon:
            min_lon = x
        if y < min_lat:
            min_lat = y
    x_min, y_min = latlon_to_utm(min_lat, min_lon)
    # Convert coordinates and update the attributes
    for vehicle in root.findall('.//vehicle', namespaces):
        x = float(vehicle.get('x'))
        y = float(vehicle.get('y'))
        #x_m, y_m = latlon_to_xy(y, x, min_lat, min_lon)
        x_m, y_m = latlon_to_utm(y, x)
        vehicle.set('x', str(round(x_m-x_min, 2)))
        vehicle.set('y', str(round(y_m-y_min, 2)))

    # Write the modified XML with correct declaration and encoding
    tree.write(output_xml_path, xml_declaration=True, encoding='utf-8', default_namespace=None)

    print(f"Conversion complete and saved to '{output_xml_path}'")

# Example usage
#convert_coordinates('outputns3.xml', 'outputns3conv.xml')
#convert_coordinates2('outputns3.xml', 'outputns3conv2.xml')
