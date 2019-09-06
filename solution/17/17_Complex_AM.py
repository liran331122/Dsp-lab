import pyaudio
import struct
import wave
import math
from matplotlib import pyplot as plt
import numpy as np
from scipy import signal as sg
f0 = 1000    # 'Duck' audio
BLOCKSIZE = 1024      # Number of frames per block
CHANNELS = 1
WIDTH = 2
RATE = 16000
T = 10 # duration 10 seconds
N = T * RATE

K = 7
[b_lpf, a_lpf] = sg.ellip(K, 0.2, 50, 0.48)
# I = np.sqrt(-1)
s = [1j**n for n in range(K+1)]
b1 = [0 for n in range(K+1)]
a1 = [0 for n in range(K+1)]
for n in range(0,K+1):
    b1[n] = b_lpf[n] * s[n]
    a1[n] = a_lpf[n] * s[n]
f = [n*float(RATE)/BLOCKSIZE for n in range(BLOCKSIZE)]

plt.ion()
# DBscale = True
plt.figure(1)

plt.subplot(3,1,1)
plt.xlim(0, 0.5*RATE)
plt.ylim(0, 150)
plt.xlabel('frequency (Hz)')
line1, =plt.plot([],[],color = 'red')
line1.set_xdata(f)

plt.subplot(3,1,3)
plt.xlim(0, 0.5*RATE)
plt.ylim(0, 150)
plt.xlabel('frequency (Hz)')
line2, =plt.plot([],[],color = 'blue')
line2.set_xdata(f)

# Open audio stream
p = pyaudio.PyAudio()
stream = p.open(
    format      = p.get_format_from_width(WIDTH),
    channels    = CHANNELS,
    rate        = RATE,
    input       = True,
    output      = True)


# Create block (initialize to zero)
output_block = [0 for n in range(0, BLOCKSIZE)]

# Number of blocks in wave file
num_blocks = int(math.floor(N/BLOCKSIZE))
states = np.zeros(K)
print('* Playing...')

# Initialize phase
# om = 2*math.pi*f0/RATE
# theta = 0

# Go through wave file 
for i in range(0, num_blocks):

    # Get block of samples from wave file
    input_string = stream.read(BLOCKSIZE,exception_on_overflow = False)     # BLOCKSIZE = number of frames read

    # Convert binary string to tuple of numbers    
    input_tuple = struct.unpack('h' * BLOCKSIZE, input_string)
            # (h: two bytes per sample (WIDTH = 2))
    r, states = sg.lfilter(b1, a1, input_tuple, -1, zi = states)
    # Go through block
    for n in range(0, BLOCKSIZE):
        # Amplitude modulation  (f0 Hz cosine)
        # theta = theta + om
        output_block[n] = np.real(r[n] * np.e**(1j*2*math.pi*f0*(i*BLOCKSIZE+n)/RATE))
        # output_block[n] = ( input_tuple[n] * math.cos(theta) )
        # output_block[n] = input_tuple[n]  # for no processing
    
    # # keep theta betwen -pi and pi
    # while theta > math.pi:
    #     theta = theta - 2*math.pi
    inputf = np.fft.fft(input_tuple)
    outputf = np.fft.fft(output_block)

    line1.set_ydata(20*np.log10(abs(inputf)))
    line2.set_ydata(20*np.log10(abs(outputf)))
    # plt.title('Block {0:d}'.format(i))
    plt.pause(0.001)
    plt.draw()
    # Convert values to binary string
    output_string = struct.pack('h' * BLOCKSIZE, *output_block)

    # Write binary string to audio output stream
    stream.write(output_string)

print('* Finished')

stream.stop_stream()
stream.close()
p.terminate()

# # Close wavefile
# wf.close()

# Original file by Gerald Schuller, October 2013
