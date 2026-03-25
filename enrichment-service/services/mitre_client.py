"""MITRE ATT&CK helper client for optional local enrichment lookups."""


class MitreClient:
    """MITRE lookup facade using static fallbacks for common activity."""

    def __init__(self) -> None:
        """Initialize MITRE lookup client."""
        self._fallbacks = {
            "powershell": ("Execution", "T1059.001", "PowerShell"),
            "lsass": ("Credential Access", "T1003.001", "LSASS Memory"),
            "lateral": ("Lateral Movement", "T1021", "Remote Services"),
            "c2": ("Command and Control", "T1071", "Application Layer Protocol"),
            "exfil": ("Exfiltration", "T1041", "Exfiltration Over C2 Channel"),
        }

    def map_from_text(self, text: str) -> tuple[str, str, str]:
        """Infer basic MITRE mapping from text when AI output is unavailable."""
        lowered = text.lower()
        for needle, mapping in self._fallbacks.items():
            if needle in lowered:
                return mapping
        return ("Discovery", "T1087", "Account Discovery")
