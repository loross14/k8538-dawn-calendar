# numbers-1: slice-6 numbers vs the calendar reading (locked before computing)

Data (Weidner 1915, sector 5 = King slice 6): 22 22 20 40 [4]0 | rotated: 40 40 40.
Main test uses all 8; a secondary run drops the restored [4]0 (7 numbers).
Numbers are read as day counts.

Score for a value set V: S = mean over the numbers of the distance to the nearest value in V (days).
Null: 20,000 random sets of the same count, integers uniform 1..59 (one sexagesimal place), seed 20261029.
p(H) = share of random sets that score as well or better under H. Lower p = H explains these numbers
better than it explains random numbers; flexible (dense) value sets are penalized automatically.

Hypotheses:
- EIGHTHS: {45.66, 22.83} (year/8, year/16)
- MONTHS: {29.53, 14.77} (synodic month, half month)
- STAR GAPS: day gaps between consecutive heliacal risings, over the whole year, of the locked bright-star list
- CALENDAR: the same gaps restricted to slice 6 of the fitted calendar: gaps between consecutive heliacal
  risings inside slice 6's 45-degree solar window, plus window start -> first rising and last rising -> window end.

Calendar fit: Weidner cribs (Mirach -> slice 2; Betelgeuse, Rigel, Bellatrix, Alnilam -> 4; Alhena, Alzirr -> 5),
heliacal_drag geometry (angle = Sun longitude at heliacal rising + rotation, direction +1, slice s = [45(s-1), 45s)),
rotation = midpoint of the zero-miss rotations (2-degree grid). Epoch 700 BCE, Nineveh, heliacal_drag atmosphere/observer.

Bright-star list (locked): Sirius Arcturus Vega Capella Rigel Procyon Betelgeuse Altair Aldebaran Antares Spica
Pollux Fomalhaut Deneb Regulus Adhara Castor Shaula Bellatrix Elnath Alnilam Alnitak Mirach Hamal Markab.
Stars with no heliacal rising are dropped and reported.

HIT only if p(CALENDAR) < 0.05 AND p(CALENDAR) is lower than each of EIGHTHS, MONTHS, STAR GAPS.
Anything else is reported as no hit, with whichever explanation scores best named.
