# A Dawn Calendar in Eight Parts

**Measuring the Nineveh Planisphere (K 8538) with Cribs**, by Logan C. Ross, 29 October 2026.

Read it: [paper/paper.pdf](paper/paper.pdf), or online at [logan.engineering/essays/dawn-calendar-k8538](https://logan.engineering/essays/dawn-calendar-k8538).

## The result

Known identifications on K 8538 serve as cribs, in the cryptanalytic sense. Every published reading of the tablet is scored against random tablets under the same rules, and each rule is written and hashed before its run.

- **On identical cribs (Weidner's four):**

  | Reading | Random tablets fit as well |
  |---|---|
  | **Dawn calendar (heliacal rising)** | **2.0%** |
  | Koch's one-night horizon | 8.7% |
  | Weidner's ecliptic order | 10.0% |
  | The 1880 sunset horizon | 12.7% |

- **With a fifth crib, fixed by a prediction locked in advance and then passed** (Weidner's bird as the Raven, Corvus, in slice 6): **0.64%** of 10,000 random tablets. Stable at 0.48–0.71% from 1500 to 400 BCE.
- **With APIN as Triangulum,** all five cribs fall exactly in their slices: **0.48%**.

The tablet is read as an administrative calendar of eight 45-day periods within the 360-day administrative year. The purpose of the eight periods is unknown. The limits are in §8 of the paper. Two of them: about seven format variants were tried, and the Raven was added after its prediction passed (3.0% without it).

## Contents

| Path | What |
|---|---|
| `paper/` | `paper.tex` (XeLaTeX / tectonic, STIX Two Text) and `paper.pdf` |
| `figures/` | the six figures, `make_figures.py` that regenerates them, `figures.json` |
| `engine/` | `crib_drag.py` (crib geometry, miss function) and `heliacal_drag.py` (Swiss Ephemeris heliacal rising at Nineveh) |
| `runs/` | the locked rule files, the run scripts and their outputs (below) |

## Runs and their locked rules

| Run | Rules file | SHA-256 (prefix) | Script | Output |
|---|---|---|---|---|
| numbers-1: slice-6 numbers as day counts | `RULES.md` | `2eef8b0e` | `run.py` | `result.json` |
| numbers-2: base-60 rereading | `RULES-2.md` | `96b2a9a7` | `run2.py` | `result2.json` |
| predict-corvus-1: the Raven prediction | `RULES-3.md` | `94cc6f7e` | `predict.py` | in the paper, Figure 3 |
| final-crib-1: five cribs | `RULES-4.md` | `21246e2a` | `final.py` | `result-final.json` |
| astrolabe-crib-1: MUL.APIN dates (**withdrawn**, judged not a relevant test) | `RULES-5.md` | `aab97315` | `astrolabe.py` | `result-astrolabe.json` |
| robust-1: null size, epochs, leave-one-out, APIN identity | `RULES-6.md` | `814c1fe9` | `robust.py` | `result-robust.json` |
| meteor-date placement | — | — | `crib_dates.py` | in the paper, §6 |

**Table 1 of the paper** comes from the earlier patchwork run. Its script, `patchwork.py`, sits in the author's private ephemeris repository and is available on request.

## Reproduce

1. **Environment:**

   ```bash
   python3 -m venv venv && venv/bin/pip install pyswisseph==2.10.3.2 numpy matplotlib pillow
   ```

2. **Ephemeris files:** download the JPL DE441-based Swiss Ephemeris files for 4200 BCE – 1 CE (`seplm06–42.se1`, `semom06–42.se1`) from <https://github.com/aloistr/swisseph/tree/master/ephe> into a folder `ephe/`.
3. **Run:** from `engine/`, with the run scripts on the path, for example:

   ```bash
   venv/bin/python runs/robust.py engine ephe
   ```

   - Each script takes the engine directory and the ephemeris directory as arguments.
   - `robust.py` writes `result-robust.json` to the working directory.
4. **Figures:**

   ```bash
   venv/bin/python figures/make_figures.py engine ephe <King 1912 plate 10 scan> runs/result-robust.json figures/
   ```

   The plate is King, *CT* 33, pl. 10 (public domain; archive.org).

## Licence

- **Paper and figures:** [CC BY 4.0](LICENSE-paper).
- **Code:** [MIT](LICENSE).

## Cite

Ross, L. C. 2026. *A Dawn Calendar in Eight Parts: Measuring the Nineveh Planisphere (K 8538) with Cribs.* https://github.com/loross14/k8538-dawn-calendar
