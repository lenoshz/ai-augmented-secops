"""Threat intelligence client for optional IOC lookups."""

import httpx

from config import settings


class ThreatIntelClient:
    """Async integrations for AbuseIPDB and VirusTotal enrichment checks."""

    async def lookup_ip(self, ip_address: str) -> list[str]:
        """Return IOC matches for destination IP from enabled intel providers."""
        if not ip_address or not settings.enable_ioc_lookup:
            return []

        findings: list[str] = []

        if settings.abuseipdb_api_key:
            abuse = await self._lookup_abuseipdb(ip_address)
            if abuse:
                findings.append(abuse)

        if settings.virustotal_api_key:
            vt = await self._lookup_virustotal(ip_address)
            if vt:
                findings.append(vt)

        return findings

    async def _lookup_abuseipdb(self, ip_address: str) -> str:
        """Query AbuseIPDB and return a concise reputation finding."""
        url = "https://api.abuseipdb.com/api/v2/check"
        headers = {"Key": settings.abuseipdb_api_key, "Accept": "application/json"}
        params = {"ipAddress": ip_address, "maxAgeInDays": 90}
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            score = response.json().get("data", {}).get("abuseConfidenceScore", 0)
            if score >= 50:
                return f"AbuseIPDB score {score} for {ip_address}"
        return ""

    async def _lookup_virustotal(self, ip_address: str) -> str:
        """Query VirusTotal IP endpoint and return malicious vote summary."""
        url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip_address}"
        headers = {"x-apikey": settings.virustotal_api_key}
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            stats = response.json().get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
            malicious = int(stats.get("malicious", 0))
            if malicious > 0:
                return f"VirusTotal malicious detections {malicious} for {ip_address}"
        return ""
