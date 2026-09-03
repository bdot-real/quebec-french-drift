# Quebec French Dialect Drift Report

## llama3.1:8b

- run: `2026-09-03T18:13:26+00:00`  ·  dataset `0.1.0`  ·  prompts `1.0`
- temperature 0.0, seed 42, num_ctx 8192
- 352 results  ·  judge: none

### Scorecard (Quebec-origin items)

| Metric | Value |
| --- | ---: |
| Canadian lexical retention — baseline (CLR) |   37.5% |
| Metropolitan drift — baseline (MDR) |   29.5% |
| Canadian lexical retention — Quebec prompt |   42.0% |
| Metropolitan drift — Quebec prompt |   21.6% |
| Quebec false correction — proofread (QFCR) |   30.2% |
| — of which the model left the text untouched |    2.3% |
| Drift recovered by prompting |    8.0% |

QFCR and *untouched* are entangled: a model that declines to edit anything scores a perfect false-correction rate. Read them together.

### Positive control: **FAILED**

The France-targeted prompt should drive more Quebec→France drift than saying nothing. Baseline 29.5%, France-targeted 22.7% (margin -6.8 pts).

> Naming France as the audience bought nothing over naming no audience at all. That is either an instruction-following failure — in which case this model's conditions are not cleanly separated — or baseline drift is already at the model's ceiling because its default French *is* France French. This run cannot distinguish the two.

### By condition

| Condition | QC retention | QC drift | QC drift (valid cells) | QC protected loss | FR retention | FR drift | unchanged | void cells |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline |   37.5% |   29.5% |   27.9% |   62.8% |   70.5% |    4.5% |    0.0% |    2.3% |
| canadian |   42.0% |   21.6% |   22.6% |   55.8% |   53.4% |   11.4% |    0.0% |    4.5% |
| metropolitan |   36.4% |   22.7% |   25.6% |   64.0% |   61.4% |   10.2% |    0.0% |   11.4% |
| proofread |   67.0% |   18.2% |   18.6% |   30.2% |   81.8% |    4.5% |    2.3% |    2.3% |

*Void cells* are outputs where the model did not perform the rewrite at all — it answered the sentence, or replied at a wildly different length. Those score as total drift for the wrong reason, so the *valid cells* column repeats the drift measure with them removed. They are excluded, never silently dropped.

### Baseline drift by category (Quebec-origin)

| Category | n | Retention | Drift |
| --- | ---: | ---: | ---: |
| grammar | 6 |    0.0% |   66.7% |
| terminology | 10 |   50.0% |   35.0% |
| register | 6 |   41.7% |   33.3% |
| lexical | 14 |   42.9% |   25.0% |
| semantic | 8 |   37.5% |    0.0% |

### Judge scores — illustrative only

A local 8-30B model is a weak authority on Quebec French, and the sample below is small and uneven across models. These numbers illustrate the failure modes; they do not rank the models. The mechanical metrics above are the headline.

| Condition | n | meaning | QC naturalness | regional usage | variety shift | unnecessary correction |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | 8 | 3.88 | 3.38 | 2.62 | 2.88 | 2.75 |
| proofread | 9 | 4.22 | 3.67 | 3.11 | 2.44 | 2.56 |

### Worst failures

**GRA001** (grammar, proofread, false_correction) — à soir → ce soir, nous autres → nous

> in:  Tu viens-tu avec nous autres à soir ?
>
> out: Vous voulez venir avec nous ce soir ?

**GRA002** (grammar, proofread, false_correction) — Y'a → Personne ne

> in:  Y'a personne qui m'a averti que la réunion était annulée.
>
> out: Personne ne m'a averti que la réunion était annulée.

**GRA003** (grammar, proofread, false_correction) — à cause que → parce que

> in:  On est allés au restaurant à cause qu'il pleuvait trop pour marcher.
>
> out: Nous sommes allés au restaurant parce que il pleuvait trop pour marcher.

**LEX010** (lexical, proofread, false_correction) — pourriel → spam

> in:  Supprimez les pourriels sans ouvrir les pièces jointes.
>
> out: Supprimez les spams sans ouvrir les pièces jointes.

**TER003** (terminology, proofread, false_correction) — infonuagique → informatique en nuage

> in:  La migration vers l'infonuagique réduira les coûts d'exploitation.
>
> out: La migration vers l'informatique en nuage réduira les coûts d'exploitation.

**TER005** (terminology, proofread, false_correction) — rançongiciel → ransomware

