# Results

Headline DiD (Table 3, row 3): **+2.75 FTE** (SE 1.31, t = 2.10); that is 13.5% of NJ's pre-period mean FTE.

## Table 3: mean FTE employment by state and wave

| row                                      |    PA |   PA_se |    NJ |   NJ_se |   NJ_minus_PA |   diff_se |   t_stat |   paper_PA |   paper_NJ |   paper_diff |
|:-----------------------------------------|------:|--------:|------:|--------:|--------------:|----------:|---------:|-----------:|-----------:|-------------:|
| 1. FTE before                            | 23.33 |    1.35 | 20.44 |    0.51 |         -2.89 |      1.44 |    -2.00 |      23.33 |      20.44 |        -2.89 |
| 2. FTE after                             | 21.17 |    0.94 | 21.03 |    0.52 |         -0.14 |      1.08 |    -0.13 |      21.17 |      21.03 |        -0.14 |
| 3. Change in mean FTE                    | -2.17 |    1.22 |  0.59 |    0.47 |          2.75 |      1.31 |     2.10 |      -2.16 |       0.59 |         2.76 |
| 4. Change in mean FTE, balanced sample   | -2.28 |    1.25 |  0.47 |    0.48 |          2.75 |      1.34 |     2.05 |      -2.28 |       0.47 |         2.75 |
| 5. Change, temporarily closed stores = 0 | -2.28 |    1.25 |  0.23 |    0.49 |          2.51 |      1.35 |     1.86 |      -2.28 |       0.23 |         2.51 |

## 2x2 DiD as a stacked regression (all stores with data in a wave)

| standard errors    |   estimate |   se |    t |
|:-------------------|-----------:|-----:|-----:|
| conventional       |       2.75 | 1.69 | 1.63 |
| HC1 robust         |       2.75 | 1.80 | 1.53 |
| clustered by store |       2.75 | 1.31 | 2.11 |

## Table 4: regression-adjusted DiD (dependent variable: change in FTE, balanced sample)

Conventional OLS standard errors, as in the paper:

| spec   | regressor   |   coef |   se |    t |   n |   se_regression |   paper_coef |
|:-------|:------------|-------:|-----:|-----:|----:|----------------:|-------------:|
| (i)    | nj          |   2.33 | 1.19 | 1.95 | 357 |            8.79 |         2.33 |
| (ii)   | nj          |   2.30 | 1.20 | 1.93 | 357 |            8.78 |         2.30 |
| (iii)  | gap         |  15.65 | 6.08 | 2.57 | 357 |            8.76 |        15.65 |
| (iv)   | gap         |  14.92 | 6.21 | 2.40 | 357 |            8.76 |        14.92 |
| (v)    | gap         |  11.98 | 7.42 | 1.61 | 357 |            8.75 |        11.91 |

Controls: (ii), (iv): chain dummies (KFC, Roy Rogers, Wendy's; Burger King omitted) and company-owned dummy. (v) adds region dummies (central NJ, north NJ, PA1, PA2; south NJ omitted).


Same regressions with HC1 robust standard errors:

| spec   | regressor   |   coef |   se |    t |   n |   se_regression |   paper_coef |
|:-------|:------------|-------:|-----:|-----:|----:|----------------:|-------------:|
| (i)    | nj          |   2.33 | 1.45 | 1.60 | 357 |            8.79 |         2.33 |
| (ii)   | nj          |   2.30 | 1.45 | 1.59 | 357 |            8.78 |         2.30 |
| (iii)  | gap         |  15.65 | 6.17 | 2.54 | 357 |            8.76 |        15.65 |
| (iv)   | gap         |  14.92 | 6.53 | 2.28 | 357 |            8.76 |        14.92 |
| (v)    | gap         |  11.98 | 7.04 | 1.70 | 357 |            8.75 |        11.91 |

## Table 5: specification tests (chain and ownership controls in every model)

Each cell: our estimate (standard error) [paper's estimate]. Level = change in FTE; prop = change in FTE divided by average FTE across the two waves (closed stores = -1).

|   row | specification                                   |   n | NJ dummy, level    | GAP, level            | NJ dummy, prop        | GAP, prop            |
|------:|:------------------------------------------------|----:|:-------------------|:----------------------|:----------------------|:---------------------|
|     1 | Base specification                              | 357 | 2.30 (1.20) [2.30] | 14.92 (6.21) [14.92]  | 0.050 (0.051) [0.050] | 0.34 (0.26) [0.34]   |
|     2 | Treat 4 temporarily closed stores as closed     | 361 | 2.03 (1.22) [2.20] | 14.42 (6.31) [14.42]  | 0.035 (0.052) [0.040] | 0.34 (0.27) [0.34]   |
|     3 | Exclude managers from FTE                       | 357 | 2.34 (1.17) [2.34] | 14.69 (6.05) [14.69]  | 0.054 (0.058) [0.050] | 0.40 (0.30) [0.28]   |
|     4 | Part-time = 0.4 x full-time                     | 357 | 2.34 (1.20) [2.34] | 15.23 (6.23) [15.23]  | 0.059 (0.055) [0.060] | 0.41 (0.28) [0.30]   |
|     5 | Part-time = 0.6 x full-time                     | 357 | 2.27 (1.21) [2.27] | 14.60 (6.26) [14.60]  | 0.042 (0.048) [0.040] | 0.28 (0.25) [0.17]   |
|     6 | Exclude NJ shore stores                         | 326 | 2.59 (1.20) [2.58] | 16.88 (6.37) [16.88]  | 0.055 (0.051) [0.060] | 0.42 (0.27) [0.42]   |
|     7 | Add wave-2 interview-week dummies               | 357 | 2.02 (1.20) [2.27] | 14.25 (6.21) [15.79]  | 0.043 (0.051) [0.050] | 0.33 (0.26) [0.40]   |
|     8 | Exclude stores called back 3+ times in wave 1   | 294 | 2.42 (1.29) [2.41] | 14.08 (7.11) [14.08]  | 0.054 (0.053) [0.050] | 0.31 (0.29) [0.31]   |
|     9 | Weight by wave-1 employment (WLS)               | 357 | -                  | -                     | 0.125 (0.049) [0.130] | 0.81 (0.26) [0.81]   |
|    12 | Placebo: PA stores only, GAP to $5.05           |  67 | -                  | -0.30 (22.00) [-0.30] | -                     | -0.33 (0.74) [-0.33] |
|    13 | Extra: add NJ region dummies (south NJ omitted) | 357 | 2.57 (1.46)        | 14.61 (6.41)          | 0.049 (0.062)         | 0.32 (0.27)          |
|    14 | Extra: NJ stores only                           | 290 | -                  | 12.21 (6.88)          | -                     | 0.31 (0.31)          |

## Starting wages

| state   |   wage_before |   wage_after |   share_below_505_before |   share_at_505_after |
|:--------|--------------:|-------------:|-------------------------:|---------------------:|
| PA      |         4.630 |        4.617 |                    0.947 |                0.014 |
| NJ      |         4.612 |        5.081 |                    0.911 |                0.890 |
