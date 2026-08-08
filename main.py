import os
import re
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def parse_aff3ct_file(file_path):
    """Parses an AFF3CT results file and extracts Eb/N0, BER, and FER."""
    ebn0, ber, fer = [], [], []
    number_pattern = re.compile(
        r"[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?"
        )
    
    if not os.path.exists(file_path):
        print(f"Warning: File not found -> {file_path}")
        return None
        
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("#") or not line:
                continue
                
            numbers = number_pattern.findall(line)
            if len(numbers) >= 7:
                try:
                    ebn0.append(float(numbers[1]))  # Eb/N0
                    ber.append(float(numbers[5]))   # BER
                    fer.append(float(numbers[6]))
                except ValueError:
                    continue
    return ebn0, ber, fer

# --- CONFIGURATION ---
# List all your AFF3CT text files here
results_files = [
    "k4096_r12_BF_MWBF_results.txt",
    "k4096_r12_BP_F_SPA_results.txt",
    "k4096_r12_BP_HL_OMS_results.txt",
    "k4096_r23_BF_MWBF_results.txt",
    "k4096_r23_BP_F_SPA_results.txt",
    "k4096_r23_BP_HL_OMS_results.txt",
    "k4096_r45_BF_MWBF_results.txt",
    "k4096_r45_BP_F_SPA_results.txt",
    "k4096_r45_BP_HL_OMS_results.txt"
]
algorithms = [
    r'MWBF with rate $\frac{1}{2}$',
    r'SPA with rate $\frac{1}{2}$',
    r'OMS with rate $\frac{1}{2}$',
    r'MWBF with rate $\frac{2}{3}$',
    r'SPA with rate $\frac{2}{3}$',
    r'OMS with rate $\frac{2}{3}$',
    r'MWBF with rate $\frac{4}{5}$',
    r'SPA with rate $\frac{4}{5}$',
    r'OMS with rate $\frac{4}{5}$'
]
linestyles = [
    '-',
    '--',
    '-.',
    '-',
    '--',
    '-.',
    '-',
    '--',
    '-.'
]

colors = [
    'tab:blue',
    'tab:orange',
    'tab:green',
    'tab:blue',
    'tab:orange',
    'tab:green',
    'tab:blue',
    'tab:orange',
    'tab:green'
]

fig, (ax_ber, ax_fer) = plt.subplots(1, 2, figsize=(16, 7), sharex=True)

# Loop through each file and plot it on the same graph
for i, file_path in enumerate(results_files):
    data = parse_aff3ct_file(file_path)
    if data is None:
        continue
        
    ebn0, ber, fer = data
    
    # Use the file name as the label in the legend
    label_name = algorithms[i]
    
    # Plot Bit Error Rate (BER) with a solid line
    ax_ber.semilogy(ebn0, ber, linestyle=linestyles[i], label=f'{label_name}', color=colors[i])
    ax_fer.semilogy(ebn0, fer, linestyle=linestyles[i], label=f'{label_name}', color=colors[i])
    

# --- Y-AXIS & GRAPH FORMATTING ---
for ax in [ax_ber, ax_fer]:
    # Force the Y-axis to display numbers explicitly in scientific math notation
    ax.yaxis.set_major_formatter(ticker.LogFormatterMathtext())
    ax.yaxis.set_minor_formatter(ticker.LogFormatterMathtext())
    
    # Apply global configurations
    ax.set_xlabel(r'$E_b/N_0$ (dB)', fontsize=24)
    ax.grid(True, which="both", linestyle="--", alpha=1)
    ax.legend(loc="lower left", fontsize=16)

# Specific Y-labels for each subplot
ax_ber.set_ylabel('Bit Error Rate (BER)', fontsize=24)
ax_fer.set_ylabel('Frame Error Rate (FER)', fontsize=24)

# Display the final composite graph
plt.tight_layout(w_pad=4.0)
plt.show()