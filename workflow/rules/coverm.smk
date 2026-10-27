rule coverm:
    input:
        bam = RESULTS_DIR + "/{sample}/07_{sample}_bbmap_reps.bam",
        bai = RESULTS_DIR + "/{sample}/07_{sample}_bbmap_reps.bam.bai"
    output:
        tsv          = RESULTS_DIR + "/{sample}/08_{sample}_coverm_reps.tsv",
        filtered_bam = RESULTS_DIR + "/{sample}/08_{sample}_coverm_reps.bam",
        filtered_bai = RESULTS_DIR + "/{sample}/08_{sample}_coverm_reps.bam.bai",
        check        = RESULTS_DIR + "/{sample}/08_{sample}_coverm_reps.done"
    log:
        logO = "logs/coverm/{sample}.log"
    conda:
        "../envs/mapping_env.yaml"
    threads: 12
    shell:
        """
        coverm filter \
            --bam-files {input.bam} \
            --threads {threads} \
            --min-read-percent-identity 95 \
            --min-read-aligned-percent 95 \
            --output-bam-files {output.filtered_bam} \
            > {log.logO} 2>&1

        samtools index -o {output.filtered_bai} {output.filtered_bam} >> {log.logO} 2>&1

        coverm contig \
            --bam-files {output.filtered_bam} \
            --threads {threads} \
            --methods count tpm rpkm covered_fraction covered_bases \
            --output-file {output.tsv} \
            >> {log.logO} 2>&1

        touch {output.check}
        """
