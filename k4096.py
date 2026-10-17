import os
import re

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np


# ============================================================
# Configuration
# ============================================================

TARGET_BER = 1e-4

# Theoretical uncoded BPSK performance over AWGN at BER = 10^-4.
UNCODED_BPSK_EBN0_AT_TARGET = 8.4  # dB, approximately

# Set this to False if you only want the horizontal BER target line.
SHOW_UNCODED_REFERENCE = True

RESULTS_FILES = [
    "k4096_r12_BF_MWBF_results.txt",
    "k4096_r12_BP_F_SPA_results.txt",
    "k4096_r12_BP_HL_OMS_results.txt",
    "k4096_r23_BF_MWBF_results.txt",
    "k4096_r23_BP_F_SPA_results.txt",
    "k4096_r23_BP_HL_OMS_results.txt",
    "k4096_r45_BF_MWBF_results.txt",
    "k4096_r45_BP_F_SPA_results.txt",
    "k4096_r45_BP_HL_OMS_results.txt",
]


ALGORITHMS = [
    r"MWBF with rate $\frac{1}{2}$",
    r"SPA with rate $\frac{1}{2}$",
    r"OMS with rate $\frac{1}{2}$",
    r"MWBF with rate $\frac{2}{3}$",
    r"SPA with rate $\frac{2}{3}$",
    r"OMS with rate $\frac{2}{3}$",
    r"MWBF with rate $\frac{4}{5}$",
    r"SPA with rate $\frac{4}{5}$",
    r"OMS with rate $\frac{4}{5}$",
]


LINESTYLES = [
    "-",   # rate 1/2
    "-",
    "-",
    "--",  # rate 2/3
    "--",
    "--",
    "-.",  # rate 4/5
    "-.",
    "-.",
]


COLORS = [
    "tab:blue",    # MWBF
    "tab:orange",  # SPA
    "tab:green",   # OMS
    "tab:blue",
    "tab:orange",
    "tab:green",
    "tab:blue",
    "tab:orange",
    "tab:green",
]


NUMBER_PATTERN = re.compile(
    r"[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?"
)


def parse_aff3ct_file(file_path):
    """Extract Eb/N0, BER, and FER columns from an AFF3CT output file."""

    ebn0 = []
    ber = []
    fer = []

    if not os.path.exists(file_path):
        print(f"Warning: file not found -> {file_path}")
        return None

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            # AFF3CT headers and blank lines do not contain result rows.
            if line.startswith("#") or not line:
                continue

            numbers = NUMBER_PATTERN.findall(line)

            # AFF3CT result rows contain:
            # Es/N0, Eb/N0, FRA, BE, FE, BER, FER, ...
            if len(numbers) < 7:
                continue

            try:
                current_ebn0 = float(numbers[1])
                current_ber = float(numbers[5])
                current_fer = float(numbers[6])
            except ValueError:
                continue

            if current_ber < 0 or current_fer < 0:
                continue

            ebn0.append(current_ebn0)
            ber.append(current_ber)
            fer.append(current_fer)

    return ebn0, ber, fer


def find_snr_at_target(ebn0, ber, target_ber):
    """Estimate Eb/N0 where a BER curve crosses target_ber.

    BER is interpolated in log10(BER), which is appropriate for a
    semilog BER plot. If a curve reaches BER=0, the next available SNR
    is returned as an upper-bound estimate.
    """

    if len(ebn0) < 2 or len(ber) < 2:
        return None, False

    target_log = np.log10(target_ber)

    for x1, y1, x2, y2 in zip(ebn0[:-1], ber[:-1], ebn0[1:], ber[1:]):
        # Exact target value.
        if y1 == target_ber:
            return x1, True
        if y2 == target_ber:
            return x2, True

        # Normal crossing from above the target to below it.
        if y1 > target_ber and 0 < y2 < target_ber:
            log_y1 = np.log10(y1)
            log_y2 = np.log10(y2)
            fraction = (target_log - log_y1) / (log_y2 - log_y1)
            return x1 + fraction * (x2 - x1), True

        # BER=0 means the measured BER is below the resolution of the
        # simulation. The crossing occurred somewhere before x2.
        if y1 > target_ber and y2 == 0:
            return x2, False

    return None, False


