# Quebec French Dialect Drift Report

## choco-fr

- run: `2026-09-03T19:29:29+00:00`  ·  dataset `0.2.0`  ·  prompts `1.0`
- provider ollama, temperature 0.0, seed 42, num_ctx 8192
- 352 results  ·  judge: none

### Scorecard (Quebec-origin items)

| Metric | Value |
| --- | ---: |
| Canadian lexical retention — baseline (CLR) |   10.2% |
| Metropolitan drift — baseline (MDR) |   31.8% |
| Canadian lexical retention — Quebec prompt |    0.0% |
| Metropolitan drift — Quebec prompt |   13.6% |
| Quebec false correction — proofread (QFCR) |   73.3% |
| — of which the model left the text untouched |    0.0% |
| Drift recovered by prompting |   18.2% |

QFCR and *untouched* are entangled: a model that declines to edit anything scores a perfect false-correction rate. Read them together.

### Positive control: **FAILED**

The France-targeted prompt should drive more Quebec→France drift than saying nothing. Baseline 31.8%, France-targeted 26.1% (margin -5.7 pts).

> Naming France as the audience bought nothing over naming no audience at all. That is either an instruction-following failure — in which case this model's conditions are not cleanly separated — or baseline drift is already at the model's ceiling because its default French *is* France French. This run cannot distinguish the two.

### By condition

| Condition | QC retention | QC drift | QC drift (valid cells) | QC protected loss | FR retention | FR drift | unchanged | void cells |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline |   10.2% |   31.8% |   34.5% |   90.7% |   31.8% |   14.8% |    0.0% |   34.1% |
| canadian |    0.0% |   13.6% |   17.6% |  100.0% |   14.8% |   11.4% |    0.0% |   61.4% |
| metropolitan |   11.4% |   26.1% |   29.4% |   88.4% |   13.6% |   15.9% |    0.0% |   61.4% |
| proofread |   25.0% |   31.8% |   31.8% |   73.3% |   62.5% |    5.7% |    0.0% |    0.0% |

*Void cells* are outputs where the model did not perform the rewrite at all — it answered the sentence, or replied at a wildly different length. Those score as total drift for the wrong reason, so the *valid cells* column repeats the drift measure with them removed. They are excluded, never silently dropped.

### Baseline drift by category (Quebec-origin)

| Category | n | Retention | Drift |
| --- | ---: | ---: | ---: |
| grammar | 6 |    0.0% |   50.0% |
| lexical | 14 |   14.3% |   46.4% |
| register | 6 |    8.3% |   33.3% |
| semantic | 8 |    0.0% |   25.0% |
| terminology | 10 |   20.0% |    5.0% |

### Worst failures

**GRA001** (grammar, proofread, false_correction) — à soir → ce soir, nous autres → nous

> in:  Tu viens-tu avec nous autres à soir ?
>
> out: Viens-tu avec nous d'autres ce soir ?

**GRA003** (grammar, proofread, false_correction) — à cause que → parce que

> in:  On est allés au restaurant à cause qu'il pleuvait trop pour marcher.
>
> out: Nous sommes allés au restaurant parce que la pluie était si forte qu'on ne pouvait pas marcher.

**LEX001** (lexical, proofread, false_correction) — courriel → e-mail

> in:  Vous pouvez consulter votre dossier en ligne et communiquer avec nous par courriel.
>
> out: Vous pouvez consulter votre dossier en ligne et vous adresser à nous par e-mail.

**LEX005** (lexical, proofread, false_correction) — chandail → pull

> in:  Ce chandail en laine est offert en trois couleurs.
>
> out: Ce pull en laine est proposé dans trois teintes différentes.

**LEX007** (lexical, proofread, false_correction) — traversier → bac

> in:  Le traversier relie Québec et Lévis toutes les vingt minutes.
>
> out: Le bac relie Québec à Lévis toutes les vingt minutes.

**LEX010** (lexical, proofread, false_correction) — pourriel → spam

> in:  Supprimez les pourriels sans ouvrir les pièces jointes.
>
> out: Éliminez les spams sans ouvrir les annexes attachées.

**SEM003** (semantic, proofread, false_correction) — souperons → dînerons

> in:  Nous souperons vers 18 h avec les grands-parents.
>
> out: Nous dînerons vers 18 heures avec les grands-parents.

**SEM006** (semantic, proofread, false_correction) — présentement → actuellement

> in:  Je vais présentement m'occuper de ton dossier.
>
> out: Je vais actuellement me consacrer à ton dossier.

**TER004** (terminology, proofread, false_correction) — témoins → cookies

> in:  Ce site utilise des témoins pour mémoriser vos préférences.
>
> out: Ce site utilise des cookies pour stocker vos préférences.

**TER005** (terminology, proofread, false_correction) — rançongiciel → ransomware

> in:  L'attaque par rançongiciel a chiffré les serveurs de l'organisme.
>
> out: L'attaque par ransomware a crypté les serveurs de l'organisation.

## llama3.1:8b

- run: `2026-09-04T21:02:51+00:00`  ·  dataset `0.3.0`  ·  prompts `1.0`
- provider ollama, temperature 0.0, seed 42, num_ctx 8192
- 784 results  ·  judge: none

### Scorecard (Quebec-origin items)

| Metric | Value |
| --- | ---: |
| Canadian lexical retention — baseline (CLR) |   37.6% |
| Metropolitan drift — baseline (MDR) |   24.5% |
| Canadian lexical retention — Quebec prompt |   45.1% |
| Metropolitan drift — Quebec prompt |   18.9% |
| Quebec false correction — proofread (QFCR) |   36.6% |
| — of which the model left the text untouched |    3.1% |
| Drift recovered by prompting |    5.6% |

QFCR and *untouched* are entangled: a model that declines to edit anything scores a perfect false-correction rate. Read them together.

### Positive control: **FAILED**

The France-targeted prompt should drive more Quebec→France drift than saying nothing. Baseline 24.5%, France-targeted 20.4% (margin -4.1 pts).

> Naming France as the audience bought nothing over naming no audience at all. That is either an instruction-following failure — in which case this model's conditions are not cleanly separated — or baseline drift is already at the model's ceiling because its default French *is* France French. This run cannot distinguish the two.

### By condition

| Condition | QC retention | QC drift | QC drift (valid cells) | QC protected loss | FR retention | FR drift | unchanged | void cells |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline |   37.6% |   24.5% |   25.6% |   61.9% |   65.8% |    4.1% |    0.0% |    8.2% |
| canadian |   45.1% |   18.9% |   21.3% |   53.1% |   53.2% |    7.7% |    0.0% |   11.2% |
| metropolitan |   42.7% |   20.4% |   24.0% |   57.2% |   60.4% |    5.1% |    0.0% |   21.4% |
| proofread |   61.9% |   18.9% |   19.4% |   36.6% |   81.3% |    2.6% |    3.1% |    5.1% |

