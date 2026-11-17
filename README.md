# Crayvir-2 Snakemake pipeline

A Snakemake workflow for (RNA) virus detection in metagenomic data from various samples (invertebrate, plants, environmental samples). This workflow is based on the workflow from: https://github.com/LanaVogrinec/snakemake-PHEW_water created by Lana Vogrinec: https://github.com/LanaVogrinec

## Workflow

### Per-sample processing

1. Trim paired-end reads with Trimmomatic to remove adapters and low-quality bases. The workflow uses the paired reads in downstream steps.
2. Assemble the trimmed reads with RNAviralSPAdes.
3. Add the sample name to each contig identifier.
4. Retain contigs that are at least 500 bp long.
5. Classify contigs with MMseqs2 against the NR nucleotide database and write the taxonomy results to a TSV file.
6. Extract contigs whose taxonomy lineage places them under **Viruses**, along with their taxonomy records.

### Combined viral-contig analysis

1. Combine the viral contigs and taxonomy records from all samples.
2. Run an all-against-all BLASTn search on the combined viral contigs.
3. Sort the BLASTn results and remove self-hits.
4. Filter contig pairs to retain those with at least 90% ANI and an alignment fraction of at least 80% of the shorter contig.
5. Cluster contigs using the filtered similarity edges and produce cluster assignments and statistics.
6. Add taxonomy information to the cluster assignments.
7. Select the longest contig in each cluster as its representative.

### Per-sample mapping and quantification

1. Map each sample's trimmed paired-end reads to the cluster representatives with BBMap, using a minimum identity of 90%.
2. Filter alignments with CoverM, requiring at least 95% read identity and at least 95% of each read aligned. CoverM reports per-contig read counts, TPM, RPKM, covered bases, and covered fraction.

### Across-sample summaries

1. Combine the per-sample read counts and coverage measurements into sample-by-contig tables.
2. Set counts to zero for a sample/contig pair if it has fewer than 2 reads, less than 0.25 covered fraction, or fewer than 400 covered bases.
3. Calculate TPM from the filtered counts.
4. Calculate each representative's percentage of a sample's reads using the filtered count and the total reads in both trimmed FASTQ files.

## Requirements and setup

### Software

- A Linux environment with Bash and Conda (or Mamba).
- A Conda environment named `snakemake` with Snakemake installed. If you need to create it:

  ```bash
  conda create -n snakemake -c conda-forge -c bioconda snakemake
  ```

The launcher runs Snakemake from this environment and enables the workflow's per-rule Conda environments, so you do not need to install each workflow tool separately.

### Configuration and input files

- The sample sheet is specified in `config/config.yaml`. By default, it is `config/samples.tsv` and must contain a `sample` column.
- For each sample listed in the sample sheet, provide paired-end reads named `resources/<sample>_1.fq.gz` and `resources/<sample>_2.fq.gz`.
- Provide the Trimmomatic adapter file at `resources/TruSeq3-PE.fa`.
- The MMseqs2 NR nucleotide database must be accessible at `/biodbs/mmseqs2/nr_database/nr.fnaDB`, as specified in the workflow.

The workflow expects these input files and the database to be accessible; it does not download them.

The launcher defaults to `/proj/etools/conda/bin/conda`. If Conda is installed elsewhere, set `CONDA_EXE` when running it:

```bash
CONDA_EXE=/path/to/conda ./run_snakemake.sh --cores 1 --dry-run
```

## Running the pipeline

From the project root, first perform a dry run to check the workflow plan without executing jobs:

```bash
./run_snakemake.sh --cores 1 --dry-run
```

If the plan looks correct, run the pipeline. Replace `8` with the number of cores you want Snakemake to use:

```bash
./run_snakemake.sh --cores 8 -k -p
```

The `-k` option lets independent jobs continue if a job fails. The `-p` option prints the commands Snakemake runs. The launcher also enables the workflow's per-rule Conda environments.

To run the workflow in a `screen` session:

```bash
screen -S virocray
./run_snakemake.sh --cores 8 -k -p
```

Detach from the session with `Ctrl-a` followed by `d`. Reconnect later with:

```bash
screen -r virocray
```

## Outputs

All workflow outputs are written under `results/`.

### Viral contig clustering

Key files in `results/merged/` include:

- `blastn_pairs.tsv`: all-against-all BLASTn results.
- `blastn_pairs_sorted_no_self_filtered.tsv`: filtered contig-pair similarities.
- `edges_filtered.tsv`: similarity edges used for clustering.
- `clusters.tsv` and `clusters_stats.tsv`: cluster assignments and summary statistics.
- `clusters_with_taxonomy.tsv`: cluster assignments combined with taxonomy.
- `cluster_representatives.fasta`: the longest representative contig from each cluster.
- `cluster_representatives_list.tsv` and `cluster_representatives_stats.tsv`: representative metadata and summary statistics.

### Read mapping and abundance

- Per-sample mapping BAMs, indexes, and CoverM tables are written under `results/<sample>/`. CoverM tables report read counts, TPM, RPKM, covered bases, and covered fraction for each representative.
- `reps_read_counts_samples.tsv`, `reps_covered_bases_samples.tsv`, and `reps_covered_fraction_samples.tsv` contain the corresponding measurements combined across samples.
- `reps_read_counts_samples_filtered.tsv` contains counts after the read-count and coverage filters; `reps_read_counts_samples_filtered_stats.tsv` summarizes the filtering.
- `reps_tpm_samples_filtered.tsv` contains TPM values calculated from the filtered counts.
- `reps_read_count_percentage_samples_filtered.tsv` contains each representative's read count as a percentage of the total reads in each sample.