def main():
    fig, (ax_ber, ax_fer) = plt.subplots(
        1,
        2,
        figsize=(18, 7),
        sharex=True,
    )

    coding_gain_results = []

    for i, file_path in enumerate(RESULTS_FILES):
        data = parse_aff3ct_file(file_path)

        if data is None:
            continue

        ebn0, ber, fer = data

        if not ebn0:
            print(f"Warning: no result rows found -> {file_path}")
            continue

        label = ALGORITHMS[i]

        ax_ber.semilogy(
            ebn0,
            ber,
            linestyle=LINESTYLES[i],
            color=COLORS[i],
            linewidth=2,
            marker="o",
            markersize=4,
            label=label,
        )

        ax_fer.semilogy(
            ebn0,
            fer,
            linestyle=LINESTYLES[i],
            color=COLORS[i],
            linewidth=2,
            marker="o",
            markersize=4,
            label=label,
        )

        target_snr, exact_crossing = find_snr_at_target(
            ebn0,
            ber,
            TARGET_BER,
        )

        if target_snr is not None:
            coding_gain = UNCODED_BPSK_EBN0_AT_TARGET - target_snr

            coding_gain_results.append(
                (label, target_snr, coding_gain, exact_crossing)
            )

            # Mark the estimated BER=10^-4 crossing on the BER graph.
            ax_ber.plot(
                target_snr,
                TARGET_BER,
                marker="o",
                markersize=7,
                color=COLORS[i],
                markeredgecolor="black",
                zorder=5,
            )

    # --------------------------------------------------------
    # BER target and coding-gain reference lines
    # --------------------------------------------------------

    ax_ber.axhline(
        TARGET_BER,
        color="black",
        linestyle=":",
        linewidth=2,
        label=r"Target BER = $10^{-4}$",
        zorder=1,
    )

    if SHOW_UNCODED_REFERENCE:
        ax_ber.axvline(
            UNCODED_BPSK_EBN0_AT_TARGET,
            color="dimgray",
            linestyle="--",
            linewidth=2,
            label="Uncoded BPSK reference (8.4 dB)",
            zorder=1,
        )

    # Put labels directly beside the reference lines.
    # ax_ber.text(
    #     1.01,
    #     TARGET_BER,
    #     r"Target BER = $10^{-4}$",
    #     transform=ax_ber.get_yaxis_transform(),
    #     ha="left",
    #     va="bottom",
    #     color="black",
    #     fontsize=11,
    #     clip_on=False,
    #     bbox=dict(facecolor="white", alpha=0.01, edgecolor="none"),
    # )

    # if SHOW_UNCODED_REFERENCE:
    #     ax_ber.text(
    #         UNCODED_BPSK_EBN0_AT_TARGET,
    #         -0.01,
    #         "Uncoded BPSK reference (8.4 dB)",
    #         transform=ax_ber.get_xaxis_transform(),
    #         ha="left",
    #         va="top",
    #         color="black",
    #         fontsize=11,
    #         clip_on=False,
    #     )

    # --------------------------------------------------------
    # Axis formatting
    # --------------------------------------------------------

    for ax in (ax_ber, ax_fer):
        ax.yaxis.set_major_formatter(ticker.LogFormatterMathtext())
        ax.yaxis.set_minor_formatter(ticker.LogFormatterMathtext())
        ax.set_xlabel(r"$E_b/N_0$ (dB)", fontsize=20)
        ax.grid(True, which="both", linestyle="--", alpha=0.7)
        ax.tick_params(axis="x", which="both", pad=10)
        ax.tick_params(axis="both", labelsize=14)

    ax_ber.set_ylabel("Bit Error Rate (BER)", fontsize=20)
    ax_fer.set_ylabel("Frame Error Rate (FER)", fontsize=20)

    ax_ber.set_title("LDPC Bit Error Rate", fontsize=22)
    ax_fer.set_title("LDPC Frame Error Rate", fontsize=22)

    # Build one figure-level legend from the BER subplot.
    # One legend beside both plots, inside the figure boundary.
    handles, labels = ax_ber.get_legend_handles_labels()

    fig.legend(
            handles,
            labels,
            loc="center left",
            bbox_to_anchor=(0.80, 0.5),
            fontsize=14,
            frameon=False,
            markerscale=1.5,
            handlelength=3,
            labelspacing=0.8,
        )

    # Reserve the right side of the figure for the legend.
    plt.tight_layout(rect=[0, 0, 0.79, 1], w_pad=4.0)

    # --------------------------------------------------------
    # Print coding-gain estimates
    # --------------------------------------------------------

    print("\nEstimated performance at BER = 1e-4")
    print("Reference: uncoded BPSK Eb/N0 = 8.4 dB")
    print("-" * 72)

    if not coding_gain_results:
        print("No curves crossed BER = 1e-4 in the supplied SNR range.")
        print("Increase the maximum SNR used in the AFF3CT simulations.")
    else:
        for label, target_snr, coding_gain, exact_crossing in coding_gain_results:
            estimate_note = "" if exact_crossing else " (upper-bound estimate)"
            print(
                f"{label}: Eb/N0 = {target_snr:.3f} dB, "
                f"coding gain = {coding_gain:.3f} dB{estimate_note}"
            )
    # plt.legend()
    plt.show()


if __name__ == "__main__":
    main()