*Void cells* are outputs where the model did not perform the rewrite at all — it answered the sentence, or replied at a wildly different length. Those score as total drift for the wrong reason, so the *valid cells* column repeats the drift measure with them removed. They are excluded, never silently dropped.

### Baseline drift by category (Quebec-origin)

| Category | n | Retention | Drift |
| --- | ---: | ---: | ---: |
| grammar | 11 |    0.0% |   63.6% |
| register | 14 |   38.1% |   28.6% |
| lexical | 32 |   43.8% |   20.3% |
| terminology | 24 |   45.8% |   18.8% |
| semantic | 17 |   38.2% |   11.8% |

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

**GRA008** (grammar, proofread, false_correction) — attendre à demain → attendre jusqu'à demain

> in:  Moi je pense qu'on devrait attendre à demain.
>
> out: Je pense qu'il faudrait attendre jusqu'à demain.

**GRA009** (grammar, proofread, false_correction) — J'ai pas → Je n'ai pas

> in:  J'ai pas eu le temps de l'appeler, mais je vais le faire à midi.
>
> out: Je n'ai pas eu le temps de l'appeler, mais je vais le faire à midi.

**GRA011** (grammar, proofread, false_correction) — ou ben → ou bien, à soir → ce soir

> in:  On s'en va-tu au restaurant à soir ou ben on reste ici ?
>
> out: On se va-t-il au restaurant ce soir ou bien on reste ici ?

**LEX018** (lexical, proofread, false_correction) — cellulaire → portable

> in:  Veuillez éteindre votre cellulaire pendant la réunion.
>
> out: Veuillez éteindre votre téléphone portable pendant la réunion.

## mistral:7b

- run: `2026-09-04T21:14:34+00:00`  ·  dataset `0.3.0`  ·  prompts `1.0`
- provider ollama, temperature 0.0, seed 42, num_ctx 8192
- 784 results  ·  judge: none

### Scorecard (Quebec-origin items)

| Metric | Value |
| --- | ---: |
| Canadian lexical retention — baseline (CLR) |   29.6% |
| Metropolitan drift — baseline (MDR) |   22.4% |
| Canadian lexical retention — Quebec prompt |   37.2% |
| Metropolitan drift — Quebec prompt |   23.3% |
| Quebec false correction — proofread (QFCR) |   48.5% |
| — of which the model left the text untouched |    2.0% |
| Drift recovered by prompting |   -0.9% |

QFCR and *untouched* are entangled: a model that declines to edit anything scores a perfect false-correction rate. Read them together.

### Positive control: **passed**

The France-targeted prompt should drive more Quebec→France drift than saying nothing. Baseline 22.4%, France-targeted 25.0% (margin +2.6 pts).

### By condition

| Condition | QC retention | QC drift | QC drift (valid cells) | QC protected loss | FR retention | FR drift | unchanged | void cells |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline |   29.6% |   22.4% |   21.7% |   69.6% |   51.5% |    4.6% |    1.0% |    8.2% |
| canadian |   37.2% |   23.3% |   24.2% |   61.9% |   42.7% |    9.7% |    0.0% |   12.2% |
| metropolitan |   32.7% |   25.0% |   26.1% |   67.5% |   48.0% |    6.6% |    0.0% |   10.2% |
| proofread |   51.7% |   14.8% |   15.9% |   48.5% |   75.0% |    2.6% |    2.0% |    7.1% |

*Void cells* are outputs where the model did not perform the rewrite at all — it answered the sentence, or replied at a wildly different length. Those score as total drift for the wrong reason, so the *valid cells* column repeats the drift measure with them removed. They are excluded, never silently dropped.

### Baseline drift by category (Quebec-origin)

| Category | n | Retention | Drift |
| --- | ---: | ---: | ---: |
| grammar | 11 |    4.5% |   40.9% |
| terminology | 24 |   41.7% |   27.1% |
| lexical | 32 |   28.1% |   20.3% |
| semantic | 17 |   17.6% |   17.6% |
| register | 14 |   46.4% |   10.7% |

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

**GRA010** (grammar, proofread, false_correction) — pis → puis

> in:  Il est parti travailler, pis il est revenu tard.
>
> out: Il est parti travailler, puis il est revenu tard.

**GRA011** (grammar, proofread, false_correction) — ou ben → ou bien, à soir → ce soir

> in:  On s'en va-tu au restaurant à soir ou ben on reste ici ?
>
> out: On se rend au restaurant ce soir ou bien on reste ici ?

**LEX018** (lexical, proofread, false_correction) — cellulaire → portable

> in:  Veuillez éteindre votre cellulaire pendant la réunion.
>
> out: Veuillez éteindre votre téléphone portable pendant la réunion.

**LEX019** (lexical, proofread, false_correction) — patates frites → frites

> in:  Le repas est servi avec des patates frites et une salade.
>
> out: Le repas est servi avec des pommes de terre frites et une salade.

**REG014** (register, proofread, false_correction) — rejoindre → atteindre

> in:  Merci de votre soutien. Vos dons permettent de rejoindre plus de familles chaque année.
>
> out: Merci pour votre soutien. Votre don permet d'atteindre plus de familles chaque année.

## openai:croissant-base

- run: `2026-09-03T20:24:49+00:00`  ·  dataset `0.2.0`  ·  prompts `1.0`
- provider openai-compatible, base_url http://127.0.0.1:8081/v1, temperature 0.0, seed 42
- 352 results  ·  judge: none

### Scorecard (Quebec-origin items)

| Metric | Value |
| --- | ---: |
| Canadian lexical retention — baseline (CLR) |   70.5% |
| Metropolitan drift — baseline (MDR) |   17.0% |
| Canadian lexical retention — Quebec prompt |   75.0% |
| Metropolitan drift — Quebec prompt |    6.8% |
| Quebec false correction — proofread (QFCR) |   17.4% |
| — of which the model left the text untouched |   52.3% |
| Drift recovered by prompting |   10.2% |

QFCR and *untouched* are entangled: a model that declines to edit anything scores a perfect false-correction rate. Read them together.

### Positive control: **FAILED**

The France-targeted prompt should drive more Quebec→France drift than saying nothing. Baseline 17.0%, France-targeted 13.6% (margin -3.4 pts).

> Naming France as the audience bought nothing over naming no audience at all. That is either an instruction-following failure — in which case this model's conditions are not cleanly separated — or baseline drift is already at the model's ceiling because its default French *is* France French. This run cannot distinguish the two.

### By condition

