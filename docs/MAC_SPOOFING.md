# MAC Spoofing Notes

MAC spoofing is an operating-system/network-interface task. It is not implemented as a scanner runtime feature in this repository.

## What This Means for This Project

- There is no scanner flag like `--stealth` or `--proxies` in current scanner entrypoints.
- Changing MAC address must be done externally (OS tools, admin privileges).
- For local mock-target training (`localhost`), MAC spoofing is generally irrelevant.

## Scope Clarification

- MAC addresses are local-network identifiers.
- They usually do not propagate beyond your first network hop/router.
- Internet-facing services typically identify your source IP and higher-layer fingerprints, not your MAC.

## If You Still Need MAC Spoofing

Use your platform-native tooling outside this project, then run scanner commands normally, for example:

```bash
python autonomous_scan.py https://authorized-target.example --depth 20 --intensity 3
```

## Recommended Focus Instead

For reliable scanner improvements, prioritize:

- better training checkpoints
- depth/intensity tuning
- manual validation workflow
- authorized target scoping and governance

## Legal Reminder

Only run this scanner on systems you are authorized to test.
