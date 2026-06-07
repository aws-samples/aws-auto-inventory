# Architecture

This document describes how AWS Auto Inventory is structured: the supported `scan.py` scanner that ships today, and the in-progress `aws_auto_inventory` package that is being built to replace it.

## Overview

The repository holds two implementations at different stages of maturity.

- **`scan.py`** is the supported scanner. It reads a JSON scan file (a list of API calls), runs the calls concurrently across Regions and services, and writes one JSON file per service and function. `organization_scanner.py` extends it to scan every account in an AWS Organization.
- **`aws_auto_inventory`** is a package that reorganizes the same scanning logic behind a layered design with YAML and JSON configuration, Pydantic validation, and planned Excel output. The package is incomplete: its command-line interface (CLI) imports an output module that does not yet exist, so the `aws-auto-inventory` console script cannot produce output today.

Both implementations call AWS APIs through boto3 and use the same retry and result-extraction model.

## Supported implementation: scan.py

### Components

| Component | File | Responsibility |
| --- | --- | --- |
| CLI and orchestrator | `scan.py` (`main`) | Parses arguments, loads the scan file, resolves Regions, and coordinates concurrent scanning. |
| Service caller | `scan.py` (`_get_service_data`, `api_call_with_retry`) | Calls one API function for one service in one Region, with retry and result extraction. |
| Region worker | `scan.py` (`process_region`) | Scans all configured services within a single Region. |
| Credential check | `scan.py` (`check_aws_credentials`) | Calls `sts:GetCallerIdentity` and prints the authenticated principal before scanning. |
| Organization scanner | `organization_scanner.py` | Lists organization accounts, assumes a role in each, and runs `scan.py`'s `main` against each account. |
| Scan-file builder | `scan_builder.py` | Generates per-service scan files listing every `get`, `describe`, and `list` function. |

### Data flow

```text
scan file (JSON list)        AWS credentials (boto3 chain)
        |                              |
        v                              v
   main(): load scan file, verify credentials, resolve Regions
        |
        v
   ThreadPoolExecutor over Regions  (--concurrent-regions)
        |
        v
   process_region(): ThreadPoolExecutor over services  (--concurrent-services)
        |
        v
   _get_service_data(): boto3 client.<function>(**parameters)
        |  retry on Throttling / RequestLimitExceeded / BotoCoreError
        |  extract result_key (plain key or jq filter)
        v
   write output/<timestamp>/<region>/<service>-<function>.json
```

`main` reads the scan file from a local path or, when the value starts with `http://` or `https://`, fetches it over HTTP. If you do not pass `--regions`, it calls `ec2:DescribeRegions` and scans every Region whose opt-in status is `opt-in-not-required` or `opted-in`.

### Concurrency

Scanning runs on two nested thread pools. The outer pool processes Regions; the inner pool, created in `process_region`, processes the services within a Region. You bound each pool with `--concurrent-regions` and `--concurrent-services`. When a bound is not set, the pool uses its default worker count.

### Retry and throttling

`api_call_with_retry` wraps each API call. On a `Throttling` or `RequestLimitExceeded` client error, or any `BotoCoreError`, it waits `retry_delay ** attempt` seconds and retries, up to `--max-retries` attempts. Other client errors are raised and logged, and that service is skipped for the Region.

### Result extraction

`_get_service_data` shapes each response based on `result_key`:

- A `result_key` that starts with `.` is compiled as a `jq` filter and applied to the full response.
- A plain `result_key` reads that top-level field from the response.
- With no `result_key`, the full response is returned with `ResponseMetadata` removed.

### Output

Each result is written as `output/<timestamp>/<region>/<service>-<function>.json`. The run timestamp is fixed when the process starts, so all files from one run share a directory. A log file, `aws_resources_<timestamp>.log`, is written to the output directory.

`DateTimeEncoder` serializes `datetime` values as ISO 8601 strings. There is no encoder for binary (`bytes`) values, so API operations that return binary data — such as `cloudtrail:ListPublicKeys` — can raise a serialization error. This is the cause of failures seen on some AWS GovCloud (US) scans.

### Organization scanning

