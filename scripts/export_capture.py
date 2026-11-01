"""Export reviewable capture fixtures without machine identifiers or free-text notes."""
import argparse
import hashlib
import json
from pathlib import Path


def export_record(record: dict) -> dict:
    fields = {'schema_version', 'session_id', 'sequence', 'event', 'utc', 'monotonic_ns',
              'observed_utc', 'observed_monotonic_ns', 'device_index', 'status', 'report_type',
              'report_id', 'length', 'raw_hex', 'connection_generation', 'trial_id', 'result',
              'result_hex', 'success', 'suppression_verified', 'seized_entries', 'code', 'state',
              'matching_entries', 'product_exact', 'user_selected_mode', 'outcome', 'received_reports',
              'verified', 'results_verified', 'plan_version', 'exit_code', 'trials'}
    output = {key: value for key, value in record.items() if key in fields}
    if isinstance(output.get('trials'), list):
        output.pop('trials')
    if 'trial' in record:
        fields = {'mode', 'button', 'action', 'repetitions', 'checklist_id', 'physical_timing'}
        output['trial'] = {key: value for key, value in record['trial'].items() if key in fields}
    if 'details' in record:
        fields = {'Product', 'Transport', 'VendorID', 'ProductID', 'VersionNumber', 'PrimaryUsagePage',
                  'PrimaryUsage', 'MaxInputReportSize', 'ReportDescriptor', 'report_descriptor_sha256'}
        output['details'] = {key: value for key, value in record['details'].items() if key in fields}
    if 'environment' in record:
        fields = {'platform', 'macos_version', 'machine', 'python', 'backend', 'diagnostic_version',
                  'physical_mode', 'actions_enabled', 'source_sha256'}
        output['environment'] = {key: value for key, value in record['environment'].items() if key in fields}
    return output


def export_capture(source: Path, destination: Path) -> dict:
    original = source.read_bytes()
    records = [export_record(json.loads(line)) for line in original.splitlines()]
    encoded = ''.join(json.dumps(record, sort_keys=True) + '\n' for record in records).encode()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open('xb') as stream:
        stream.write(encoded)
    return {'file': destination.name, 'session_id': records[0]['session_id'],
            'records': len(records), 'input_reports': sum(row['event'] == 'input_report' for row in records),
            'source_sha256': hashlib.sha256(original).hexdigest(),
            'export_sha256': hashlib.sha256(encoded).hexdigest()}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    arguments = parser.parse_args()
    print(json.dumps(export_capture(arguments.source, arguments.output), indent=2))


if __name__ == '__main__':
    main()
