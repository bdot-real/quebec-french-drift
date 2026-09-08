import json
import re
import unicodedata
from typing import List, Dict, Tuple, Optional

class DialectMetricsCalculator:
    """
    A diagnostic calculator to measure dialect drift in Canadian French AI deployments.
    Calculates:
    - Metropolitan Drift Rate (MDR): How often Quebec terms are replaced by their Metropolitan equivalents.
    - Quebec False Correction Rate (QFCR): How often valid Quebec terms are removed under proofreading constraints.
    """

    def __init__(self):
        # Compiled patterns for normalization
        self.apos_pattern = re.compile(r"['’‘`’]")

    def normalize_text(self, text: str) -> str:
        """
        Normalizes French text to prevent false mismatches due to unicode encoding, 
        typographic apostrophes, accents, casing, and trailing whitespace.
        """
        if not text:
            return ""
        # 1. Unicode Normalization (NFC)
        text = unicodedata.normalize("NFC", text)
        # 2. Lowercase
        text = text.lower()
        # 3. Standardize apostrophes
        text = self.apos_pattern.sub("'", text)
        # 4. Standardize whitespace
        text = " ".join(text.split())
        return text

    def has_term(self, text: str, term: str) -> bool:
        """
        Checks if a specific term exists in normalized text, respecting word boundaries
        and French-specific contractions (e.g., l'courriel, d'assurance-emploi).
        """
        norm_text = self.normalize_text(text)
        norm_term = self.normalize_text(term)
        
        if not norm_term:
            return False

        # Escape the term for regex
        escaped_term = re.escape(norm_term)

        # In French, word boundaries (\b) can fail on apostrophes (e.g., \bcourriel\b doesn't match l'courriel correctly 
        # or e-mail contains a hyphen which affects \b).
        # We construct a custom boundary matcher: the term must be preceded and followed by non-alphanumeric characters 
        # or start/end of string, allowing straight apostrophes to act as boundaries as well.
        pattern = r"(?:^|[^a-zA-Z0-9àâäéèêëîïôöùûüç])" + escaped_term + r"(?:$|[^a-zA-Z0-9àâäéèêëîïôöùûüç])"
        
        match = re.search(pattern, norm_text)
        return match is not None

    def calculate_metrics(self, data: List[Dict]) -> Dict:
        """
        Calculates MDR and QFCR metrics on a dataset of sentences and model outputs.
        Expected format for each item in data:
        {
            "id": int/str,
            "category": str (e.g. "Terminology", "Lexical"),
            "qc_sentence": str (original Quebec input),
            "qc_term": str (Quebec term to trace),
            "fr_term": str (Metropolitan/France equivalent),
            "baseline_output": Optional[str] (model output under baseline condition),
            "proofread_output": Optional[str] (model output under proofread condition)
        }
        """
        total_baseline_valid = 0
        mdr_substitutions = 0
        mdr_paraphrases_or_void = 0
        
        total_proofread_valid = 0
        qfcr_removals = 0

        detailed_results = []

        for item in data:
            qc_term = item["qc_term"]
            fr_term = item["fr_term"]
            
            # 1. Calculate MDR (Metropolitan Drift Rate) on Baseline Outputs
            baseline_out = item.get("baseline_output")
            has_drift = False
            is_void_or_paraphrase = False
            
            if baseline_out:
                # We expect the original QC term to be in the input QC sentence
                # Let's verify if the original QC term is actually in the model output
                qc_present_in_output = self.has_term(baseline_out, qc_term)
                fr_present_in_output = self.has_term(baseline_out, fr_term)
                
                total_baseline_valid += 1
                
                if not qc_present_in_output:
                    if fr_present_in_output:
                        # Direct substitution (drift occurred)
                        has_drift = True
                        mdr_substitutions += 1
                    else:
                        # Quebec form vanished but wasn't replaced by the FR counterpart (paraphrase or void)
                        is_void_or_paraphrase = True
                        mdr_paraphrases_or_void += 1
            
            # 2. Calculate QFCR (Quebec False Correction Rate) on Proofread Outputs
            proofread_out = item.get("proofread_output")
            has_false_correction = False
            
            if proofread_out:
                # Under the proofread condition, the model is told NOT to touch valid regionalisms.
                # If the valid Quebec term was in the original and gets removed, it's a False Correction.
                qc_present_in_input = self.has_term(item["qc_sentence"], qc_term)
                qc_present_in_output = self.has_term(proofread_out, qc_term)
                
                if qc_present_in_input:
                    total_proofread_valid += 1
                    if not qc_present_in_output:
                        has_false_correction = True
                        qfcr_removals += 1
            
            detailed_results.append({
                "id": item.get("id"),
                "category": item.get("category", "General"),
                "qc_term": qc_term,
                "fr_term": fr_term,
                "baseline_drifted": has_drift,
                "baseline_paraphrased_or_void": is_void_or_paraphrase,
                "proofread_falsely_corrected": has_false_correction
            })

        # Calculate percentages
        mdr_rate = (mdr_substitutions / total_baseline_valid * 100) if total_baseline_valid > 0 else 0.0
        qfcr_rate = (qfcr_removals / total_proofread_valid * 100) if total_proofread_valid > 0 else 0.0

        return {
            "summary": {
                "total_baseline_evaluated": total_baseline_valid,
                "mdr_substitutions": mdr_substitutions,
                "mdr_paraphrases_or_void": mdr_paraphrases_or_void,
                "metropolitan_drift_rate_pct": round(mdr_rate, 2),
                
                "total_proofread_evaluated": total_proofread_valid,
                "qfcr_removals": qfcr_removals,
                "quebec_false_correction_rate_pct": round(qfcr_rate, 2)
            },
            "details": detailed_results
        }