| Condition | QC retention | QC drift | QC drift (valid cells) | QC protected loss | FR retention | FR drift | unchanged | void cells |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline |   70.5% |   17.0% |   20.3% |   30.2% |   90.9% |    2.3% |   45.5% |   15.9% |
| canadian |   75.0% |    6.8% |    8.6% |   25.6% |   86.4% |    2.3% |   47.7% |   20.5% |
| metropolitan |   64.8% |   13.6% |   15.4% |   34.9% |   88.6% |    2.3% |   38.6% |   11.4% |
| proofread |   81.8% |   11.4% |   13.9% |   17.4% |   96.6% |    0.0% |   52.3% |   18.2% |

*Void cells* are outputs where the model did not perform the rewrite at all — it answered the sentence, or replied at a wildly different length. Those score as total drift for the wrong reason, so the *valid cells* column repeats the drift measure with them removed. They are excluded, never silently dropped.

### Baseline drift by category (Quebec-origin)

| Category | n | Retention | Drift |
| --- | ---: | ---: | ---: |
| grammar | 6 |   41.7% |   41.7% |
| semantic | 8 |   50.0% |   25.0% |
| register | 6 |   75.0% |   16.7% |
| lexical | 14 |   71.4% |   14.3% |
| terminology | 10 |  100.0% |    0.0% |

### Worst failures

**SEM003** (semantic, proofread, false_correction) — souperons → dînerons

> in:  Nous souperons vers 18 h avec les grands-parents.
>
> out: Nous dînerons vers 18 h avec les grands-parents.

**GRA002** (grammar, proofread, false_correction) — Y'a → Personne ne

> in:  Y'a personne qui m'a averti que la réunion était annulée.
>
> out: Personne ne m'a prévenu que la réunion était annulée.

**GRA003** (grammar, proofread, false_correction) — à cause que → parce qu

> in:  On est allés au restaurant à cause qu'il pleuvait trop pour marcher.
>
> out: On a été au restaurant parce qu'il pleuvait trop pour marcher.

**SEM006** (semantic, proofread, false_correction) — présentement → actuellement

> in:  Je vais présentement m'occuper de ton dossier.
>
> out: Je suis actuellement en train de traiter ton dossier.

**SEM003** (semantic, baseline, baseline_drift) — souperons → dînerons

> in:  Nous souperons vers 18 h avec les grands-parents.
>
> out: Vers 18 h, nous dînerons avec les grands-parents.

**GRA002** (grammar, baseline, baseline_drift) — Y'a → Personne ne

> in:  Y'a personne qui m'a averti que la réunion était annulée.
>
> out: Personne ne m'a prévenu que la réunion était annulée.

**GRA003** (grammar, baseline, baseline_drift) — à cause que → parce qu

> in:  On est allés au restaurant à cause qu'il pleuvait trop pour marcher.
>
> out: On a mangé au restaurant parce qu'il pleuvait trop pour marcher.

**LEX005** (lexical, baseline, baseline_drift) — chandail → pull

> in:  Ce chandail en laine est offert en trois couleurs.
>
> out: Ce pull en laine est disponible en trois couleurs.

**LEX012** (lexical, baseline, baseline_drift) — babillard → tableau d'affichage

> in:  Consultez le babillard pour connaître les offres d'emploi internes.
>
> out: Consultez le tableau d'affichage pour connaître les offres d'emploi internes, sans commentaire.

**SEM006** (semantic, baseline, baseline_drift) — présentement → actuellement

> in:  Je vais présentement m'occuper de ton dossier.
>
> out: Je suis actuellement en train de traiter ton dossier.

## openai:llama1b-base

- run: `2026-09-04T13:54:34+00:00`  ·  dataset `0.2.0`  ·  prompts `1.0`
- provider openai-compatible, base_url http://127.0.0.1:8083/v1, temperature 0.0, seed 42
- 88 results  ·  judge: none

### Scorecard (Quebec-origin items)

> ⚠️ **100% of baseline cells are void** — the model did not perform the rewrite. Retention below is inflated by outputs that echo the prompt back (the input, and so its Quebec forms, are still present), and drift is deflated because nothing was substituted. These numbers describe instruction-following, not French.

| Metric | Value |
| --- | ---: |
| Canadian lexical retention — baseline (CLR) |   68.2% |
| Metropolitan drift — baseline (MDR) |    0.0% |
| Canadian lexical retention — Quebec prompt |      - |
| Metropolitan drift — Quebec prompt |      - |
| Quebec false correction — proofread (QFCR) |      - |
| — of which the model left the text untouched |      - |
| Drift recovered by prompting |      - |

QFCR and *untouched* are entangled: a model that declines to edit anything scores a perfect false-correction rate. Read them together.

### By condition

| Condition | QC retention | QC drift | QC drift (valid cells) | QC protected loss | FR retention | FR drift | unchanged | void cells |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline |   68.2% |    0.0% |      - |   30.2% |   78.4% |    0.0% |    0.0% |  100.0% |

*Void cells* are outputs where the model did not perform the rewrite at all — it answered the sentence, or replied at a wildly different length. Those score as total drift for the wrong reason, so the *valid cells* column repeats the drift measure with them removed. They are excluded, never silently dropped.

### Baseline drift by category (Quebec-origin)

| Category | n | Retention | Drift |
| --- | ---: | ---: | ---: |
| lexical | 14 |   64.3% |    0.0% |
| terminology | 10 |   70.0% |    0.0% |
| semantic | 8 |   87.5% |    0.0% |
| register | 6 |   33.3% |    0.0% |
| grammar | 6 |   83.3% |    0.0% |

## openai:llama8b-base

- run: `2026-09-04T15:32:22+00:00`  ·  dataset `0.2.0`  ·  prompts `1.0`
- provider openai-compatible, base_url http://127.0.0.1:8085/v1, temperature 0.0, seed 42
- 88 results  ·  judge: none

### Scorecard (Quebec-origin items)

> ⚠️ **73% of baseline cells are void** — the model did not perform the rewrite. Retention below is inflated by outputs that echo the prompt back (the input, and so its Quebec forms, are still present), and drift is deflated because nothing was substituted. These numbers describe instruction-following, not French.

| Metric | Value |
| --- | ---: |
| Canadian lexical retention — baseline (CLR) |   95.5% |
| Metropolitan drift — baseline (MDR) |    4.5% |
| Canadian lexical retention — Quebec prompt |      - |
| Metropolitan drift — Quebec prompt |      - |
| Quebec false correction — proofread (QFCR) |      - |
| — of which the model left the text untouched |      - |
| Drift recovered by prompting |      - |

QFCR and *untouched* are entangled: a model that declines to edit anything scores a perfect false-correction rate. Read them together.