> in:  L'attaque par rançongiciel a chiffré les serveurs de l'organisme.
>
> out: L'attaque par ransomware a chiffré les serveurs de l'organisme.

**GRA001** (grammar, baseline, baseline_drift) — à soir → ce soir, nous autres → nous

> in:  Tu viens-tu avec nous autres à soir ?
>
> out: Vous allez vous amuser ce soir ? Nous sommes tous là-bas et c'est une belle soirée ! Vous devriez venir rejoindre la fête.

**GRA002** (grammar, baseline, baseline_drift) — Y'a → Personne ne

> in:  Y'a personne qui m'a averti que la réunion était annulée.
>
> out: Personne ne m'a prévenu que la réunion avait été annulée.

**GRA003** (grammar, baseline, baseline_drift) — à cause que → parce que

> in:  On est allés au restaurant à cause qu'il pleuvait trop pour marcher.
>
> out: Nous sommes allés au restaurant parce que la pluie tombait trop fort pour pouvoir marcher.

**LEX001** (lexical, baseline, baseline_drift) — courriel → e-mail

> in:  Vous pouvez consulter votre dossier en ligne et communiquer avec nous par courriel.
>
> out: Vous pouvez consulter votre dossier en ligne et vous mettre en contact avec nous par e-mail.

## phi4:latest

- run: `2026-09-03T16:57:59+00:00`  ·  dataset `0.1.0`  ·  prompts `1.0`
- temperature 0.0, seed 42, num_ctx 8192
- 232 results  ·  judge: qwen2.5:14b-instruct

### Scorecard (Quebec-origin items)

| Metric | Value |
| --- | ---: |
| Canadian lexical retention — baseline (CLR) |   12.5% |
| Metropolitan drift — baseline (MDR) |   50.0% |
| Canadian lexical retention — Quebec prompt |   29.5% |
| Metropolitan drift — Quebec prompt |   19.3% |
| Quebec false correction — proofread (QFCR) |   52.3% |
| — of which the model left the text untouched |   25.0% |
| Drift recovered by prompting |   30.7% |

QFCR and *untouched* are entangled: a model that declines to edit anything scores a perfect false-correction rate. Read them together.

### Positive control: **FAILED**

The France-targeted prompt should drive more Quebec→France drift than saying nothing. Baseline 50.0%, France-targeted 46.6% (margin -3.4 pts).

> Naming France as the audience bought nothing over naming no audience at all. That is either an instruction-following failure — in which case this model's conditions are not cleanly separated — or baseline drift is already at the model's ceiling because its default French *is* France French. This run cannot distinguish the two.

### By condition

| Condition | QC retention | QC drift | QC drift (valid cells) | QC protected loss | FR retention | FR drift | unchanged | void cells |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline |   12.5% |   50.0% |   52.6% |   87.2% |   50.0% |   21.4% |    0.0% |   13.6% |
| canadian |   29.5% |   19.3% |   18.8% |   69.8% |    7.1% |   35.7% |    0.0% |    9.1% |
| metropolitan |   10.2% |   46.6% |   48.6% |   89.5% |   35.7% |   21.4% |    0.0% |   20.5% |
| proofread |   52.3% |   26.1% |   26.1% |   52.3% |   78.6% |    7.1% |   25.0% |    0.0% |

*Void cells* are outputs where the model did not perform the rewrite at all — it answered the sentence, or replied at a wildly different length. Those score as total drift for the wrong reason, so the *valid cells* column repeats the drift measure with them removed. They are excluded, never silently dropped.

### Baseline drift by category (Quebec-origin)

| Category | n | Retention | Drift |
| --- | ---: | ---: | ---: |
| grammar | 6 |    0.0% |   66.7% |
| terminology | 10 |   20.0% |   65.0% |
| register | 6 |    8.3% |   50.0% |
| lexical | 14 |   14.3% |   46.4% |
| semantic | 8 |   12.5% |   25.0% |

### Judge scores — illustrative only

A local 8-30B model is a weak authority on Quebec French, and the sample below is small and uneven across models. These numbers illustrate the failure modes; they do not rank the models. The mechanical metrics above are the headline.

| Condition | n | meaning | QC naturalness | regional usage | variety shift | unnecessary correction |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | 8 | 4.12 | 3.25 | 2.50 | 3.00 | 2.62 |
| proofread | 7 | 4.86 | 4.00 | 3.29 | 2.86 | 2.86 |

### Worst failures

