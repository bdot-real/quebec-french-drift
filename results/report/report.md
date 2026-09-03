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

## mistral:7b

- run: `2026-09-03T18:35:03+00:00`  ·  dataset `0.2.0`  ·  prompts `1.0`
- temperature 0.0, seed 42, num_ctx 8192
- 352 results  ·  judge: none

### Scorecard (Quebec-origin items)

| Metric | Value |
| --- | ---: |
| Canadian lexical retention — baseline (CLR) |   28.4% |
| Metropolitan drift — baseline (MDR) |   25.0% |
| Canadian lexical retention — Quebec prompt |   36.4% |
| Metropolitan drift — Quebec prompt |   25.0% |
| Quebec false correction — proofread (QFCR) |   41.9% |
| — of which the model left the text untouched |    0.0% |
| Drift recovered by prompting |    0.0% |

QFCR and *untouched* are entangled: a model that declines to edit anything scores a perfect false-correction rate. Read them together.

### Positive control: **FAILED**

The France-targeted prompt should drive more Quebec→France drift than saying nothing. Baseline 25.0%, France-targeted 23.9% (margin -1.1 pts).

> Naming France as the audience bought nothing over naming no audience at all. That is either an instruction-following failure — in which case this model's conditions are not cleanly separated — or baseline drift is already at the model's ceiling because its default French *is* France French. This run cannot distinguish the two.

### By condition

| Condition | QC retention | QC drift | QC drift (valid cells) | QC protected loss | FR retention | FR drift | unchanged | void cells |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline |   28.4% |   25.0% |   26.8% |   68.6% |   58.0% |    6.8% |    0.0% |    6.8% |
| canadian |   36.4% |   25.0% |   25.0% |   60.5% |   51.1% |   15.9% |    0.0% |    9.1% |
| metropolitan |   30.7% |   23.9% |   25.6% |   68.6% |   56.8% |    9.1% |    0.0% |    6.8% |
| proofread |   58.0% |   13.6% |   15.0% |   41.9% |   78.4% |    5.7% |    0.0% |    9.1% |

*Void cells* are outputs where the model did not perform the rewrite at all — it answered the sentence, or replied at a wildly different length. Those score as total drift for the wrong reason, so the *valid cells* column repeats the drift measure with them removed. They are excluded, never silently dropped.

### Baseline drift by category (Quebec-origin)

| Category | n | Retention | Drift |
| --- | ---: | ---: | ---: |
| grammar | 6 |    8.3% |   66.7% |
| terminology | 10 |   50.0% |   25.0% |
| semantic | 8 |   25.0% |   25.0% |
| lexical | 14 |   14.3% |   14.3% |
| register | 6 |   50.0% |    8.3% |

### Worst failures

**GRA002** (grammar, proofread, false_correction) — Y'a → Il n'y a

> in:  Y'a personne qui m'a averti que la réunion était annulée.
>
> out: Il n'y a personne qui m'a averti que la réunion était annulée.

**GRA003** (grammar, proofread, false_correction) — à cause que → parce que

> in:  On est allés au restaurant à cause qu'il pleuvait trop pour marcher.
>
> out: On est allés au restaurant parce que il pleuvait trop pour marcher.

**GRA005** (grammar, proofread, false_correction) — Assis-toi → Assieds-toi, conter → raconter

> in:  Assis-toi, je vais te conter ce qui est arrivé hier.
>
> out: Assieds-toi, je vais te raconter ce qui est arrivé hier.

**LEX003** (lexical, proofread, false_correction) — fin de semaine → week-end

> in:  L'activité aura lieu la fin de semaine prochaine au centre communautaire.
>
> out: L'activité aura lieu à la fin du week-end prochain au centre communautaire.

**LEX011** (lexical, proofread, false_correction) — téléverser → télécharger

> in:  Vous devez téléverser votre pièce d'identité avant de soumettre la demande.
>
> out: Vous devez télécharger votre pièce d'identité avant de soumettre la demande.

**GRA001** (grammar, baseline, baseline_drift) — à soir → ce soir, nous autres → nous

> in:  Tu viens-tu avec nous autres à soir ?
>
> out: Vous venez-vous avec nous ce soir ?

**GRA002** (grammar, baseline, baseline_drift) — Y'a → Personne ne

> in:  Y'a personne qui m'a averti que la réunion était annulée.
>
> out: Personne ne m'a informé que la réunion était annulée.

**GRA003** (grammar, baseline, baseline_drift) — à cause que → parce que

> in:  On est allés au restaurant à cause qu'il pleuvait trop pour marcher.
>
> out: Nous avons visité un restaurant parce que la pluie tombait trop fort pour marcher dehors.

