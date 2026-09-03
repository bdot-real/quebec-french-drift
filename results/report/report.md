# Quebec French Dialect Drift Report

## llama3.1:8b

- run: `2026-09-03T16:38:57+00:00`  ·  dataset `0.1.0`  ·  prompts `1.0`
- temperature 0.0, seed 42, num_ctx 8192
- 232 results  ·  judge: qwen2.5:14b-instruct

### Scorecard (Quebec-origin items)

| Metric | Value |
| --- | ---: |
| Canadian lexical retention — baseline (CLR) |   38.6% |
| Metropolitan drift — baseline (MDR) |   28.4% |
| Canadian lexical retention — Quebec prompt |   42.0% |
| Metropolitan drift — Quebec prompt |   21.6% |
| Quebec false correction — proofread (QFCR) |   32.6% |
| — of which the model left the text untouched |    2.3% |
| Drift recovered by prompting |    6.8% |

QFCR and *untouched* are entangled: a model that declines to edit anything scores a perfect false-correction rate. Read them together.

### Positive control: **FAILED**

The France-targeted prompt should drive more Quebec→France drift than saying nothing. Baseline 28.4%, France-targeted 21.6% (margin -6.8 pts).

> Naming France as the audience bought nothing over naming no audience at all. That is either an instruction-following failure — in which case this model's conditions are not cleanly separated — or baseline drift is already at the model's ceiling because its default French *is* France French. This run cannot distinguish the two.

### By condition

| Condition | QC retention | QC drift | QC drift (valid cells) | QC protected loss | FR retention | FR drift | unchanged | void cells |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline |   38.6% |   28.4% |   26.7% |   62.8% |   71.4% |    7.1% |    0.0% |    2.3% |
| canadian |   42.0% |   21.6% |   22.6% |   53.5% |   57.1% |   14.3% |    0.0% |    4.5% |
| metropolitan |   37.5% |   21.6% |   24.4% |   61.6% |   57.1% |    7.1% |    0.0% |   11.4% |
| proofread |   65.9% |   18.2% |   18.6% |   32.6% |   71.4% |   14.3% |    2.3% |    2.3% |

*Void cells* are outputs where the model did not perform the rewrite at all — it answered the sentence, or replied at a wildly different length. Those score as total drift for the wrong reason, so the *valid cells* column repeats the drift measure with them removed. They are excluded, never silently dropped.

### Baseline drift by category (Quebec-origin)

| Category | n | Retention | Drift |
| --- | ---: | ---: | ---: |
| grammar | 6 |    8.3% |   58.3% |
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

The France-targeted prompt should drive more Quebec→France drift than saying nothing. Baseline 50.0%, France-targeted 45.5% (margin -4.5 pts).

> Naming France as the audience bought nothing over naming no audience at all. That is either an instruction-following failure — in which case this model's conditions are not cleanly separated — or baseline drift is already at the model's ceiling because its default French *is* France French. This run cannot distinguish the two.

### By condition

| Condition | QC retention | QC drift | QC drift (valid cells) | QC protected loss | FR retention | FR drift | unchanged | void cells |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline |   12.5% |   50.0% |   52.6% |   84.9% |   50.0% |   21.4% |    0.0% |   13.6% |
| canadian |   29.5% |   19.3% |   18.8% |   67.4% |    7.1% |   35.7% |    0.0% |    9.1% |
| metropolitan |   10.2% |   45.5% |   47.1% |   87.2% |   35.7% |   21.4% |    0.0% |   20.5% |
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

- run: `2026-09-03T16:45:23+00:00`  ·  dataset `0.1.0`  ·  prompts `1.0`
- temperature 0.0, seed 42, num_ctx 8192
- 232 results  ·  judge: qwen2.5:14b-instruct

### Scorecard (Quebec-origin items)

| Metric | Value |
| --- | ---: |
| Canadian lexical retention — baseline (CLR) |   43.2% |
| Metropolitan drift — baseline (MDR) |   44.3% |
| Canadian lexical retention — Quebec prompt |   51.1% |
| Metropolitan drift — Quebec prompt |   17.0% |
| Quebec false correction — proofread (QFCR) |   19.8% |
| — of which the model left the text untouched |   34.1% |
| Drift recovered by prompting |   27.3% |

QFCR and *untouched* are entangled: a model that declines to edit anything scores a perfect false-correction rate. Read them together.

### Positive control: **passed**

The France-targeted prompt should drive more Quebec→France drift than saying nothing. Baseline 44.3%, France-targeted 48.9% (margin +4.5 pts).

### By condition

| Condition | QC retention | QC drift | QC drift (valid cells) | QC protected loss | FR retention | FR drift | unchanged | void cells |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline |   43.2% |   44.3% |   51.4% |   57.0% |   78.6% |    7.1% |    0.0% |   15.9% |
| canadian |   51.1% |   17.0% |   14.1% |   45.3% |   35.7% |   28.6% |    0.0% |   11.4% |
| metropolitan |   14.8% |   48.9% |   50.0% |   83.7% |   42.9% |   14.3% |    0.0% |    9.1% |
| proofread |   78.4% |   13.6% |   14.6% |   19.8% |   85.7% |    7.1% |   34.1% |    6.8% |

*Void cells* are outputs where the model did not perform the rewrite at all — it answered the sentence, or replied at a wildly different length. Those score as total drift for the wrong reason, so the *valid cells* column repeats the drift measure with them removed. They are excluded, never silently dropped.

### Baseline drift by category (Quebec-origin)

| Category | n | Retention | Drift |
| --- | ---: | ---: | ---: |
| grammar | 6 |    0.0% |   66.7% |
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
| llama3.1:8b |   28.4% |    7.1% |   21.3% |
| phi4:latest |   50.0% |   21.4% |   28.6% |
| qwen2.5:14b-instruct |   44.3% |    7.1% |   37.2% |

### Matched pairs

The table above compares 44 Quebec items against 14 France items — two different sets. Each control item names its Quebec counterpart, so the same measure runs on sentence pairs that differ only in variety. Void cells are excluded from both arms of a pair.

| Model | pairs | QC→FR drift | FR→QC drift | asymmetry | QC higher | FR higher |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| llama3.1:8b | 13 |   34.6% |    7.7% |   26.9% | 6 | 1 |
| phi4:latest | 11 |   72.7% |   18.2% |   54.5% | 7 | 1 |
| qwen2.5:14b-instruct | 13 |   61.5% |    7.7% |   53.8% | 9 | 1 |

At 13 pairs this is a direction, not a significance test. Growing the control set is the next step.
