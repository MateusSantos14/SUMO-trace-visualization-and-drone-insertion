import xml.etree.ElementTree as ET
from math import cos, radians
from pyproj import Proj, transform

def longitude_to_utm_zone(longitude):
    """
    Calcula o número da zona UTM a partir da longitude.
    
    Parâmetros:
    - longitude: Longitude em graus decimais.
    
    Retorna:
    - int: Número da zona UTM.
    """
    return int((longitude + 180) / 6) + 1

def latlon_to_utm(lat, lon):
    """
    Converte latitude e longitude para coordenadas UTM.
    
    Parâmetros:
    - lat: Latitude em graus decimais.
    - lon: Longitude em graus decimais.
    
    Retorna:
    - x, y: Coordenadas UTM (Easting, Northing).
    """
    zone = longitude_to_utm_zone(lon)
    wgs84 = Proj(proj='latlong', datum='WGS84')
    utm = Proj(proj='utm', zone=zone, datum='WGS84')
    x, y = transform(wgs84, utm, lon, lat)
    return x, y

def latlon_to_xy(lat, lon, min_lat, min_lon):
    """
    Converte latitude e longitude para coordenadas Cartesianas (x, y).
    
    Parâmetros:
    - lat: Latitude em graus decimais.
    - lon: Longitude em graus decimais.
    - min_lat: Latitude mínima de referência.
    - min_lon: Longitude mínima de referência.
    
    Retorna:
    - x, y: Coordenadas Cartesianas em metros.
    """
    R = 6378137  # Raio da Terra em metros
    dLat = radians(lat - min_lat)
    dLon = radians(lon - min_lon)
    x = R * dLon * cos(radians(min_lat))
    y = R * dLat
    return x, y

def convert_coordinates(input_xml_path, output_xml_path):
    """
    Converte coordenadas de latitude e longitude em um arquivo XML para coordenadas Cartesianas.
    
    Parâmetros:
    - input_xml_path: Caminho do arquivo XML de entrada.
    - output_xml_path: Caminho do arquivo XML de saída.
    """
    tree = ET.parse(input_xml_path)
    root = tree.getroot()

    # Gerenciamento de namespaces para garantir a saída correta
    namespaces = {'xsi': 'http://www.w3.org/2001/XMLSchema-instance'}
    ET.register_namespace('xsi', namespaces['xsi'])

    # Inicializa os valores mínimos de latitude e longitude
    min_lat = float('inf')
    min_lon = float('inf')
    for vehicle in root.findall('.//vehicle', namespaces):
        x = float(vehicle.get('x'))
        y = float(vehicle.get('y'))
        if x < min_lon:
            min_lon = x
        if y < min_lat:
            min_lat = y

    # Converte as coordenadas e atualiza os atributos
    for vehicle in root.findall('.//vehicle', namespaces):
        x = float(vehicle.get('x'))
        y = float(vehicle.get('y'))
        x_m, y_m = latlon_to_xy(y, x, min_lat, min_lon)
        vehicle.set('x', str(round(x_m, 2)))
        vehicle.set('y', str(round(y_m, 2)))

    # Salva o XML modificado com declaração e codificação corretas
    tree.write(output_xml_path, xml_declaration=True, encoding='utf-8', default_namespace=None)

    print(f"Conversão concluída e salva em '{output_xml_path}'")