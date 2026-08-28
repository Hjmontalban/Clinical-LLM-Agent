import re

UNSAFE_PATTERNS = [
    (r"\byou (have|definitely have|likely have)\b.*\b(cancer|diabetes|disease)\b", "diagnosis"),
    (r"\btake \d+\s*mg\b", "prescription"),
    (r"\bstop (taking|your) (medication|medicine|drug)\b", "medication advice"),
    (r"\bdefinitely safe\b", "safety claim"),
    (r"\byou should (take|start|stop)\b", "treatment directive"),
    (r"\bemergency\b.*\b(call|go to)\b", "emergency substitute"),
]

SAFE_REPLACEMENTS = {
    "diagnosis": "Research has investigated associations related to this topic. Consult a healthcare professional for personal medical assessment.",
    "prescription": "Clinical dosing should be determined by a qualified healthcare professional.",
    "medication advice": "Medication decisions should be made with a qualified healthcare professional.",
    "safety claim": "Safety profiles vary; consult published studies and healthcare professionals.",
    "treatment directive": "Treatment decisions require individualized clinical assessment.",
    "emergency substitute": "For emergencies, contact local emergency services immediately.",
}

DISCLAIMER = (
    "This is a research and evidence-synthesis tool, not medical advice. "
    "Do not use for diagnosis, prescribing, or emergency care. "
    "Consult qualified healthcare professionals for personal medical decisions."
)


class SafetyGate:
    def check_text(self, text: str) -> tuple[str, list[str]]:
        issues: list[str] = []
        cleaned = text
        for pattern, issue_type in UNSAFE_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                issues.append(issue_type)
                cleaned = SAFE_REPLACEMENTS.get(issue_type, cleaned)
        return cleaned, issues

    def filter_findings(self, findings: list[str]) -> list[str]:
        filtered = []
        for f in findings:
            cleaned, issues = self.check_text(f)
            if not issues:
                filtered.append(f)
            else:
                filtered.append(
                    f"[Revised for safety] Research literature addresses related topics. "
                    f"Consult healthcare professionals for personal decisions."
                )
        return filtered

    def add_disclaimer(self, summary: str) -> str:
        if DISCLAIMER not in summary:
            return f"{summary}\n\n{DISCLAIMER}"
        return summary