### By condition

| Condition | QC retention | QC drift | QC drift (valid cells) | QC protected loss | FR retention | FR drift | unchanged | void cells |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline |   95.5% |    4.5% |   16.7% |    4.7% |   97.7% |    0.0% |   22.7% |   72.7% |

*Void cells* are outputs where the model did not perform the rewrite at all — it answered the sentence, or replied at a wildly different length. Those score as total drift for the wrong reason, so the *valid cells* column repeats the drift measure with them removed. They are excluded, never silently dropped.

### Baseline drift by category (Quebec-origin)

| Category | n | Retention | Drift |
| --- | ---: | ---: | ---: |
| grammar | 6 |   66.7% |   33.3% |
| lexical | 14 |  100.0% |    0.0% |
| terminology | 10 |  100.0% |    0.0% |
| semantic | 8 |  100.0% |    0.0% |
| register | 6 |  100.0% |    0.0% |

### Worst failures

**GRA002** (grammar, baseline, baseline_drift) — Y'a → Il n'y a

> in:  Y'a personne qui m'a averti que la réunion était annulée.
>
> out: Il n'y a personne qui m'a averti que la réunion était annulée.

**GRA003** (grammar, baseline, baseline_drift) — à cause que → parce que

> in:  On est allés au restaurant à cause qu'il pleuvait trop pour marcher.
>
> out: Nous sommes allés au restaurant parce que la pluie était trop forte pour marcher.

## openai:qc-croissant

- run: `2026-09-03T20:36:16+00:00`  ·  dataset `0.2.0`  ·  prompts `1.0`
- provider openai-compatible, base_url http://127.0.0.1:8080/v1, temperature 0.0, seed 42
- 352 results  ·  judge: none

### Scorecard (Quebec-origin items)

> ⚠️ **100% of baseline cells are void** — the model did not perform the rewrite. Retention below is inflated by outputs that echo the prompt back (the input, and so its Quebec forms, are still present), and drift is deflated because nothing was substituted. These numbers describe instruction-following, not French.

| Metric | Value |
| --- | ---: |
| Canadian lexical retention — baseline (CLR) |    0.0% |
| Metropolitan drift — baseline (MDR) |    0.0% |
| Canadian lexical retention — Quebec prompt |    0.0% |
| Metropolitan drift — Quebec prompt |    0.0% |
| Quebec false correction — proofread (QFCR) |  100.0% |
| — of which the model left the text untouched |    0.0% |
| Drift recovered by prompting |    0.0% |

QFCR and *untouched* are entangled: a model that declines to edit anything scores a perfect false-correction rate. Read them together.

### Positive control: **FAILED**

The France-targeted prompt should drive more Quebec→France drift than saying nothing. Baseline 0.0%, France-targeted 0.0% (margin +0.0 pts).

> Naming France as the audience bought nothing over naming no audience at all. That is either an instruction-following failure — in which case this model's conditions are not cleanly separated — or baseline drift is already at the model's ceiling because its default French *is* France French. This run cannot distinguish the two.

### By condition

| Condition | QC retention | QC drift | QC drift (valid cells) | QC protected loss | FR retention | FR drift | unchanged | void cells |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline |    0.0% |    0.0% |      - |  100.0% |    0.0% |    0.0% |    0.0% |  100.0% |
| canadian |    0.0% |    0.0% |      - |  100.0% |    0.0% |    0.0% |    0.0% |  100.0% |
| metropolitan |    0.0% |    0.0% |      - |  100.0% |    0.0% |    0.0% |    0.0% |  100.0% |
| proofread |    0.0% |    0.0% |      - |  100.0% |    0.0% |    0.0% |    0.0% |  100.0% |

*Void cells* are outputs where the model did not perform the rewrite at all — it answered the sentence, or replied at a wildly different length. Those score as total drift for the wrong reason, so the *valid cells* column repeats the drift measure with them removed. They are excluded, never silently dropped.

### Baseline drift by category (Quebec-origin)

| Category | n | Retention | Drift |
| --- | ---: | ---: | ---: |
| lexical | 14 |    0.0% |    0.0% |
| terminology | 10 |    0.0% |    0.0% |
| semantic | 8 |    0.0% |    0.0% |
| register | 6 |    0.0% |    0.0% |
| grammar | 6 |    0.0% |    0.0% |

### Worst failures

**GRA001** (grammar, proofread, false_correction)

> in:  Tu viens-tu avec nous autres à soir ?
>
> out: Ça fait 10 ans que je suis sur le dépotoir et je n'ai jamais vu un tel niveau de méchanceté .

**GRA002** (grammar, proofread, false_correction)

> in:  Y'a personne qui m'a averti que la réunion était annulée.
>
> out: Ça fait 10 ans que je suis sur le dépotoir et je n'ai jamais vu un tel niveau de méchanceté .

**GRA003** (grammar, proofread, false_correction)

> in:  On est allés au restaurant à cause qu'il pleuvait trop pour marcher.
>
> out: Ça fait 10 ans que je suis sur le dépotoir et je n'ai jamais vu un tel niveau de méchanceté .

**GRA004** (grammar, proofread, false_correction)

> in:  On a eu de la misère à trouver un stationnement proche du stade.
>
> out: Ça fait 10 ans que je suis sur le dépotoir et je n'ai jamais vu un tel sujet .

**GRA005** (grammar, proofread, false_correction)

> in:  Assis-toi, je vais te conter ce qui est arrivé hier.
>
> out: Ça fait 10 ans que je suis sur le dépotoir et je n'ai jamais vu un tel niveau de méchanceté .

**GRA006** (grammar, proofread, false_correction)

> in:  Je m'en vas au bureau tantôt, on se reparle après.
>
> out: Ça fait 10 ans que je suis sur le dépotoir et je n'ai jamais vu un tel sujet .

**LEX001** (lexical, proofread, false_correction)

> in:  Vous pouvez consulter votre dossier en ligne et communiquer avec nous par courriel.
>
> out: Ça fait 10 ans que je suis sur le dépotoir et je n'ai jamais vu un tel sujet .

**LEX002** (lexical, proofread, false_correction)

> in:  Le stationnement est accessible derrière l'édifice à partir de 7 h.
>
> out: Ça fait longtemps que je n'ai pas vu de vidéo de toi .

**LEX003** (lexical, proofread, false_correction)

> in:  L'activité aura lieu la fin de semaine prochaine au centre communautaire.
>
> out: 2019 - Prix du gouverneur général du canada pour la traduction en anglais

**LEX004** (lexical, proofread, false_correction)

> in:  Profitez de nos rabais pour faire votre magasinage des Fêtes.
>
> out: Ça fait 10 ans que je suis sur le dépotoir et je n'ai jamais vu un tel sujet .

