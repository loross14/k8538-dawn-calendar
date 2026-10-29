# numbers-2: base-60 rereading (locked before computing; follow-up to numbers-1, chosen after seeing it)

Logan, live: "these guys use base-60 math, so maybe you're reading it wrong."

Same 8 numbers (and the 7-number variant), same four value sets as numbers-1 (EIGHTHS, MONTHS, STAR GAPS,
CALENDAR; gaps taken from numbers-1 result.json).
Readings: cuneiform has no zero or radix point, so each number x may be read, independently, as
x/60, x or 60x days, or in time-degrees (1 day = 360 UŠ) as x/360, 60x/360 or x/21600 days.
Distance: |ln(reading / value)|, the best reading and nearest value for each number; score = mean over numbers.
Primary null: 20,000 random sets, integers uniform 1..59, given exactly the same reading freedom. Seed 20261030.
Secondary null (round-number check): same, but each number is a multiple of 10 (10..50) with probability 0.5.
HIT only if p(CALENDAR) < 0.05 and lowest of the four under the primary null.
Multiple testing: numbers-1 plus numbers-2 make 8 hypothesis tests; a result is a lead unless p < 0.00625.
