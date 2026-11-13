import json
from pathlib import Path

import numpy as np


def _read_opensignals_header(txt_path: Path) -> dict:
    with txt_path.open("r", encoding="utf-8") as file:
        for line in file:
            if line.startswith("# {"):
                metadata = json.loads(line[2:].strip())
                return next(iter(metadata.values()))
    raise ValueError(f"No se encontró el encabezado JSON de OpenSignals en {txt_path}")


def _get_sample(
    source: str | Path | np.ndarray,
    *,
    sensor: str | None,
    sampling_rate: float | None,
    units: str | None,
    column_index: int | None,
) -> tuple[np.ndarray, str, float, str]:
    if isinstance(source, (str, Path)):
        txt_path = Path(source)
        device_info = _read_opensignals_header(txt_path)
        columns = device_info.get("column", [])
        sensors = device_info.get("sensor", [])
        labels = device_info.get("label", [])
        sensor_name = sensor or (sensors[0] if sensors else "sensor")

        if sampling_rate is None:
            rate_from_header = device_info.get("sampling rate")
            if rate_from_header is None:
                raise ValueError(
                    f"El encabezado de {txt_path} no indica sampling rate."
                )
            sampling_rate = float(rate_from_header)

        if column_index is None:
            if sensor_name in columns:
                column_index = columns.index(sensor_name)
            elif sensor_name in sensors:
                sensor_index = sensors.index(sensor_name)
                if sensor_index >= len(labels) or labels[sensor_index] not in columns:
                    raise ValueError(
                        f"No se encontró la columna para el sensor {sensor_name!r}"
                    )
                column_index = columns.index(labels[sensor_index])
            elif sensor_name in labels:
                column_index = columns.index(sensor_name)
            else:
                available = sorted(set(sensors + labels))
                raise ValueError(
                    f"Sensor {sensor_name!r} no encontrado. Disponibles: {available}"
                )

        data = np.genfromtxt(
            txt_path,
            comments="#",
            delimiter="\t",
            usecols=range(len(columns)) if columns else None,
            ndmin=2,
        )
        if column_index < 0 or column_index >= data.shape[1]:
            raise ValueError(
                f"Índice de columna {column_index} fuera del rango "
                f"de {data.shape[1]} columnas"
            )
        values = data[:, column_index]
        units = units or "raw"
    else:
        values = np.asarray(source, dtype=float)
        sensor_name = sensor or "sensor"

        if values.ndim == 2:
            if column_index is None:
                raise ValueError(
                    "Para una matriz 2D indique column_index; "
                    "para una señal use un array 1D."
                )
            if column_index < 0 or column_index >= values.shape[1]:
                raise ValueError(
                    f"Índice de columna {column_index} fuera del rango "
                    f"de {values.shape[1]} columnas"
                )
            values = values[:, column_index]
        elif values.ndim != 1:
            raise ValueError("La señal debe ser un array 1D o una matriz 2D.")

        if sampling_rate is None:
            raise ValueError(
                "Indique sampling_rate cuando la fuente sea un array."
            )
        units = units or "raw"

    if not np.isfinite(sampling_rate) or sampling_rate <= 0:
        raise ValueError("sampling_rate debe ser un número positivo y finito.")
    if values.size == 0:
        raise ValueError("La señal no contiene muestras.")
    if not np.isfinite(values).all():
        raise ValueError("La señal contiene valores NaN o infinitos.")

    return values, sensor_name, float(sampling_rate), units


def _make_output_path(
    output_dir: str | Path,
    filename: str | Path | None,
    source: str | Path | np.ndarray,
    sensor: str,
    extension: str,
    label: str | None,
) -> Path:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if filename is None:
        stem = Path(source).stem if isinstance(source, (str, Path)) else sensor
        filename = f"{stem}.{extension}"
    else:
        filename = Path(filename)
        if filename.suffix.lower() != f".{extension}":
            filename = filename.with_suffix(f".{extension}")

    if label:
        filename = filename.with_name(f"{label}.{filename.name}")
    return out_dir / filename


def opensignals_txt_to_ei_json(
    source: str | Path | np.ndarray,
    output_dir: str | Path = "ei_json",
    *,
    sensor: str | None = None,
    sampling_rate: float | None = None,
    units: str | None = None,
    filename: str | Path | None = None,
    column_index: int | None = None,
    label: str | None = None,
) -> Path:
    """Write a signal as an Edge Impulse Data Acquisition JSON sample."""
    values, sensor_name, sampling_rate, units = _get_sample(
        source,
        sensor=sensor,
        sampling_rate=sampling_rate,
        units=units,
        column_index=column_index,
    )
    output_path = _make_output_path(
        output_dir, filename, source, sensor_name, "json", label
    )
    payload = {
        "protected": {"ver": "v1", "alg": "none"},
        "signature": "00",
        "payload": {
            "device_type": f"BITALINO_{sensor_name.upper()}",
            "interval_ms": 1000.0 / sampling_rate,
            "sensors": [{"name": sensor_name.lower(), "units": units}],
            "values": [[float(value)] for value in values],
        },
    }
    output_path.write_text(
        json.dumps(payload, indent=2, allow_nan=False), encoding="utf-8"
    )
    return output_path


def opensignals_txt_to_clean_csv(
    source: str | Path | np.ndarray,
    output_dir: str | Path = "ei_csv",
    *,
    sensor: str | None = None,
    sampling_rate: float | None = None,
    units: str | None = None,
    filename: str | Path | None = None,
    column_index: int | None = None,
    label: str | None = None,
) -> Path:
    """Write a signal as timestamped CSV for Edge Impulse time-series upload."""
    values, sensor_name, sampling_rate, _ = _get_sample(
        source,
        sensor=sensor,
        sampling_rate=sampling_rate,
        units=units,
        column_index=column_index,
    )
    output_path = _make_output_path(
        output_dir, filename, source, sensor_name, "csv", label
    )
    timestamps_ms = np.arange(values.size, dtype=float) * (1000.0 / sampling_rate)
    csv_values = np.column_stack((timestamps_ms, values))
    np.savetxt(
        output_path,
        csv_values,
        delimiter=",",
        header=f"timestamp,{sensor_name.lower()}",
        comments="",
        fmt="%.12g",
    )
    return output_path