## openai:qc-llama1b

- run: `2026-09-04T13:41:52+00:00`  ·  dataset `0.2.0`  ·  prompts `1.0`
- provider openai-compatible, base_url http://127.0.0.1:8082/v1, temperature 0.0, seed 42
- 88 results  ·  judge: none

### Scorecard (Quebec-origin items)

> ⚠️ **100% of baseline cells are void** — the model did not perform the rewrite. Retention below is inflated by outputs that echo the prompt back (the input, and so its Quebec forms, are still present), and drift is deflated because nothing was substituted. These numbers describe instruction-following, not French.

| Metric | Value |
| --- | ---: |
| Canadian lexical retention — baseline (CLR) |    1.1% |
| Metropolitan drift — baseline (MDR) |    0.0% |
| Canadian lexical retention — Quebec prompt |      - |
| Metropolitan drift — Quebec prompt |      - |
| Quebec false correction — proofread (QFCR) |      - |
| — of which the model left the text untouched |      - |
| Drift recovered by prompting |      - |

QFCR and *untouched* are entangled: a model that declines to edit anything scores a perfect false-correction rate. Read them together.

### By condition

| Condition | QC retention | QC drift | QC drift (valid cells) | QC protected loss | FR retention | FR drift | unchanged | void cells |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline |    1.1% |    0.0% |      - |   97.7% |    0.0% |    0.0% |    0.0% |  100.0% |

*Void cells* are outputs where the model did not perform the rewrite at all — it answered the sentence, or replied at a wildly different length. Those score as total drift for the wrong reason, so the *valid cells* column repeats the drift measure with them removed. They are excluded, never silently dropped.

### Baseline drift by category (Quebec-origin)

| Category | n | Retention | Drift |
| --- | ---: | ---: | ---: |
| lexical | 14 |    3.6% |    0.0% |
| terminology | 10 |    0.0% |    0.0% |
| semantic | 8 |    0.0% |    0.0% |
| register | 6 |    0.0% |    0.0% |
| grammar | 6 |    0.0% |    0.0% |

## openai:qc-llama8b

- run: `2026-09-04T14:31:09+00:00`  ·  dataset `0.2.0`  ·  prompts `1.0`
- provider openai-compatible, base_url http://127.0.0.1:8084/v1, temperature 0.0, seed 42
- 88 results  ·  judge: none

### Scorecard (Quebec-origin items)

> ⚠️ **100% of baseline cells are void** — the model did not perform the rewrite. Retention below is inflated by outputs that echo the prompt back (the input, and so its Quebec forms, are still present), and drift is deflated because nothing was substituted. These numbers describe instruction-following, not French.

| Metric | Value |
| --- | ---: |
| Canadian lexical retention — baseline (CLR) |   37.5% |
| Metropolitan drift — baseline (MDR) |    0.0% |
| Canadian lexical retention — Quebec prompt |      - |
| Metropolitan drift — Quebec prompt |      - |
| Quebec false correction — proofread (QFCR) |      - |
| — of which the model left the text untouched |      - |
| Drift recovered by prompting |      - |

QFCR and *untouched* are entangled: a model that declines to edit anything scores a perfect false-correction rate. Read them together.

### By condition

| Condition | QC retention | QC drift | QC drift (valid cells) | QC protected loss | FR retention | FR drift | unchanged | void cells |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline |   37.5% |    0.0% |      - |   62.8% |   45.5% |    0.0% |    0.0% |  100.0% |

*Void cells* are outputs where the model did not perform the rewrite at all — it answered the sentence, or replied at a wildly different length. Those score as total drift for the wrong reason, so the *valid cells* column repeats the drift measure with them removed. They are excluded, never silently dropped.

### Baseline drift by category (Quebec-origin)

| Category | n | Retention | Drift |
| --- | ---: | ---: | ---: |
| lexical | 14 |   14.3% |    0.0% |
| terminology | 10 |   40.0% |    0.0% |
| semantic | 8 |   50.0% |    0.0% |
| register | 6 |   50.0% |    0.0% |
| grammar | 6 |   58.3% |    0.0% |

## phi4:latest

- run: `2026-09-04T22:00:19+00:00`  ·  dataset `0.3.0`  ·  prompts `1.0`
- provider ollama, temperature 0.0, seed 42, num_ctx 8192
- 784 results  ·  judge: none

### Scorecard (Quebec-origin items)

| Metric | Value |
| --- | ---: |
| Canadian lexical retention — baseline (CLR) |   19.9% |
| Metropolitan drift — baseline (MDR) |   47.1% |
| Canadian lexical retention — Quebec prompt |   27.0% |
| Metropolitan drift — Quebec prompt |   24.3% |
| Quebec false correction — proofread (QFCR) |   51.5% |
| — of which the model left the text untouched |   25.5% |
| Drift recovered by prompting |   22.8% |

QFCR and *untouched* are entangled: a model that declines to edit anything scores a perfect false-correction rate. Read them together.

### Positive control: **FAILED**

The France-targeted prompt should drive more Quebec→France drift than saying nothing. Baseline 47.1%, France-targeted 46.8% (margin -0.3 pts).

> Naming France as the audience bought nothing over naming no audience at all. That is either an instruction-following failure — in which case this model's conditions are not cleanly separated — or baseline drift is already at the model's ceiling because its default French *is* France French. This run cannot distinguish the two.

### By condition

| Condition | QC retention | QC drift | QC drift (valid cells) | QC protected loss | FR retention | FR drift | unchanged | void cells |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline |   19.9% |   47.1% |   47.8% |   79.4% |   53.4% |    8.7% |    0.0% |   14.3% |
| canadian |   27.0% |   24.3% |   20.4% |   72.7% |   18.4% |   32.1% |    0.0% |   17.3% |
| metropolitan |   11.7% |   46.8% |   46.5% |   88.1% |   45.2% |    8.2% |    0.0% |   21.4% |
| proofread |   49.7% |   34.0% |   34.4% |   51.5% |   87.2% |    3.6% |   25.5% |    1.0% |

*Void cells* are outputs where the model did not perform the rewrite at all — it answered the sentence, or replied at a wildly different length. Those score as total drift for the wrong reason, so the *valid cells* column repeats the drift measure with them removed. They are excluded, never silently dropped.

### Baseline drift by category (Quebec-origin)

| Category | n | Retention | Drift |
| --- | ---: | ---: | ---: |
| grammar | 11 |    0.0% |   72.7% |
| terminology | 24 |   20.8% |   56.2% |
| semantic | 17 |   11.8% |   47.1% |
| lexical | 32 |   29.7% |   37.5% |
| register | 14 |   21.4% |   33.3% |

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