`organization_scanner.py` runs from the management account:

1. `get_organization_accounts` pages through `organizations:ListAccounts` and keeps accounts with status `ACTIVE`.
2. `assume_role` calls `sts:AssumeRole` for `arn:aws:iam::<account-id>:role/<role-name>` to obtain a session in each account.
3. `scan_organization` runs `scan.py`'s `main` against each account, writing results under `output/organization-<timestamp>/<account-id>/`.

This lists accounts directly and does not walk the organizational unit (OU) tree, so OU structure does not affect which accounts are scanned.

## In-progress implementation: aws_auto_inventory package

The package reorganizes the same scanning logic into three layers. It is not yet complete.

### Layers

```text
Configuration layer  -->  Core scanning engine  -->  Output processor (planned)
```

#### Configuration layer (`aws_auto_inventory/config/`)

- `loader.py` (`ConfigLoader`) detects the file format from the extension and parses YAML or JSON into a `Config`.
- `models.py` defines Pydantic models: `Config`, `Inventory`, `AWSConfig`, `Sheet`, and `ExcelConfig`. This schema differs from `scan.py`: each inventory holds an `aws` block, a list of `sheets` (one per API call), and an `excel` block.
- `validator.py` (`ConfigValidator`) checks a loaded `Config` and returns a list of validation errors.

#### Core scanning engine (`aws_auto_inventory/core/`)

- `scan_engine.py` (`ScanEngine`) iterates the inventories in a `Config`, dispatching each to an account scan or an organization scan and collecting `ScanResult` objects.
- `region.py` (`RegionScanner`) scans the services in a Region concurrently with a thread pool.
- `service.py` (`ServiceScanner`) scans one service through `AWSClient`. `ResourceFilter` in the same module is a placeholder that currently returns results unchanged.
- `organization.py` (`OrganizationScanner`) lists active accounts with `organizations:ListAccounts` and assumes a role per account — the same approach as `organization_scanner.py`, with no OU traversal.
- `aws_client.py` (`AWSClient`) calls AWS APIs with retry and result extraction, including the same plain-key and `jq`-filter handling as `scan.py`.

#### Output processor (planned, not present)

`cli.py` imports `from .output.processor import OutputProcessor`, but the `aws_auto_inventory/output/` package does not exist in the repository. Because the import runs at module load, the `aws-auto-inventory` console script fails before it can scan or write output. JSON and Excel output generation remain to be implemented.

### Command-line interface (`aws_auto_inventory/cli.py`)

The CLI parses arguments (`--config`, `--output-dir`, `--format`, `--max-regions`, `--max-services`, `--max-retries`, `--retry-delay`, `--log-level`, `--validate-only`), loads and validates the configuration, checks credentials per inventory, runs the `ScanEngine`, and hands results to the output processor. The missing output module prevents the command from running end to end.

### Configuration schema

The package configuration is an `inventories` list. Each inventory names an `aws` block, a `sheets` list, and an optional `excel` block.

```yaml
inventories:
  - name: my-aws-inventory
    aws:
      profile: default
      region:
        - us-east-1
        - us-west-2
      organization: false
      role_name: OrganizationAccountAccessRole
    excel:
      transpose: true
    sheets:
      - name: EC2Instances
        service: ec2
        function: describe_instances
        result_key: Reservations
      - name: S3Buckets
        service: s3
        function: list_buckets
        result_key: Buckets
```

## Design decisions

- **Scan files map directly to boto3 calls.** A scan entry is a service name, a client method, optional parameters, and an optional result key. This keeps the tool generic across every AWS service without per-service code.
- **Concurrency is bounded but optional.** Region and service scanning use thread pools you can cap, trading throughput against API rate limits.
- **Retries target rate limiting.** Backoff is applied to throttling and transient `BotoCoreError` conditions; other errors fail fast and are logged.
- **Organization scanning is account-flat.** Accounts come from `organizations:ListAccounts`, not from OU traversal, so every active account is in scope regardless of OU placement.
- **The package rewrite is layered.** Configuration, scanning, and output are separated so that YAML support, validation, and additional output formats can evolve independently. The output layer is the remaining gap.
