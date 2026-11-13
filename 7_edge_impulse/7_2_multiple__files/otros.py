"""Modificar ligeramente las señales ECG dentro de los archivos raw."""

import glob
import hashlib
import json
import os
import shutil

import numpy as np
from opensignalsreader import OpenSignalsReader


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RECORDS_ROOT = os.path.join(SCRIPT_DIR, "records_bitalino")
BACKUP_FOLDER = "raw_originales"
SENSOR = "ECG"
SEED = 2026
MODIFIED_SAMPLE_RATIO = 0.01


def file_hash(path):
    with open(path, "rb") as file:
        return hashlib.sha256(file.read()).hexdigest()


def seed_for_file(raw_file):
    relative_path = os.path.relpath(raw_file, RECORDS_ROOT)
    seed_bytes = hashlib.sha256(f"{SEED}:{relative_path}".encode("utf-8")).digest()
    return int.from_bytes(seed_bytes[:8], byteorder="big")


def find_signal_column(device_info):
    columns = device_info["column"]
    sensors = device_info["sensor"]
    labels = device_info["label"]
    sensor_index = sensors.index(SENSOR)
    return columns.index(labels[sensor_index])


def modify_raw_file(raw_file, backup_file):
    with open(backup_file, "rb") as file:
        original_text = file.read().decode("utf-8")
    lines = original_text.splitlines(keepends=True)

    metadata = None
    header_end = None
    for index, line in enumerate(lines):
        if line.startswith("# {"):
            metadata = next(iter(json.loads(line[2:].strip()).values()))
        if line.strip() == "# EndOfHeader":
            header_end = index
            break
    if metadata is None or header_end is None:
        raise ValueError(f"Encabezado OpenSignals inválido: {raw_file}")

    column_index = find_signal_column(metadata)
    resolution = int(metadata["resolution"][column_index])
    adc_max = (2**resolution) - 1

    acquisition = OpenSignalsReader(backup_file)
    raw_signal = np.asarray(acquisition.raw(SENSOR), dtype=int)
    sample_count = len(raw_signal)
    number_to_change = max(1, round(sample_count * MODIFIED_SAMPLE_RATIO))

    rng = np.random.default_rng(seed_for_file(raw_file))
    sample_indices = rng.choice(sample_count, size=number_to_change, replace=False)
    changes = rng.choice((-1, 1), size=number_to_change)
    modified_values = raw_signal.copy()
    modified_values[sample_indices] = np.clip(
        modified_values[sample_indices] + changes, 0, adc_max
    )

    sample_index = 0
    changed_count = 0
    for line_index in range(header_end + 1, len(lines)):
        line = lines[line_index]
        if not line.strip() or line.lstrip().startswith("#"):
            continue

        if line.endswith("\r\n"):
            line_ending = "\r\n"
            body = line[:-2]
        elif line.endswith(("\n", "\r")):
            line_ending = line[-1]
            body = line[:-1]
        else:
            line_ending = ""
            body = line

        fields = body.split("\t")
        if column_index >= len(fields) or sample_index >= sample_count:
            raise ValueError(f"Datos OpenSignals inválidos: {raw_file}")

        original_value = int(round(float(fields[column_index])))
        if original_value != raw_signal[sample_index]:
            raise ValueError(f"El canal ECG no coincide con los datos: {raw_file}")

        new_value = int(modified_values[sample_index])
        changed_count += new_value != original_value
        fields[column_index] = str(new_value)
        lines[line_index] = "\t".join(fields) + line_ending
        sample_index += 1

    if sample_index != sample_count or changed_count == 0:
        raise ValueError(f"No se modificaron muestras ECG en {raw_file}")

    temporary_file = f"{raw_file}.tmp"
    with open(temporary_file, "wb") as file:
        file.write("".join(lines).encode("utf-8"))
    os.replace(temporary_file, raw_file)
    return changed_count


label_dirs = sorted(
    path
    for path in glob.glob(os.path.join(RECORDS_ROOT, "label_*"))
    if os.path.isdir(path)
)
if not label_dirs:
    raise FileNotFoundError(f"No se encontraron carpetas label_* en {RECORDS_ROOT}")

modified_files = []
original_hashes = set()
for label_dir in label_dirs:
    label = os.path.basename(label_dir)
    raw_dir = os.path.join(label_dir, "raw")
    backup_dir = os.path.join(label_dir, BACKUP_FOLDER)
    raw_files = sorted(glob.glob(os.path.join(raw_dir, "*.txt")))
    if not raw_files:
        raise FileNotFoundError(f"No se encontraron archivos .txt en {raw_dir}")

    os.makedirs(backup_dir, exist_ok=True)
    for raw_file in raw_files:
        backup_file = os.path.join(backup_dir, os.path.basename(raw_file))
        if not os.path.exists(backup_file):
            shutil.copy2(raw_file, backup_file)

        original_hashes.add(file_hash(backup_file))
        changed_count = modify_raw_file(raw_file, backup_file)
        modified_files.append(raw_file)
        print(f"{label}: {os.path.basename(raw_file)} ({changed_count} muestras alteradas)")

    print(f"Originales respaldados en: {backup_dir}")

modified_hashes = {file_hash(path) for path in modified_files}
if len(modified_hashes) != len(modified_files):
    raise RuntimeError("Algunos archivos raw modificados todavía son idénticos.")

if len(original_hashes) < len(modified_files):
    print(
        f"ADVERTENCIA: {len(modified_files)} archivos raw originales tienen solo "
        f"{len(original_hashes)} contenido(s) distinto(s). El ruido no crea "
        "grabaciones reales ni corrige etiquetas contradictorias."
    )

print(f"Se modificaron {len(modified_files)} archivos raw.")
print("Las carpetas formateado no fueron modificadas.")