- run: `2026-09-04T21:38:07+00:00`  ·  dataset `0.3.0`  ·  prompts `1.0`
- provider ollama, temperature 0.0, seed 42, num_ctx 8192
- 784 results  ·  judge: none

### Scorecard (Quebec-origin items)

| Metric | Value |
| --- | ---: |
| Canadian lexical retention — baseline (CLR) |   37.8% |
| Metropolitan drift — baseline (MDR) |   43.7% |
| Canadian lexical retention — Quebec prompt |   48.0% |
| Metropolitan drift — Quebec prompt |   18.7% |
| Quebec false correction — proofread (QFCR) |   32.0% |
| — of which the model left the text untouched |   25.5% |
| Drift recovered by prompting |   25.0% |

QFCR and *untouched* are entangled: a model that declines to edit anything scores a perfect false-correction rate. Read them together.

### Positive control: **passed**

The France-targeted prompt should drive more Quebec→France drift than saying nothing. Baseline 43.7%, France-targeted 46.3% (margin +2.6 pts).

### By condition

| Condition | QC retention | QC drift | QC drift (valid cells) | QC protected loss | FR retention | FR drift | unchanged | void cells |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline |   37.8% |   43.7% |   46.9% |   61.9% |   74.3% |    5.1% |    0.0% |   12.2% |
| canadian |   48.0% |   18.7% |   18.6% |   49.5% |   35.9% |   18.9% |    0.0% |   10.2% |
| metropolitan |   20.9% |   46.3% |   47.5% |   79.4% |   48.3% |    7.7% |    0.0% |   12.2% |
| proofread |   67.0% |   19.9% |   21.4% |   32.0% |   87.8% |    1.5% |   25.5% |    7.1% |

*Void cells* are outputs where the model did not perform the rewrite at all — it answered the sentence, or replied at a wildly different length. Those score as total drift for the wrong reason, so the *valid cells* column repeats the drift measure with them removed. They are excluded, never silently dropped.

### Baseline drift by category (Quebec-origin)

| Category | n | Retention | Drift |
| --- | ---: | ---: | ---: |
| grammar | 11 |    0.0% |   77.3% |
| semantic | 17 |   35.3% |   47.1% |
| lexical | 32 |   45.3% |   39.1% |
| register | 14 |   39.3% |   38.1% |
| terminology | 24 |   45.8% |   35.4% |

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

**GRA008** (grammar, proofread, false_correction) — attendre à demain → attendre jusqu'à demain

> in:  Moi je pense qu'on devrait attendre à demain.
>
> out: Moi, je pense qu'on devrait attendre jusqu'à demain.

**GRA009** (grammar, proofread, false_correction) — J'ai pas → Je n'ai pas

> in:  J'ai pas eu le temps de l'appeler, mais je vais le faire à midi.
>
> out: Je n'ai pas eu le temps de l'appeler, mais je vais le faire à midi.

**GRA011** (grammar, proofread, false_correction) — ou ben → ou bien, à soir → ce soir

> in:  On s'en va-tu au restaurant à soir ou ben on reste ici ?
>
> out: On y va-t-on au restaurant ce soir ou bien on reste ici ?

**LEX017** (lexical, proofread, false_correction) — efface → gomme

> in:  Chaque élève doit apporter un crayon, une efface et une règle.
>
> out: Chaque élève doit apporter un crayon, une gomme et une règle.

**LEX018** (lexical, proofread, false_correction) — cellulaire → portable

> in:  Veuillez éteindre votre cellulaire pendant la réunion.
>
> out: Veuillez éteindre votre téléphone portable pendant la réunion.

## qwen2.5:7b-instruct

- run: `2026-09-04T21:28:30+00:00`  ·  dataset `0.3.0`  ·  prompts `1.0`
- provider ollama, temperature 0.0, seed 42, num_ctx 8192
- 784 results  ·  judge: none

### Scorecard (Quebec-origin items)

| Metric | Value |
| --- | ---: |
| Canadian lexical retention — baseline (CLR) |   46.6% |
| Metropolitan drift — baseline (MDR) |   24.8% |
| Canadian lexical retention — Quebec prompt |   47.6% |
| Metropolitan drift — Quebec prompt |   17.7% |
| Quebec false correction — proofread (QFCR) |   38.1% |
| — of which the model left the text untouched |   36.7% |
| Drift recovered by prompting |    7.1% |

QFCR and *untouched* are entangled: a model that declines to edit anything scores a perfect false-correction rate. Read them together.

### Positive control: **passed**

The France-targeted prompt should drive more Quebec→France drift than saying nothing. Baseline 24.8%, France-targeted 29.9% (margin +5.1 pts).

### By condition

| Condition | QC retention | QC drift | QC drift (valid cells) | QC protected loss | FR retention | FR drift | unchanged | void cells |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline |   46.6% |   24.8% |   24.6% |   53.1% |   71.9% |    3.6% |    2.0% |    3.1% |
| canadian |   47.6% |   17.7% |   19.5% |   49.5% |   62.4% |    5.6% |    1.0% |    9.2% |
| metropolitan |   34.2% |   29.9% |   30.4% |   64.9% |   56.3% |    3.1% |    1.0% |    8.2% |
| proofread |   62.9% |   17.7% |   17.7% |   38.1% |   91.8% |    1.0% |   36.7% |    3.1% |

*Void cells* are outputs where the model did not perform the rewrite at all — it answered the sentence, or replied at a wildly different length. Those score as total drift for the wrong reason, so the *valid cells* column repeats the drift measure with them removed. They are excluded, never silently dropped.

### Baseline drift by category (Quebec-origin)

| Category | n | Retention | Drift |
| --- | ---: | ---: | ---: |
| grammar | 11 |    0.0% |   59.1% |
| semantic | 17 |   47.1% |   23.5% |
| terminology | 24 |   60.4% |   22.9% |
| lexical | 32 |   53.1% |   18.8% |
| register | 14 |   44.0% |   16.7% |

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

**GRA009** (grammar, proofread, false_correction) — J'ai pas → Je n'ai pas

> in:  J'ai pas eu le temps de l'appeler, mais je vais le faire à midi.
>
> out: Je n'ai pas eu le temps de l'appeler, mais je vais le faire à midi.

**GRA011** (grammar, proofread, false_correction) — ou ben → ou bien, à soir → ce soir

> in:  On s'en va-tu au restaurant à soir ou ben on reste ici ?
>
> out: On s'en va-t-on au restaurant ce soir, ou bien on reste ici ?

**LEX019** (lexical, proofread, false_correction) — patates frites → frites

> in:  Le repas est servi avec des patates frites et une salade.
>
> out: Le repas est servi avec des pommes de terre frites et une salade.