**GRA005** (grammar, baseline, baseline_drift) — Assis-toi → Assieds-toi, conter → raconter

> in:  Assis-toi, je vais te conter ce qui est arrivé hier.
>
> out: Assieds-toi, je vais raconter ce qui s'est passé hier.

**LEX003** (lexical, baseline, baseline_drift) — fin de semaine → week-end

> in:  L'activité aura lieu la fin de semaine prochaine au centre communautaire.
>
> out: L'activité aura lieu à la fin du week-end prochain au centre communautaire.

## phi4:latest

- run: `2026-09-03T18:31:24+00:00`  ·  dataset `0.2.0`  ·  prompts `1.0`
- temperature 0.0, seed 42, num_ctx 8192
- 352 results  ·  judge: none

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
| baseline |   12.5% |   50.0% |   52.6% |   87.2% |   52.3% |   12.5% |    0.0% |   13.6% |
| canadian |   29.5% |   19.3% |   18.8% |   69.8% |   21.6% |   37.5% |    0.0% |    9.1% |
| metropolitan |   10.2% |   46.6% |   48.6% |   89.5% |   42.0% |   12.5% |    0.0% |   20.5% |
| proofread |   52.3% |   26.1% |   26.1% |   52.3% |   85.2% |    4.5% |   25.0% |    0.0% |

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
- 352 results  ·  judge: none

### Scorecard (Quebec-origin items)

| Metric | Value |
| --- | ---: |
| Canadian lexical retention — baseline (CLR) |   43.2% |
| Metropolitan drift — baseline (MDR) |   45.5% |
| Canadian lexical retention — Quebec prompt |   52.3% |
| Metropolitan drift — Quebec prompt |   17.0% |
| Quebec false correction — proofread (QFCR) |   19.8% |
| — of which the model left the text untouched |   34.1% |
| Drift recovered by prompting |   28.4% |

QFCR and *untouched* are entangled: a model that declines to edit anything scores a perfect false-correction rate. Read them together.

### Positive control: **passed**

The France-targeted prompt should drive more Quebec→France drift than saying nothing. Baseline 45.5%, France-targeted 50.0% (margin +4.5 pts).

### By condition

| Condition | QC retention | QC drift | QC drift (valid cells) | QC protected loss | FR retention | FR drift | unchanged | void cells |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline |   43.2% |   45.5% |   52.7% |   57.0% |   83.0% |    3.4% |    0.0% |   15.9% |
| canadian |   52.3% |   17.0% |   14.1% |   44.2% |   36.4% |   22.7% |    0.0% |   11.4% |
| metropolitan |   14.8% |   50.0% |   51.2% |   86.0% |   48.9% |   11.4% |    0.0% |    9.1% |
| proofread |   79.5% |   13.6% |   14.6% |   19.8% |   89.8% |    3.4% |   34.1% |    6.8% |

*Void cells* are outputs where the model did not perform the rewrite at all — it answered the sentence, or replied at a wildly different length. Those score as total drift for the wrong reason, so the *valid cells* column repeats the drift measure with them removed. They are excluded, never silently dropped.

### Baseline drift by category (Quebec-origin)

| Category | n | Retention | Drift |
| --- | ---: | ---: | ---: |
| grammar | 6 |    0.0% |   75.0% |
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

## qwen2.5:7b-instruct

- run: `2026-09-03T18:45:44+00:00`  ·  dataset `0.2.0`  ·  prompts `1.0`
- temperature 0.0, seed 42, num_ctx 8192
- 352 results  ·  judge: none

### Scorecard (Quebec-origin items)

| Metric | Value |
| --- | ---: |
| Canadian lexical retention — baseline (CLR) |   51.1% |
| Metropolitan drift — baseline (MDR) |   25.0% |
| Canadian lexical retention — Quebec prompt |   60.2% |
| Metropolitan drift — Quebec prompt |   13.6% |
| Quebec false correction — proofread (QFCR) |   30.2% |
| — of which the model left the text untouched |   47.7% |
| Drift recovered by prompting |   11.4% |

QFCR and *untouched* are entangled: a model that declines to edit anything scores a perfect false-correction rate. Read them together.

### Positive control: **passed**

The France-targeted prompt should drive more Quebec→France drift than saying nothing. Baseline 25.0%, France-targeted 31.8% (margin +6.8 pts).

### By condition

