"""Check the measured evidence independently of any future live decoder."""
import hashlib
import json
import unittest
from pathlib import Path


def load_capture(name: str) -> list:
    path = Path(__file__).parent / 'fixtures' / '2026-11-01' / name
    return [json.loads(line) for line in path.read_text().splitlines()]


def reports_for(records: list, trial_id: str) -> list:
    return [row for row in records if row['event'] == 'input_report' and row.get('trial_id') == trial_id]


class CaptureFixtureTests(unittest.TestCase):
    def test_manifest_and_journal_integrity(self):
        root = Path(__file__).parent / 'fixtures' / '2026-11-01'
        manifest = json.loads((root / 'manifest.json').read_text())
        for capture in manifest['captures']:
            data = (root / capture['file']).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), capture['export_sha256'])
            rows = load_capture(capture['file'])
            self.assertEqual(len(rows), capture['records'])
            self.assertEqual([row['sequence'] for row in rows], list(range(1, len(rows) + 1)))
            self.assertEqual(sum(row['event'] == 'input_report' for row in rows), capture['input_reports'])
            self.assertEqual(rows[-1]['exit_code'], 0)
            for row in rows:
                if row['event'] == 'input_report':
                    raw = bytes.fromhex(row['raw_hex'])
                    self.assertEqual((len(raw), raw[0]), (row['length'], row['report_id']))
                if row['event'] == 'trial_end':
                    self.assertEqual(len(reports_for(rows, row['trial_id'])), row['received_reports'])

    def test_t_taps_repeat_and_hold_signals_differ(self):
        rows = load_capture('baseline.jsonl')
        signatures = []
        for identifier in ('T-upper-single-1', 'T-middle-single-2', 'T-lower-single-3'):
            raw = [row['raw_hex'] for row in reports_for(rows, identifier)]
            self.assertEqual(len(raw), 40)
            self.assertEqual(raw, raw[:8] * 5)
            signatures.append(tuple(raw[:8]))
        self.assertEqual(len(set(signatures)), 3)
        for identifier, pressed in (('T-upper-hold-10', '02ea00'), ('T-lower-hold-12', '02e900')):
            raw = [row['raw_hex'] for row in reports_for(rows, identifier)]
            self.assertGreater(len(raw), 2)
            self.assertEqual(raw, [pressed, '020000'] * (len(raw) // 2))

    def test_confirmation_repeats_lower_hold_pattern(self):
        baseline = reports_for(load_capture('baseline.jsonl'), 'C-lower-hold-24')
        rows = load_capture('confirmation.jsonl')
        confirmed = reports_for(rows, 'easy-08-attempt8')
        pattern = [row['raw_hex'] for row in baseline[:5]]
        self.assertEqual([row['raw_hex'] for row in confirmed], pattern * 5)
        self.assertEqual(sum(row['event'] == 'input_report' for row in rows), 25)
        self.assertEqual(len([row for row in rows if row['event'] == 'trial_end' and row['received_reports'] == 0]), 7)


if __name__ == '__main__':
    unittest.main()