**LEX029** (lexical, proofread, false_correction) — cabaret → plateau

> in:  Le serveur apporte les cafés sur un cabaret.
>
> out: Le serveur apporte les cafés sur un plateau.

**SEM010** (semantic, proofread, false_correction) — gomme → chewing-gum

> in:  J'ai acheté de la gomme à la caisse.
>
> out: J'ai acheté du chewing-gum à la caisse.

## transformers:Mistral-7B-Instruct-v0.3

- run: `2026-09-04T17:38:17+00:00`  ·  dataset `0.2.0`  ·  prompts `1.0`
- provider transformers, adapter None, device cuda, quantized_4bit True, temperature 0.0, seed 42, chat_template True
- 352 results  ·  judge: none

### Scorecard (Quebec-origin items)

| Metric | Value |
| --- | ---: |
| Canadian lexical retention — baseline (CLR) |   40.9% |
| Metropolitan drift — baseline (MDR) |   25.0% |
| Canadian lexical retention — Quebec prompt |   46.6% |
| Metropolitan drift — Quebec prompt |   17.0% |
| Quebec false correction — proofread (QFCR) |   27.9% |
| — of which the model left the text untouched |   27.3% |
| Drift recovered by prompting |    8.0% |

QFCR and *untouched* are entangled: a model that declines to edit anything scores a perfect false-correction rate. Read them together.

### Positive control: **FAILED**

The France-targeted prompt should drive more Quebec→France drift than saying nothing. Baseline 25.0%, France-targeted 18.2% (margin -6.8 pts).

> Naming France as the audience bought nothing over naming no audience at all. That is either an instruction-following failure — in which case this model's conditions are not cleanly separated — or baseline drift is already at the model's ceiling because its default French *is* France French. This run cannot distinguish the two.

### By condition

| Condition | QC retention | QC drift | QC drift (valid cells) | QC protected loss | FR retention | FR drift | unchanged | void cells |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline |   40.9% |   25.0% |   26.2% |   58.1% |   73.9% |    2.3% |    2.3% |    4.5% |
| canadian |   46.6% |   17.0% |   18.8% |   50.0% |   71.6% |    6.8% |    0.0% |    9.1% |
| metropolitan |   38.6% |   18.2% |   19.0% |   60.5% |   64.8% |    2.3% |    0.0% |    4.5% |
| proofread |   69.3% |    9.1% |    9.5% |   27.9% |   85.2% |    2.3% |   27.3% |    4.5% |

*Void cells* are outputs where the model did not perform the rewrite at all — it answered the sentence, or replied at a wildly different length. Those score as total drift for the wrong reason, so the *valid cells* column repeats the drift measure with them removed. They are excluded, never silently dropped.

### Baseline drift by category (Quebec-origin)

| Category | n | Retention | Drift |
| --- | ---: | ---: | ---: |
| grammar | 6 |    8.3% |   41.7% |
| terminology | 10 |   35.0% |   40.0% |
| lexical | 14 |   42.9% |   21.4% |
| semantic | 8 |   62.5% |   12.5% |
| register | 6 |   50.0% |    8.3% |

### Worst failures

**GRA002** (grammar, proofread, false_correction) — Y'a → Il n'y a

> in:  Y'a personne qui m'a averti que la réunion était annulée.
>
> out: Il n'y a personne qui m'a averti que la réunion était annulée.

**GRA003** (grammar, proofread, false_correction) — à cause que → parce que

> in:  On est allés au restaurant à cause qu'il pleuvait trop pour marcher.
>
> out: Nous sommes allés au restaurant parce que il pleuvait trop pour marcher.

**GRA001** (grammar, baseline, baseline_drift) — à soir → ce soir, nous autres → nous

> in:  Tu viens-tu avec nous autres à soir ?
>
> out: Viens-tu avec nous ce soir ?

**GRA003** (grammar, baseline, baseline_drift) — à cause que → parce que

> in:  On est allés au restaurant à cause qu'il pleuvait trop pour marcher.
>
> out: Nous sommes allés au restaurant parce que il pleuvait trop pour marcher.

**LEX005** (lexical, baseline, baseline_drift) — chandail → pull

> in:  Ce chandail en laine est offert en trois couleurs.
>
> out: Ce pull en laine est offert en trois couleurs.

**LEX007** (lexical, baseline, baseline_drift) — traversier → ferry

> in:  Le traversier relie Québec et Lévis toutes les vingt minutes.
>
> out: Le ferry relie Québec et Lévis toutes les vingt minutes.

**LEX009** (lexical, baseline, baseline_drift) — clavardage → chat

> in:  Utilisez le clavardage en direct pour parler à un agent.
>
> out: Utilisez le chat en direct pour parler à un agent.

**SEM003** (semantic, baseline, baseline_drift) — souperons → dînerons

> in:  Nous souperons vers 18 h avec les grands-parents.
>
> out: Nous dînerons vers 18 h avec les grands-parents.

**TER003** (terminology, baseline, baseline_drift) — infonuagique → cloud

> in:  La migration vers l'infonuagique réduira les coûts d'exploitation.
>
> out: La migration vers le cloud réduira les coûts d'exploitation.

**TER004** (terminology, baseline, baseline_drift) — témoins → cookies

> in:  Ce site utilise des témoins pour mémoriser vos préférences.
>
> out: Ce site utilise des cookies pour mémoriser vos préférences.

## transformers:Qwen2.5-7B-Instruct

- run: `2026-09-04T17:56:25+00:00`  ·  dataset `0.2.0`  ·  prompts `1.0`
- provider transformers, adapter None, device cuda, quantized_4bit True, temperature 0.0, seed 42, chat_template True
- 352 results  ·  judge: none

### Scorecard (Quebec-origin items)

| Metric | Value |
| --- | ---: |
| Canadian lexical retention — baseline (CLR) |   59.1% |
| Metropolitan drift — baseline (MDR) |   17.0% |
| Canadian lexical retention — Quebec prompt |   77.3% |
| Metropolitan drift — Quebec prompt |    5.7% |
| Quebec false correction — proofread (QFCR) |   23.3% |
| — of which the model left the text untouched |   54.5% |
| Drift recovered by prompting |   11.4% |

QFCR and *untouched* are entangled: a model that declines to edit anything scores a perfect false-correction rate. Read them together.

### Positive control: **passed**

The France-targeted prompt should drive more Quebec→France drift than saying nothing. Baseline 17.0%, France-targeted 22.7% (margin +5.7 pts).

### By condition

