import xml.etree.ElementTree as ET

def read_and_offset_trace(file_path, output_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    # Verifica se a raiz do XML é <fcd-export>
    if root.tag != 'fcd-export':
        raise ValueError("Arquivo XML não é um trace válido.")
    
    # Aplica o offset de 1 aos tempos nos timesteps existentes
    for timestep in root.findall('timestep'):
        time = timestep.get('time')
        if time is not None:
            # Aplica o offset de 1
            new_time = str(float(time) + 1.0)
            timestep.set('time', new_time)
    
    # Cria um novo timestep com tempo "0.00" e sem filhos
    new_timestep = ET.Element('timestep', {'time': "0.00"})
    root.insert(0, new_timestep)  # Insere o novo timestep no início do XML
    
    # Escreve o novo XML no arquivo de saída
    tree.write(output_path, encoding='utf-8', xml_declaration=True)

# Use a função passando os caminhos do arquivo de entrada e de saída
# Exemplo:
# read_and_offset_trace('input.xml', 'output.xml')


# Exemplo de uso
file_path = 'manhattan.xml'
output_path = 'manhattan2.xml'
read_and_offset_trace(file_path, output_path)