#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import gzip

def parse_args():
    p = argparse.ArgumentParser(
        description="Remove self-hits, canonicalize BLAST pairs, and sort for ANI/AF calculation"
    )
    p.add_argument("--input", required=True,
                   help="Input BLAST TSV")
    p.add_argument("--output", required=True,
                   help="Output sorted TSV.gz")
    return p.parse_args()

def log(msg):
    print(f"[INFO] {msg}", flush=True)

def main():
    args = parse_args()

    log(f"Reading input BLAST TSV from {args.input}")

    records = []

    with open(args.input) as fin:
        for i, line in enumerate(fin, 1):

            parts = line.rstrip("\n").split("\t")

            # Expected BLAST format:
            # qseqid sseqid pident length qstart qend sstart send

            if len(parts) < 8:
                log(f"[WARN] Skipping malformed line {i}")
                continue

            q = parts[0]
            s = parts[1]

            # Remove self hits
            if q == s:
                continue

            # Canonicalize pair
            if q <= s:
                a, b = q, s

            else:
                a, b = s, q

                # Swap original IDs
                parts[0], parts[1] = parts[1], parts[0]

                # Swap coordinates
                parts[4], parts[6] = parts[6], parts[4]
                parts[5], parts[7] = parts[7], parts[5]

            records.append((a, b, parts))

    log(f"Total valid pairs collected: {len(records)}")

    log("Sorting canonical pairs")
    records.sort(key=lambda x: (x[0], x[1]))

    log(f"Writing sorted output to {args.output}")

    with gzip.open(args.output, "wt") as fout:

        for a, b, parts in records:

            # Output format:
            # A B qseqid sseqid pident length qstart qend sstart send

            fout.write(
                "\t".join([a, b] + parts) + "\n"
            )

    log("Done.")

if __name__ == "__main__":
    main()