import skrf as rf
import numpy as np
import matplotlib.pyplot as plt

# Load the network
network = rf.Network(r"D:\Cornell\Research\Device Modelling\20250122_WINMAY24_LUKEHRL\CG_4X25_VD0_VGN0P5.s2p")
coldfet = rf.Network(r"D:\Cornell\Research\Device Modelling\20250122_WINMAY24_LUKEHRL\CG_4X25_VD0_VGN1P5.s2p")

# Step 1 - S to Z for Extrinsic Inductances
z_parameters = network.z
freq = network.frequency.f * 2 * np.pi  # Angular frequency

# Compute extrinsic inductances
Ls = np.abs(np.imag(z_parameters[:, 0, 1])) / freq       # Shared source inductance
Lg = np.abs(np.imag(z_parameters[:, 0, 0])) / freq - Ls  # Gate inductance
Ld = np.abs(np.imag(z_parameters[:, 1, 1])) / freq - Ls  # Drain inductance

z_parameters[:, 0, 0] -= 1j * freq * Lg
z_parameters[:, 1, 1] -= 1j * freq * Ld

network2 = rf.Network(frequency=network.frequency, z0=50)
network2.z = z_parameters

# Step 2 - Z to Y for Extrinsic Capacitances

cold_z = coldfet.z
cold_z[:, 0, 0] -= 1j * freq * Lg
cold_z[:, 1, 1] -= 1j * freq * Ld

cold_z2 = rf.Network(frequency=network.frequency, z0=50)
cold_z2.z = cold_z

cold_y = cold_z2.y
Cb = -np.imag(cold_y[:, 0, 1]) / freq
Cpg = (np.imag(cold_y[:, 0, 0]) / freq) - 2 * Cb
Cpd = (np.imag(cold_y[:, 1, 1]) / freq) - Cb

# Update network with subtracted extrinsic capacitances
y_parameters = network2.y
y_parameters[:, 0, 0] -= 1j * freq * Cpg
y_parameters[:, 1, 1] -= 1j * freq * Cpd

network3 = rf.Network(frequency=network.frequency, z0=50)
network3.y = y_parameters

# Step 3 - Y to Z for Extrinsic Resistances
z_parameters2 = network3.z
Rsrd = 0.005 # CHANGE RS + RD VALUE ##
n = 2.92  ## CHANGE IDEALITY FACTOR ## 
Ig = 0.9e-8 ## CHANGE GATE CURRENT ##

Rc = np.real(z_parameters[:, 1, 1]) - Rsrd
Rs = np.real(z_parameters[:, 0, 1]) + Rc / 2

Rdy = (n * (1.38e-23) * 300) / Ig  # nkT/q * Ig
Rg = np.real(z_parameters[:, 0, 0]) - Rs - Rc / 3 - Rdy
Rg = abs(Rg)
Rd = np.real(z_parameters[:, 1, 1]) - Rs - Rc
Rd = abs(Rd)

z_parameters2[:, 0, 0] -= Rs + Rg + (1j * freq * Ls)
z_parameters2[:, 0, 1] -= Rs + (1j * freq * Ls)
z_parameters2[:, 1, 0] -= Rs + (1j * freq * Ls)
z_parameters2[:, 1, 1] -= Rs + Rd + (1j * freq * Ls)

intrinsic = rf.Network(frequency=network.frequency, z0=50)
intrinsic.z = z_parameters2

################################################################################
####################   AVERAGE CALCULATIONS  ###################################
################################################################################

low_freq_range = (network.frequency.f >= 20e9) & (network.frequency.f <= 40e9)
high_freq_range = (network.frequency.f >= 110e9) & (network.frequency.f <= 170e9)
avg_Ls =  abs(np.mean(Ls[high_freq_range]))
avg_Lg =  abs(np.mean(Lg[high_freq_range]))
avg_Ld =  abs(np.mean(Ld[high_freq_range]))
avg_Cb =  abs(np.mean(Cb[low_freq_range]))
avg_Cpg = abs( np.mean(Cpg[low_freq_range]))
avg_Cpd = abs( np.mean(Cpd[low_freq_range]))
avg_Rs =  abs(np.mean(Rs[low_freq_range]))
avg_Rg =  abs(np.mean(Rg[low_freq_range]))
avg_Rd =  abs(np.mean(Rd[low_freq_range]))

# Print averages
print("Average Extrinsic Parameters around Stable Portions (usually 110-170GHz):")
print(f"Ls: {avg_Ls:.3e} H")
print(f"Lg: {avg_Lg:.3e} H")
print(f"Ld: {avg_Ld:.3e} H")
print(f"Cb: {avg_Cb:.3e} F")
print(f"Cpg: {avg_Cpg:.3e} F")
print(f"Cpd: {avg_Cpd:.3e} F")
print(f"Rs: {avg_Rs:.3f} Ohms")
print(f"Rg: {avg_Rg:.3f} Ohms")
print(f"Rd: {avg_Rd:.3f} Ohms")