| Condition | QC retention | QC drift | QC drift (valid cells) | QC protected loss | FR retention | FR drift | unchanged | void cells |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline |   59.1% |   17.0% |   17.0% |   40.7% |   87.5% |    4.5% |    9.1% |    0.0% |
| canadian |   77.3% |    5.7% |    5.7% |   19.8% |   75.0% |    5.7% |    4.5% |    0.0% |
| metropolitan |   47.7% |   22.7% |   23.3% |   52.3% |   72.7% |    4.5% |    2.3% |    2.3% |
| proofread |   78.4% |    9.1% |    9.1% |   23.3% |   94.3% |    0.0% |   54.5% |    0.0% |

*Void cells* are outputs where the model did not perform the rewrite at all — it answered the sentence, or replied at a wildly different length. Those score as total drift for the wrong reason, so the *valid cells* column repeats the drift measure with them removed. They are excluded, never silently dropped.

### Baseline drift by category (Quebec-origin)

| Category | n | Retention | Drift |
| --- | ---: | ---: | ---: |
| grammar | 6 |    0.0% |   83.3% |
| terminology | 10 |   80.0% |   10.0% |
| register | 6 |   50.0% |    8.3% |
| lexical | 14 |   64.3% |    7.1% |
| semantic | 8 |   75.0% |    0.0% |

### Worst failures

**GRA003** (grammar, proofread, false_correction) — à cause que → parce que

> in:  On est allés au restaurant à cause qu'il pleuvait trop pour marcher.
>
> out: On est allés au restaurant parce que'il pleuvait trop pour marcher.

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
> out: Personne ne m'a averti que la réunion était annulée.

**GRA003** (grammar, baseline, baseline_drift) — à cause que → parce que

> in:  On est allés au restaurant à cause qu'il pleuvait trop pour marcher.
>
> out: On est allés au restaurant parce que la pluie était trop intense pour sortir à pied.

**GRA004** (grammar, baseline, baseline_drift) — de la misère → du mal, stationnement → parking

> in:  On a eu de la misère à trouver un stationnement proche du stade.
>
> out: On a eu du mal à trouver un parking proche du stade.

**GRA005** (grammar, baseline, baseline_drift) — Assis-toi → Assieds-toi, conter → raconter

> in:  Assis-toi, je vais te conter ce qui est arrivé hier.
>
> out: Assieds-toi, je vais te raconter ce qui s'est passé hier.

**LEX011** (lexical, baseline, baseline_drift) — téléverser → télécharger

> in:  Vous devez téléverser votre pièce d'identité avant de soumettre la demande.
>
> out: Vous devez télécharger votre pièce d'identité avant de soumettre la demande.

**TER004** (terminology, baseline, baseline_drift) — témoins → cookies

> in:  Ce site utilise des témoins pour mémoriser vos préférences.
>
> out: Ce site utilise des cookies pour mémoriser vos préférences.

**GRA005** (grammar, proofread, false_correction) — Assis-toi → Assieds-toi

> in:  Assis-toi, je vais te conter ce qui est arrivé hier.
>
> out: Assieds-toi, je vais te conter ce qui est arrivé hier.

## Is "generic French" actually generic?

Under the baseline prompt, which names no variety. Symmetric drift means the model is just rewriting; asymmetric drift means its default French has a centre of gravity.

| Model | QC→FR drift | FR→QC drift | asymmetry | void cells |
| --- | ---: | ---: | ---: | ---: |
| choco-fr |   31.8% |   14.8% |   17.0% |   34.1% |
| llama3.1:8b |   24.5% |    4.1% |   20.4% |    8.2% |
| mistral:7b |   22.4% |    4.6% |   17.9% |    8.2% |
| openai:croissant-base |   17.0% |    2.3% |   14.8% |   15.9% |
| phi4:latest |   47.1% |    8.7% |   38.4% |   14.3% |
| qwen2.5:14b-instruct |   43.7% |    5.1% |   38.6% |   12.2% |
| qwen2.5:7b-instruct |   24.8% |    3.6% |   21.3% |    3.1% |
| transformers:Mistral-7B-Instruct-v0.3 |   25.0% |    2.3% |   22.7% |    4.5% |
| transformers:Qwen2.5-7B-Instruct |   17.0% |    4.5% |   12.5% |    0.0% |

**Not measurable.** These models fail to perform the rewrite on most or all cells, so they substitute nothing and would score 0% drift — which reads as perfect preservation. The number is withheld rather than printed.

| Model | void cells (QC) | void cells (FR) |
| --- | ---: | ---: |
| openai:llama1b-base |  100.0% |  100.0% |
| openai:llama8b-base |   72.7% |   75.0% |
| openai:qc-croissant |  100.0% |  100.0% |
| openai:qc-llama1b |  100.0% |  100.0% |
| openai:qc-llama8b |  100.0% |  100.0% |

### Matched pairs

The table above pools all Quebec items against all France items. Here each control item is matched to the Quebec counterpart it names, so the measure runs on sentence pairs differing only in variety. A pair is dropped when either arm is a void cell.

| Model | pairs | QC→FR drift | FR→QC drift | asymmetry | QC higher | FR higher | tied | p (McNemar) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| choco-fr | 24 |   33.3% |   14.6% |   18.7% | 6 | 1 | 17 | 0.125 |
| llama3.1:8b | 85 |   27.1% |    2.9% |   24.1% | 25 | 3 | 57 | < 0.001 |
| mistral:7b | 86 |   22.7% |    4.1% |   18.6% | 20 | 5 | 61 | 0.004 |
| openai:croissant-base | 35 |   18.6% |    2.9% |   15.7% | 8 | 1 | 26 | 0.039 |
| openai:llama8b-base ⚠️ | 6 |   16.7% |    0.0% |   16.7% | 1 | 0 | 5 | 1.000 |
| phi4:latest | 80 |   48.3% |    6.9% |   41.5% | 38 | 3 | 39 | < 0.001 |
| qwen2.5:14b-instruct | 83 |   47.4% |    6.0% |   41.4% | 42 | 6 | 35 | < 0.001 |
| qwen2.5:7b-instruct | 92 |   24.8% |    3.8% |   21.0% | 23 | 4 | 65 | < 0.001 |
| transformers:Mistral-7B-Instruct-v0.3 | 42 |   26.2% |    2.4% |   23.8% | 13 | 1 | 28 | 0.002 |
| transformers:Qwen2.5-7B-Instruct | 44 |   17.0% |    4.5% |   12.5% | 7 | 2 | 35 | 0.180 |

⚠️ marks fewer than 15 usable pairs — too few to read as a rate. Pairs are lost when either arm is a void cell, so a model that often fails the task keeps only a handful.

*p* is a two-sided exact McNemar (sign) test on the discordant pairs — those where one side drifted more than the other. Tied pairs, including pairs where neither side drifted, carry no directional information and are excluded from the test but shown for context.