**GRA001** (grammar, proofread, false_correction) — à soir → ce soir, nous autres → nous

> in:  Tu viens-tu avec nous autres à soir ?
>
> out: Viens-tu avec nous ce soir ?

**GRA002** (grammar, proofread, false_correction) — Y'a → Personne ne

> in:  Y'a personne qui m'a averti que la réunion était annulée.
>
> out: Personne ne m’a averti que la réunion était annulée.

**GRA003** (grammar, proofread, false_correction) — à cause que → parce qu

> in:  On est allés au restaurant à cause qu'il pleuvait trop pour marcher.
>
> out: Nous sommes allés au restaurant parce qu'il pleuvait trop pour marcher.

**LEX010** (lexical, proofread, false_correction) — pourriel → spam

> in:  Supprimez les pourriels sans ouvrir les pièces jointes.
>
> out: Supprimez les spams sans ouvrir les pièces jointes.

**LEX011** (lexical, proofread, false_correction) — téléverser → télécharger

> in:  Vous devez téléverser votre pièce d'identité avant de soumettre la demande.
>
> out: Vous devez télécharger votre pièce d'identité avant de soumettre la demande.

**SEM003** (semantic, proofread, false_correction) — souperons → dînerons

> in:  Nous souperons vers 18 h avec les grands-parents.
>
> out: Nous dînerons vers 18 h avec les grands-parents.

**SEM006** (semantic, proofread, false_correction) — présentement → actuellement

> in:  Je vais présentement m'occuper de ton dossier.
>
> out: Je vais actuellement m’occuper de ton dossier.

**TER003** (terminology, proofread, false_correction) — infonuagique → informatique en nuage

> in:  La migration vers l'infonuagique réduira les coûts d'exploitation.
>
> out: La migration vers l'informatique en nuage réduira les coûts d'exploitation.

**TER004** (terminology, proofread, false_correction) — témoins → cookies

> in:  Ce site utilise des témoins pour mémoriser vos préférences.
>
> out: Ce site utilise des cookies pour mémoriser vos préférences.

**TER005** (terminology, proofread, false_correction) — rançongiciel → ransomware

> in:  L'attaque par rançongiciel a chiffré les serveurs de l'organisme.
>
> out: L'attaque par ransomware a chiffré les serveurs de l'organisme.

## qwen2.5:14b-instruct

- run: `2026-09-03T18:21:29+00:00`  ·  dataset `0.1.0`  ·  prompts `1.0`
- temperature 0.0, seed 42, num_ctx 8192
- 333 results  ·  judge: none

### Scorecard (Quebec-origin items)

| Metric | Value |
| --- | ---: |
| Canadian lexical retention — baseline (CLR) |   44.2% |
| Metropolitan drift — baseline (MDR) |   44.2% |
| Canadian lexical retention — Quebec prompt |   52.3% |
| Metropolitan drift — Quebec prompt |   17.4% |
| Quebec false correction — proofread (QFCR) |   20.2% |
| — of which the model left the text untouched |   34.9% |
| Drift recovered by prompting |   26.7% |

QFCR and *untouched* are entangled: a model that declines to edit anything scores a perfect false-correction rate. Read them together.

### Positive control: **passed**

The France-targeted prompt should drive more Quebec→France drift than saying nothing. Baseline 44.2%, France-targeted 48.8% (margin +4.7 pts).

### By condition

| Condition | QC retention | QC drift | QC drift (valid cells) | QC protected loss | FR retention | FR drift | unchanged | void cells |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline |   44.2% |   44.2% |   51.4% |   56.0% |   84.1% |    3.7% |    0.0% |   16.3% |
| canadian |   52.3% |   17.4% |   14.5% |   44.0% |   37.5% |   23.8% |    0.0% |   11.6% |
| metropolitan |   15.1% |   48.8% |   50.0% |   85.7% |   51.2% |   11.2% |    0.0% |    9.3% |
| proofread |   79.1% |   14.0% |   15.0% |   20.2% |   88.8% |    3.8% |   34.9% |    7.0% |

*Void cells* are outputs where the model did not perform the rewrite at all — it answered the sentence, or replied at a wildly different length. Those score as total drift for the wrong reason, so the *valid cells* column repeats the drift measure with them removed. They are excluded, never silently dropped.

### Baseline drift by category (Quebec-origin)

| Category | n | Retention | Drift |
| --- | ---: | ---: | ---: |
| grammar | 5 |    0.0% |   70.0% |
| lexical | 14 |   42.9% |   53.6% |
| register | 6 |   50.0% |   41.7% |
| terminology | 10 |   50.0% |   35.0% |
| semantic | 8 |   62.5% |   25.0% |

