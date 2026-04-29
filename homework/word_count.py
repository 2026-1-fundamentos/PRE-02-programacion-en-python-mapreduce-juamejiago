"""Taller evaluable"""

# pylint: disable=broad-exception-raised

import fileinput
import glob
import os.path
import shutil
import time
from itertools import groupby


def _concat(sequences):
    # Aplana una secuencia de iterables en un solo flujo.
    for seq in sequences:
        for item in seq:
            yield item


def _pluck(index, sequence):
    # Devuelve el elemento en la posicion `index` de cada item.
    for item in sequence:
        yield item[index]



def copy_raw_files_to_input_folder(n):
    """Generate n copies of the raw files in the input folder"""
    # Recrea files/input con N copias de cada archivo raw.
    raw_files = glob.glob(os.path.join("files", "raw", "*.txt"))
    input_dir = os.path.join("files", "input")

    if os.path.exists(input_dir):
        shutil.rmtree(input_dir)
    os.makedirs(input_dir, exist_ok=True)

    for i in range(n):
        for raw_file in raw_files:
            base = os.path.basename(raw_file)
            name, ext = os.path.splitext(base)
            target = os.path.join(input_dir, f"{name}-{i:05d}{ext}")
            with open(raw_file, "r", encoding="utf-8") as src:
                content = src.read()
            with open(target, "w", encoding="utf-8") as dst:
                dst.write(content)



def load_input(input_directory):
    """Funcion load_input"""
    # Lee todos los archivos de entrada como un unico iterable de lineas.
    files = glob.glob(os.path.join(input_directory, "*"))
    return fileinput.input(files=files, openhook=fileinput.hook_encoded("utf-8"))


def preprocess_line(x):
    """Preprocess the line x"""
    # Normaliza a minusculas y conserva solo letras como tokens.
    return "".join(ch.lower() if ch.isalpha() else " " for ch in x)


def map_line(x):
    # Convierte una linea en pares (palabra, 1).
    cleaned = preprocess_line(x)
    words = [word for word in cleaned.split() if word]
    return [(word, 1) for word in words]

def mapper(sequence):
    """Mapper"""
    # Aplica map_line a cada linea y aplana los resultados.
    return _concat(map(map_line, sequence))


def shuffle_and_sort(sequence):
    """Shuffle and Sort"""
    # Ordena por palabra y agrupa para preparar la reduccion.
    sorted_sequence = sorted(sequence, key=lambda item: item[0])
    return groupby(sorted_sequence, key=lambda item: item[0])



def compute_sum_by_group(group):
    # Suma los conteos de una palabra agrupada.
    key, values = group
    return key, sum(_pluck(1, values))

def reducer(sequence):
    """Reducer"""
    # Reduce cada grupo a (palabra, total).
    return map(compute_sum_by_group, sequence)


def create_directory(directory):
    """Create Output Directory"""
    # Asegura un directorio de salida limpio.
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.makedirs(directory, exist_ok=True)


def save_output(output_directory, sequence):
    """Save Output"""
    # Escribe la salida del reducer en un archivo tipo part.
    output_path = os.path.join(output_directory, "part-00000")
    with open(output_path, "w", encoding="utf-8") as f:
        for key, value in sequence:
            f.write(f"{key}\t{value}\n")


def create_marker(output_directory):
    """Create Marker"""
    # Crea el archivo marcador _SUCCESS que esperan las pruebas.
    marker_path = os.path.join(output_directory, "_SUCCESS")
    with open(marker_path, "w", encoding="utf-8"):
        pass


def run_job(input_directory, output_directory):
    """Job"""
    # Ejecuta el flujo completo de entrada a salida.
    sequence = load_input(input_directory)
    sequence = mapper(sequence)
    sequence = shuffle_and_sort(sequence)
    sequence = reducer(sequence)
    create_directory(output_directory)
    save_output(output_directory, sequence)
    create_marker(output_directory)


if __name__ == "__main__":

    copy_raw_files_to_input_folder(n=1000)

    start_time = time.time()

    run_job(
        "files/input",
        "files/output",
    )

    end_time = time.time()
    print(f"Tiempo de ejecución: {end_time - start_time:.2f} segundos")