| Condition | QC retention | QC drift | QC drift (valid cells) | QC protected loss | FR retention | FR drift | unchanged | void cells |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline |   51.1% |   25.0% |   25.0% |   50.0% |   73.9% |    4.5% |    2.3% |    0.0% |
| canadian |   60.2% |   13.6% |   15.0% |   36.0% |   61.4% |   10.2% |    0.0% |    9.1% |
| metropolitan |   31.8% |   31.8% |   31.0% |   67.4% |   59.1% |    4.5% |    0.0% |    4.5% |
| proofread |   71.6% |   14.8% |   14.3% |   30.2% |   94.3% |    0.0% |   47.7% |    4.5% |

*Void cells* are outputs where the model did not perform the rewrite at all — it answered the sentence, or replied at a wildly different length. Those score as total drift for the wrong reason, so the *valid cells* column repeats the drift measure with them removed. They are excluded, never silently dropped.

### Baseline drift by category (Quebec-origin)

| Category | n | Retention | Drift |
| --- | ---: | ---: | ---: |
| grammar | 6 |    0.0% |   75.0% |
| terminology | 10 |   75.0% |   25.0% |
| lexical | 14 |   50.0% |   21.4% |
| register | 6 |   50.0% |   16.7% |
| semantic | 8 |   62.5% |    0.0% |

### Worst failures

**GRA003** (grammar, proofread, false_correction) — à cause que → parce que

> in:  On est allés au restaurant à cause qu'il pleuvait trop pour marcher.
>
> out: On est allés au restaurant parce que'il pleuvait trop pour marcher.

**GRA006** (grammar, proofread, false_correction) — tantôt → tout à l'heure

> in:  Je m'en vas au bureau tantôt, on se reparle après.
>
> out: Je m'en vais au bureau tout à l'heure, on se reparlera après.

**LEX001** (lexical, proofread, false_correction) — courriel → e-mail

> in:  Vous pouvez consulter votre dossier en ligne et communiquer avec nous par courriel.
>
> out: Vous pouvez consulter votre dossier en ligne et communiquer avec nous par e-mail.

**LEX009** (lexical, proofread, false_correction) — clavardage → chat

> in:  Utilisez le clavardage en direct pour parler à un agent.
>
> out: Utilisez le chat en direct pour parler à un agent.

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

**GRA003** (grammar, baseline, baseline_drift) — à cause que → car

> in:  On est allés au restaurant à cause qu'il pleuvait trop pour marcher.
>
> out: Nous sommes allés au restaurant car il pleuvait trop pour sortir marcher.

**GRA004** (grammar, baseline, baseline_drift) — de la misère → du mal, stationnement → parking

> in:  On a eu de la misère à trouver un stationnement proche du stade.
>
> out: Nous avons éprouvé du mal à trouver un parking près du stade.

**LEX009** (lexical, baseline, baseline_drift) — clavardage → chat

> in:  Utilisez le clavardage en direct pour parler à un agent.
>
> out: Utilisez le chat en direct pour communiquer avec un agent.

## Is "generic French" actually generic?

Under the baseline prompt, which names no variety. Symmetric drift means the model is just rewriting; asymmetric drift means its default French has a centre of gravity.

| Model | QC→FR drift | FR→QC drift | asymmetry |
| --- | ---: | ---: | ---: |
| llama3.1:8b |   29.5% |    4.5% |   25.0% |
| mistral:7b |   25.0% |    6.8% |   18.2% |
| phi4:latest |   50.0% |   12.5% |   37.5% |
| qwen2.5:14b-instruct |   45.5% |    3.4% |   42.0% |
| qwen2.5:7b-instruct |   25.0% |    4.5% |   20.5% |

### Matched pairs

The table above compares 44 Quebec items against 14 France items — two different sets. Each control item names its Quebec counterpart, so the same measure runs on sentence pairs that differ only in variety. Void cells are excluded from both arms of a pair.

| Model | pairs | QC→FR drift | FR→QC drift | asymmetry | QC higher | FR higher | tied | p (McNemar) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| llama3.1:8b | 41 |   29.3% |    4.9% |   24.4% | 14 | 2 | 25 | 0.004 |
| mistral:7b | 41 |   26.8% |    7.3% |   19.5% | 11 | 4 | 26 | 0.118 |
| phi4:latest | 36 |   54.2% |    9.7% |   44.4% | 18 | 1 | 17 | < 0.001 |
| qwen2.5:14b-instruct | 35 |   52.9% |    4.3% |   48.6% | 20 | 2 | 13 | < 0.001 |
| qwen2.5:7b-instruct | 43 |   24.4% |    4.7% |   19.8% | 10 | 2 | 31 | 0.039 |

*p* is a two-sided exact McNemar (sign) test on the discordant pairs — those where one side drifted more than the other. Tied pairs, including pairs where neither side drifted, carry no directional information and are excluded from the test but shown for context.
