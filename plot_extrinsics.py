import skrf as rf
import numpy as np
import matplotlib.pyplot as plt

## INSERT ZERO DRAIN BIAS S-PARAMETER HERE ##
network = rf.Network(r"D:\Cornell\Research\Device Modelling\20250122_WINMAY24_LUKEHRL\CG_4X25_VD0_VGN0P5.s2p")

plt.figure(1)
plt.title('Raw measurements')
plt.xlabel('Frequency (GHz)')
plt.ylabel('S-parameters (dB)')
plt.legend()
plt.grid(True)
network.plot_s_db(0, 0)
network.plot_s_db(0, 1)
network.plot_s_db(1, 0)
network.plot_s_db(1, 1)

# Step 1 - S to Z for Extrinsic Indutances
z_parameters = network.z

freq = network.frequency.f * 2 * np.pi # w, angular frequency

Ls = np.abs(np.imag(z_parameters[:,0,1]) ) / freq       # z12 - jw*Ls, shared source inductance parasitic
Lg = np.abs(np.imag(z_parameters[:,0,0]) ) / freq - Ls  # z11 - jw*(Lg+Ls)
Ld = np.abs(np.imag(z_parameters[:,1,1]) ) / freq - Ls  # z22 - jw*(Ld+Ls)

z_parameters[:,0,0] -= 1j * freq * Lg
z_parameters[:,1,1] -= 1j * freq * Ld

network2 = rf.Network(frequency=network.frequency, z0=50)
network2.z = z_parameters

# Step 2 - Z to Y for Extrinsic Capacitances

# Need to determine accurate Cpg and Cpd first. ## INSERT COLD FET S-PARAMETER HERE ##
coldfet = rf.Network(r"D:\Cornell\Research\Device Modelling\20250122_WINMAY24_LUKEHRL\CG_4X25_VD0_VGN1P5.s2p")

cold_z = coldfet.z

cold_z[:,0,0] -= 1j * freq * Lg
cold_z[:,1,1] -= 1j * freq * Ld

cold_z2 = rf.Network(frequency=network.frequency, z0=50)
cold_z2.z = cold_z

cold_y = cold_z2.y

Cb = -np.imag(cold_y[:,0,1]) / freq
Cpg = (np.imag(cold_y[:,0,0]) / freq) - 2*Cb
Cpd = (np.imag(cold_y[:,1,1]) / freq) - Cb

# Go back to previous network 2 and subtract Cpg Cpd from it
y_parameters = network2.y
y_parameters[:,0,0] -= 1j * freq * Cpg
y_parameters[:,1,1] -= 1j * freq * Cpd

network3 = rf.Network(frequency=network.frequency, z0=50)
network3.y = y_parameters

# Step 3 - Y back to Z for Extrinsic Resistances
z_parameters2 = network3.z

Rsrd = 0.005 # CHANGE RS + RD VALUE ##
n = 2.92  ## CHANGE IDEALITY FACTOR ## 
Ig = 0.9e-8 ## CHANGE GATE CURRENT ##

Rc = np.real(z_parameters[:,1,1]) - Rsrd
Rs = np.real(z_parameters[:,0,1]) + Rc/2

Rdy = (n*(1.38e-23)*300)/Ig  # nkT/q*Ig
Rg = np.real(z_parameters[:,0,0]) - Rs - Rc/3 - Rdy
Rg = abs(Rg)
Rd = np.real(z_parameters[:,1,1]) - Rs - Rc
Rd = abs(Rd)

z_parameters2[:,0,0] = z_parameters2[:,0,0] - Rs - Rg - (1j * freq * Ls)
z_parameters2[:,0,1] = z_parameters2[:,0,1] - Rs - (1j * freq * Ls)
z_parameters2[:,1,0] = z_parameters2[:,1,0] - Rs - (1j * freq * Ls)
z_parameters2[:,1,1] = z_parameters2[:,1,1] - Rs - Rd - (1j * freq * Ls)

intrinsic = rf.Network(frequency=network.frequency)
intrinsic.z = z_parameters2

z0_array = np.full_like(network.frequency.f, 50)
intrinsic.z0 = z0_array

intrinsic_y = intrinsic.y
intrinsic_s = intrinsic.s

# Plot
# Plotting inductances
plt.figure(3)
plt.plot(network.frequency.f/1e9, Ls, label='Ls')
plt.plot(network.frequency.f/1e9, Lg, label='Lg')
plt.plot(network.frequency.f/1e9, Ld, label='Ld')
plt.xlabel('Frequency (GHz)')
plt.ylabel('Inductance (H)')
plt.legend()
plt.title('Extrinsic Inductances')
plt.grid(True)


# Plotting capacitances
plt.figure(4)
plt.plot(network.frequency.f/1e9, Cb, label='Cb')
plt.plot(network.frequency.f/1e9, Cpg, label='Cpg')
plt.plot(network.frequency.f/1e9, Cpd, label='Cpd')
plt.xlabel('Frequency (GHz)')
plt.ylabel('Capacitance (F)')
plt.legend()
plt.title('Extrinsic Capacitances')
plt.grid(True)


# Plotting resistances
plt.figure(5)
plt.plot(network.frequency.f/1e9, Rs, label='Rs')
plt.plot(network.frequency.f/1e9, Rg, label='Rg')
plt.plot(network.frequency.f/1e9, Rd, label='Rd')
plt.plot(network.frequency.f/1e9, Rc, label='Rc')
plt.xlabel('Frequency (GHz)')
plt.ylabel('Resistance (Ohms)')
plt.legend()
plt.title('Extrinsic Resistances')
plt.grid(True)

plt.show()