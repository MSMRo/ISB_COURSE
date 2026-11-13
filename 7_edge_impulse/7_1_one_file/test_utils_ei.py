import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from utils_ei import opensignals_txt_to_clean_csv, opensignals_txt_to_ei_json


class EdgeImpulseExportTests(unittest.TestCase):
    def setUp(self):
        self.source = Path(__file__).with_name("SampleECG.txt")
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_opensignals_txt_exports_json_and_csv(self):
        json_path = opensignals_txt_to_ei_json(
            self.source, self.output_dir / "json", sensor="ECG"
        )
        csv_path = opensignals_txt_to_clean_csv(
            self.source, self.output_dir / "csv", sensor="ECG"
        )

        payload = json.loads(json_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["protected"], {"ver": "v1", "alg": "none"})
        self.assertEqual(payload["payload"]["interval_ms"], 1.0)
        self.assertEqual(len(payload["payload"]["values"]), 22350)
        self.assertEqual(payload["payload"]["values"][0], [496.0])

        data = np.genfromtxt(csv_path, delimiter=",", names=True)
        self.assertEqual(data.dtype.names, ("timestamp", "ecg"))
        self.assertEqual(len(data), 22350)
        self.assertEqual(data["timestamp"][1] - data["timestamp"][0], 1.0)
        self.assertEqual(data["ecg"][0], 496.0)

    def test_signal_array_exports_in_selected_units(self):
        signal = np.array([-0.046875, -0.0439453125, -0.041015625])
        json_path = opensignals_txt_to_ei_json(
            signal,
            self.output_dir / "json",
            sensor="ECG",
            sampling_rate=1000,
            units="mV",
        )
        csv_path = opensignals_txt_to_clean_csv(
            signal,
            self.output_dir / "csv",
            sensor="ECG",
            sampling_rate=1000,
            units="mV",
        )

        payload = json.loads(json_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["payload"]["sensors"][0]["units"], "mV")
        self.assertEqual(len(payload["payload"]["values"]), 3)
        data = np.genfromtxt(csv_path, delimiter=",", names=True)
        np.testing.assert_array_equal(data["ecg"], signal)
        np.testing.assert_array_equal(data["timestamp"], [0.0, 1.0, 2.0])


if __name__ == "__main__":
    unittest.main()
