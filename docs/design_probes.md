design_probes.py
============

This script allows to **identify the best FISH probe** in a specific genomic region. Specifically, it provides a number of candidates from which the user can choose its favorite.

```
usage: design_probes.py [-h] [--description descr] [--feat_order fo]
                        [--f1_thr ft] [--min_d md] [--n_oligo no]
                        [--n_probes np] [--max_probes mp] [--win_shift ws]
                        [--outdir od] [-f [F]]
                        id name chr start end db

Query database for a FISH probe.

positional arguments:
  id                   Query ID.
  name                 Query name.
  chr                  Chromosome in "chrXX" format.
  start                Probe range starting position.
  end                  Probe range ending position.
  db                   Database folder path.

optional arguments:
  -h, --help           show this help message and exit
  --description descr  Query description
  --feat_order fo      Comma-separated features. Available features: size,
                       spread, centrality.
  --f1_thr ft          Threshold of first feature filter, used to identify a
                       range around the best value. It's the percentage range
                       around it. Accepts values from 0 to 1.
  --min_d md           Minimum distance between consecutive oligos.
  --n_oligo no         Number of oligos per probe.
  --n_probes np        Number of probes to design.
  --max_probes mp      Maximum number of output probe candidates. Set to "-1"
                       to retrieve all candidates.
  --win_shift ws       Window size fraction for shifting the windows.
  --outdir od          Query output directory.
  -f [F]               Force overwriting of the query if already run.
```


Probe characteristics
---------------------

The script focuses on three possible probe characteristics:

* **Size** (:math:`I_i`). The size of the genomic regione covered by the probe. It is calculated as the difference between the end position of the last :math:`k`-mer (:math:`E`) and the start position of the first :math:`k`-mer (:math:`S`).

```
I_i = E_i - S_i
```

* **Centrality** (:math:`C_i`). It measures how centrally the probe is located in the specified genomic region of interest (GRoI). Specifically, it takes values between 0 and 1, where 1 means perfectly central and 0 means perfectly borderline. Mathematically speaking, if :math:`S_g` and :math:`E_g` are respectively the start and end position of the GRoi, then

```
M_i = S_i + (E_i - S_i)/2
M_g = S_g + (E_g - S_g)/2
C_i = |d(S_g, M_g) - d(M_i, M_g)| / d(S_g, M_g)
```

With :math:`M_g` and :math:`M_i` being the middle points of the GRoI and of the :math:`i`-th probe, respectively, and `d(A, B)` being the distance between the points `A` and `B`.

* **Spread** (:math:`P_i`). It measures how homogeneously the oligomers are spread over the probe. It is basically the inverse of the consecutive-mers distance's standard deviation. Thus, the larger :math:`P_i`, the more homogeneously the oligomers are spread.

```
U_i = sum(from j=1, to N_O-1)((S_{j+1} - E_{j}) / (N_O - 1))

1/P_i = sqrt( sum(from j=1, to N_0-1)( (U - |S_(j+1) - E_j|)^2 / (N_0-1) ) )
```

It is important to note how size and spread need to be minimized, while centrality should be maximized.

Algorithm
---------

The algorithm behind the single probe design considers a probe candidate as a set of :math:`N_O` consecutive oligomers (or :math:`k`-mers), in the genomic region of interest. Two :math:`k`-mers are considered **consecutive** when there are no other :math:`k`-mers between them.

It starts by checking that the number of requested :math:`k`-mers can actually fit the specified GRoI. Otherwise, it throws an error. Keeping in mind that the ``uniqueOligo`` pipeline forces a minimum distance :math:`min_d` between consecutive :math:`k`-mers, the minimum size of a GRoI is

```
min_{I_G} = k · N_O + min_d · (N_O-1)
```

If the query passes the first test, the tool proceeds with the generation of all probe candidates :math:`C`. This is achieved by :math:`N_O` grouping consecutive :math:`k`-mers in :math:`C`.

```
C_i = O_i, O_{i + 1}, ..., O_{i + N_O - 1}
```

Where :math:`O_i` is the :math:`i`-th :math:`k`-mers in the GRoI and :math:`C_i` is the :math:`i`-th probe candidate. If the GRoI has :math:`N_G` :math:`k`-mers, then :math:`N_G - N_O + 1` probe candidates are generated.

The algorithms requires to rank the probe characteristics (size, centrality, and spread) in so-called 1st, 2nd and 3rd *features* (:math:`f_1`, :math:`f_2`, and :math:`f_3`).

```
best(f_x) = max(f_x) if f_x in {centrality}
best(f_x) = min(f_x) if f_x in {size, spread}
```

Then, the 1st feature is calculated for every probe candidate :math:`C` and the best probe candidate is identified. An interval around the best candidate 1st feature value is calculated using the user-provided threshold :math:`t`.

```
I_{f_1} = [ best(f_1) - t · best(f_1), best(f_1) + t · best(f_1) ]
```

Every candidate probe :math:`C_i` with an :math:`f_{1,i} not in I_{f_1}` is discarded.

Then, :math:`f_2` and :math:`f_3` are calculated for every remaining probe candidate. The candidates are ranked based on :math:`f_2` (with the :math:`best` on top) and returned as the output.

The tool also produces plots to easily understand how the probe is structured.
