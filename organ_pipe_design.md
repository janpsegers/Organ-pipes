Frequency determines the length

L = 1000 * 343 / (4 * f) in mm
Mh_open = 550 / 2^ln(f)
Mh_closed = [3.018 - 0.233 * ln(f)]^5

Cylindrical pipe

The length and the normal scaling of the diameter:

DIA(n) = SD / [2^((n - 1)/(HN - 1))]

How to build pipe organ robots
http://www.rwgiangiulio.com/math/wst.htm

D = 156 / 2^[(m + st - 36)/(ht - 1)]
Area = pi * 0.5 * D * 0.5 * D

Where:
- m is MIDI note number
- st = semitone deviation from normal
- ht = number of semitones per halving of the diameter

Mouth width (standard: 0.25 * D)
W = frac * circumference
W = D * pi * frac

Square pipe

The mouth width was calculated above. For rectangular pipes, that's the width of the front.
The cross-sectional area is the same as for a comparable round pipe.
From that, the depth follows:

Area = width * depth
      = D * pi * frac * depth
Depth = area / (D * pi * frac)
      = (pi * 0.5 * D * 0.5 * D) / (D * pi * frac)
      = 0.5 * 0.5 * D / frac
Depth = 0.25 * D / frac

Check

Rectangular Area = 0.25 * D * D * pi * frac / frac
                 = pi * (D / 2)^2

A0 = 27.5 Hz → n = 21

f(n) = 2^((n - 21) / 12) * 27.5

Mensur Scaling Examples

- Viole d'orchestre (thin, mordant string stop): 35.6 mm [-10 ht]
- Salicional (broader-toned, non-imitative string stop): 40.6 mm [-7 ht]
- Violin diapason (thin-toned principal stop): 46.2 mm [-4 ht]
- Principal (typical mid-scale principal stop): 50.4 mm [-2 ht]
- Normalmensur: 54.9 mm [+/-0 ht]
- Open diapason (broader-toned principal stop): 57.4 mm [+1 ht]
- Gedeckt (thin-toned flute stop): 65.4 mm [+4 ht]
- Flûte à cheminée (typical mid-scale flute stop): 74.4 mm [+7 ht]
- Flûte ouverte (broader-toned flute stop): 81.1 mm [+9 ht]

http://www.fonema.se/violpip/violpip.htm

Ising's Formula
by Johan Liljencrants
e-mail:  johan@speech.kth.se

How big a mouth in a flue pipe?
I had the luck to stumble on the wisdom of Hartmuth Ising (1971) when my interest in pipes started some 20 years ago. He did a lot of research on the jet mechanism in the flue pipe, including flow visualizations. This particular work was published in German in an extremely arcane publication. So it is no wonder it is never cited and probably not even known by all that should. Among other things it tells how to select the proper dimensions in the mouth area and how to estimate the sound power.

First the dimensions and constants we are talking about:

- H [m]: height of the cut-up, the distance the air jet travels across the mouth
- D [m]: thickness of the base of the jet, the small dimension of the flue
- W [m]: width of the mouth, the large dimension of the flue, usually somewhat less than the pipe diameter
- F [Hz]: fundamental frequency of the pipe
- P [Pa=N/m²]: blowing pressure
- V [m/s]: initial velocity of the jet
- rho [kg/m³]: air density (1.2 kg/m³ under normal conditions)

You can use other consistent unit systems than SI, for instance cgs, but beware of peculiar additional constants if you try to drag in any inches.

Bernoulli's law gives:

V = sqrt(2 * P / rho)  [m/s]

Air consumption rate:

Q = V * W * D  [m³/s]

Intonation number (Ising):

I = sqrt(2 * P * D / (rho * H³)) / F

- I should be more than 2 but less than 3
- With I = 2 you get maximum efficiency
- With higher values, stronger harmonics
- If I > 3, the pipe may overblow

(If you add a frein, you can stretch it.)

If you want to change the blowing pressure P of an already working pipe, the logical adjustment is to change D in inverse proportion, assuming you want to keep H, F, and voicing the same.

The width W does not affect I, but it does affect sound power and air consumption.

Why this formula is obscure:
Pipe makers rarely start from scratch — they use traditional tables and empirical knowledge. Ising's formula puts hard numbers to vague traditional voicing advice, such as in:

- Audsley: The Art of Organ Building
- Monette: The Art of Organ Voicing

Reference:
Ising H: Erforschung und Planung des Orgelklanges.
Walcker Hausmitteilung no. 42, June 1971, pp. 38–57.
