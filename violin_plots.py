#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def main():
    df = pd.read_csv("../FP_moi15_thresho20_60k_-celltype_default.csv")
    df["topic"] = df["response_id"].str.extract("X(\d+)").astype(int)
    os.makedirs("analysis_results/gene_violin_plots", exist_ok=True)
    for gene in df["grna_target"].unique():
        plt.figure(figsize=(12, 6))
        gene_data = df[df["grna_target"] == gene]
        sns.violinplot(data=gene_data, x="topic", y="log_2_fold_change", color="skyblue")
        sig_data = gene_data[gene_data["significant"]]
        if len(sig_data) > 0:
            plt.scatter(sig_data["topic"]-1, sig_data["log_2_fold_change"], color="red", label="Significant")
        plt.title(f"Effects of {gene} Perturbation")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f"analysis_results/gene_violin_plots/{gene}_violin.pdf")
        plt.close()
        print(f"Generated plot for {gene}")

if __name__ == "__main__":
    main()
