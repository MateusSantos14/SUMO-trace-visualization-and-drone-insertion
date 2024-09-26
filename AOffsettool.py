import xml.etree.ElementTree as ET

def read_and_offset_trace(file_path, output_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    # Verifica se a raiz do XML é <fcd-export>
    if root.tag != 'fcd-export':
        raise ValueError("Arquivo XML não é um trace válido.")
    
    # Aplica o offset de 1 aos tempos nos timesteps
    for timestep in root.findall('timestep'):
        time = timestep.get('time')
        if time is not None:
            if time == "0.00":
                # Remove todos os filhos do timestep com tempo "0.00"
                for child in list(timestep):
                    timestep.remove(child)
            else:
                # Aplica o offset de 1
                new_time = str(float(time) + 1.0)
                timestep.set('time', new_time)
    
    # Escreve o novo XML no arquivo de saída
    tree.write(output_path, encoding='utf-8', xml_declaration=True)

# Exemplo de uso
file_path = 'manhattan.xml'
output_path = 'manhattan.xml'
read_and_offset_trace(file_path, output_path)