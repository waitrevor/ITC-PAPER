import os
import re
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def parse_aff3ct_file(file_path):
    """Parses an AFF3CT results file and extracts Eb/N0, BER, and FER."""
    ebn0, ber = [], []
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
                except ValueError:
                    continue
    return ebn0, ber

# --- CONFIGURATION ---
# List all your AFF3CT text files here
results_files = [
    "k4096_r45_BF_MWBF_results.txt",
    "k4096_r45_BP_F_SPA_results.txt",
    "k4096_r45_BP_HL_OMS_results.txt"
]
algorithms = [
    'MODIFIED WEIGHT BIT FLIPPING',
    'SUM PRODUCT ALGORITHM',
    'OFFSET MIN-SUM'
]

plt.figure(figsize=(10, 7))

# Loop through each file and plot it on the same graph
for i, file_path in enumerate(results_files):
    data = parse_aff3ct_file(file_path)
    if data is None:
        continue
        
    ebn0, ber = data
    print(ber)
    
    # Use the file name as the label in the legend
    label_name = algorithms[i]
    
    # Plot Bit Error Rate (BER) with a solid line
    plt.semilogy(ebn0, ber, linestyle='-', label=f'{label_name} (BER)')
    

# --- Y-AXIS & GRAPH FORMATTING ---
ax = plt.gca()

# Force the Y-axis to display numbers explicitly in scientific math notation
ax.yaxis.set_major_formatter(ticker.LogFormatterMathtext())
ax.yaxis.set_minor_formatter(ticker.LogFormatterMathtext())

# Clean up visual grid and labels
plt.xlabel('Eb/N0 (dB)', fontsize=12)
plt.ylabel('Bit Error Rate (BER)', fontsize=12)
# plt.title('AFF3CT Performance Comparison', fontsize=14, fontweight='bold')
plt.grid(True, which="both", linestyle="--", alpha=0.5)
plt.legend(loc="lower left", fontsize=10)

# Display the final composite graph
plt.tight_layout()
plt.show()