# --- Demonstration & Mock Dataset ---
if __name__ == "__main__":
    # Create mock evaluations based directly on actual examples from the study
    mock_dataset = [
        {
            "id": 1,
            "category": "Technology",
            "qc_sentence": "Supprimez les pourriels sans ouvrir les pièces jointes.",
            "qc_term": "pourriels",
            "fr_term": "spams",
            # Model 1 (Llama 3.1 8B simulation):
            # Baseline: rephrases but drifts to metropolitan
            "baseline_output": "Supprimez tous les spams sans ouvrir les pièces jointes.",
            # Proofread: instructed to leave valid regional usage alone, but still corrected it to "spams"
            "proofread_output": "Veuillez supprimer les spams sans ouvrir les fichiers joints."
        },
        {
            "id": 2,
            "category": "Technology",
            "qc_sentence": "Ce site utilise des témoins pour mémoriser vos préférences.",
            "qc_term": "témoins",
            "fr_term": "cookies",
            # Model 2 (Qwen 2.5 14B simulation):
            # Baseline: direct drift to Metropolitan
            "baseline_output": "Ce site utilise des cookies pour mémoriser vos préférences.",
            # Proofread: false correction
            "proofread_output": "Ce site web utilise des cookies pour stocker vos préférences."
        },
        {
            "id": 3,
            "category": "Lexical",
            "qc_sentence": "Nous souperons vers 18 h avec les grands-parents.",
            "qc_term": "souperons",
            "fr_term": "dînerons",
            # Baseline: model kept regionalism (retention!)
            "baseline_output": "Nous souperons à 18h avec les grands-parents.",
            # Proofread: kept regionalism (no false correction)
            "proofread_output": "Nous souperons vers 18 h avec les grands-parents."
        },
        {
            "id": 4,
            "category": "Terminology",
            "qc_sentence": "Vous pouvez communiquer avec nous par courriel.",
            "qc_term": "courriel",
            "fr_term": "e-mail",
            # Baseline: complete rephrase that doesn't use e-mail or courriel (should NOT count as drift)
            "baseline_output": "N'hésitez pas à nous contacter par écrit.",
            # Proofread: kept courriel
            "proofread_output": "Vous pouvez communiquer avec nous par courriel."
        },
        {
            "id": 5,
            "category": "Institutional",
            "qc_sentence": "Elle a déposé une demande d'assurance-emploi après sa mise à pied.",
            "qc_term": "assurance-emploi",
            "fr_term": "assurance chômage",
            # Baseline: direct drift to Metropolitan
            "baseline_output": "Elle a déposé un dossier d'assurance chômage après son licenciement.",
            # Proofread: severe institutional false correction
            "proofread_output": "Elle a fait une demande d'assurance chômage après sa mise à pied."
        }
    ]

    calculator = DialectMetricsCalculator()
    report = calculator.calculate_metrics(mock_dataset)

    # Output formatted report
    print("=" * 60)
    print("   CANADIAN FRENCH DIALECT METRICS EVALUATION PIPELINE REPORT   ")
    print("=" * 60)
    
    summary = report["summary"]
    print(f"Total Sentences Evaluated (Baseline):  {summary['total_baseline_evaluated']}")
    print(f"Direct Metropolitan Substitutions:     {summary['mdr_substitutions']}")
    print(f"Paraphrases or Void outputs:           {summary['mdr_paraphrases_or_void']}")
    print("-" * 60)
    print(f"METROPOLITAN DRIFT RATE (MDR):         {summary['metropolitan_drift_rate_pct']}%")
    print("=" * 60)
    
    print(f"Total Sentences Evaluated (Proofread): {summary['total_proofread_evaluated']}")
    print(f"Falsely Corrected Regionalisms:        {summary['qfcr_removals']}")
    print("-" * 60)
    print(f"QUEBEC FALSE CORRECTION RATE (QFCR):   {summary['quebec_false_correction_rate_pct']}%")
    print("=" * 60)
    
    print("\nDetailed Item Classifications:")
    for detail in report["details"]:
        status_baseline = "DRIFT" if detail["baseline_drifted"] else ("PARAPHRASE/VOID" if detail["baseline_paraphrased_or_void"] else "RETAINED")
        status_proof = "FALSE CORRECTION" if detail["proofread_falsely_corrected"] else "CORRECT"
        print(f"ID {detail['id']} [{detail['category']}] - '{detail['qc_term']}' vs '{detail['fr_term']}':")
        print(f"  -> Baseline Output Status:  {status_baseline}")
        print(f"  -> Proofread Output Status: {status_proof}")
    print("=" * 60)