### Judge scores — illustrative only

A local 8-30B model is a weak authority on Quebec French, and the sample below is small and uneven across models. These numbers illustrate the failure modes; they do not rank the models. The mechanical metrics above are the headline.

| Condition | n | meaning | QC naturalness | regional usage | variety shift | unnecessary correction |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | 8 | 4.25 | 3.62 | 2.88 | 2.38 | 3.00 |
| proofread | 7 | 4.71 | 4.00 | 3.43 | 2.86 | 2.29 |

### Worst failures

**GRA001** (grammar, proofread, false_correction) — à soir → ce soir, nous autres → nous

> in:  Tu viens-tu avec nous autres à soir ?
>
> out: Viens-tu avec nous ce soir ?

**GRA002** (grammar, proofread, false_correction) — Y'a → Il n'y a

> in:  Y'a personne qui m'a averti que la réunion était annulée.
>
> out: Il n'y a personne qui m'ait averti que la réunion était annulée.

**LEX012** (lexical, proofread, false_correction) — babillard → tableau d'affichage

> in:  Consultez le babillard pour connaître les offres d'emploi internes.
>
> out: Consultez le tableau d'affichage pour connaître les offres d'emploi internes.

**SEM004** (semantic, proofread, false_correction) — barrer la porte → verrouiller la porte

> in:  N'oubliez pas de barrer la porte en partant.
>
> out: N'oubliez pas de verrouiller la porte en partant.

**TER004** (terminology, proofread, false_correction) — témoins → cookies

> in:  Ce site utilise des témoins pour mémoriser vos préférences.
>
> out: Ce site utilise des cookies pour mémoriser vos préférences.

**GRA001** (grammar, baseline, baseline_drift) — à soir → ce soir, nous autres → nous

> in:  Tu viens-tu avec nous autres à soir ?
>
> out: Viens-tu avec nous ce soir ?

**GRA002** (grammar, baseline, baseline_drift) — Y'a → Personne ne

> in:  Y'a personne qui m'a averti que la réunion était annulée.
>
> out: Personne ne m'a informé que la réunion avait été annulée.

**GRA003** (grammar, baseline, baseline_drift) — à cause que → parce qu

> in:  On est allés au restaurant à cause qu'il pleuvait trop pour marcher.
>
> out: On est allés au restaurant parce qu'il pleuvait trop pour marcher.

**LEX001** (lexical, baseline, baseline_drift) — courriel → email

> in:  Vous pouvez consulter votre dossier en ligne et communiquer avec nous par courriel.
>
> out: Vous pouvez consulter votre dossier en ligne et communiquer avec nous par email.

**LEX002** (lexical, baseline, baseline_drift) — stationnement → parking

> in:  Le stationnement est accessible derrière l'édifice à partir de 7 h.
>
> out: Le parking est disponible derrière l'immeuble à partir de 7 heures.

## Is "generic French" actually generic?

Under the baseline prompt, which names no variety. Symmetric drift means the model is just rewriting; asymmetric drift means its default French has a centre of gravity.

| Model | QC→FR drift | FR→QC drift | asymmetry |
| --- | ---: | ---: | ---: |
| llama3.1:8b |   29.5% |    4.5% |   25.0% |
| phi4:latest |   50.0% |   21.4% |   28.6% |
| qwen2.5:14b-instruct |   44.2% |    3.7% |   40.5% |

### Matched pairs

The table above compares 44 Quebec items against 14 France items — two different sets. Each control item names its Quebec counterpart, so the same measure runs on sentence pairs that differ only in variety. Void cells are excluded from both arms of a pair.

| Model | pairs | QC→FR drift | FR→QC drift | asymmetry | QC higher | FR higher | tied | p (McNemar) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| llama3.1:8b | 41 |   29.3% |    4.9% |   24.4% | 14 | 2 | 25 | 0.004 |
| phi4:latest | 11 |   72.7% |   18.2% |   54.5% | 7 | 1 | 3 | 0.070 |
| qwen2.5:14b-instruct | 32 |   51.6% |    4.7% |   46.9% | 18 | 2 | 12 | < 0.001 |

*p* is a two-sided exact McNemar (sign) test on the discordant pairs — those where one side drifted more than the other. Tied pairs, including pairs where neither side drifted, carry no directional information and are excluded from the test but shown for context.
