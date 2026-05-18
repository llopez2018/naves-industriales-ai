"""TWX file parser — extracts and classifies all XML artifacts inside a .twx package."""

import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
import re


IBM_NAMESPACES = {
    "lombardi": "http://www.ibm.com/xmlns/prod/websphere/lombardi/8.0",
    "bpd":      "http://www.ibm.com/xmlns/prod/websphere/lombardi/8.0/process",
    "svc":      "http://www.ibm.com/xmlns/prod/websphere/lombardi/8.0/service",
    "bo":       "http://www.ibm.com/xmlns/prod/websphere/lombardi/8.0/businessObject",
    "dec":      "http://www.ibm.com/xmlns/prod/websphere/lombardi/8.0/decision",
    "baw":      "http://www.ibm.com/xmlns/prod/websphere/baw/20.0",
}

ARTIFACT_EXTENSIONS = {
    ".bpd":      "business_process",
    ".service":  "service",
    ".bo":       "business_object",
    ".decision": "decision_table",
    ".htm":      "human_task",
    ".epa":      "event_subprocess",
    ".web":      "web_service",
    ".integr":   "integration_service",
    ".report":   "report",
    ".scoreboard": "scoreboard",
}


@dataclass
class TWXArtifact:
    path: str
    artifact_type: str
    name: str
    raw_xml: Optional[str] = None
    tree: Optional[ET.ElementTree] = None
    guid: Optional[str] = None
    version: Optional[str] = None
    description: Optional[str] = None
    tags: list = field(default_factory=list)


@dataclass
class TWXPackage:
    file_path: str
    app_name: str = ""
    app_guid: str = ""
    app_version: str = ""
    app_acronym: str = ""
    toolkit: bool = False
    artifacts: list[TWXArtifact] = field(default_factory=list)
    manifest: dict = field(default_factory=dict)

    def by_type(self, artifact_type: str) -> list[TWXArtifact]:
        return [a for a in self.artifacts if a.artifact_type == artifact_type]

    @property
    def summary(self) -> dict:
        counts: dict = {}
        for a in self.artifacts:
            counts[a.artifact_type] = counts.get(a.artifact_type, 0) + 1
        return {
            "app_name": self.app_name,
            "app_version": self.app_version,
            "toolkit": self.toolkit,
            "total_artifacts": len(self.artifacts),
            "by_type": counts,
        }


class TWXParser:
    """Opens a .twx file and returns a fully parsed TWXPackage."""

    def __init__(self, twx_path: str):
        self.twx_path = Path(twx_path)
        if not self.twx_path.exists():
            raise FileNotFoundError(f"TWX file not found: {twx_path}")
        if not zipfile.is_zipfile(self.twx_path):
            raise ValueError(f"File is not a valid TWX (ZIP) archive: {twx_path}")

    def parse(self) -> TWXPackage:
        package = TWXPackage(file_path=str(self.twx_path))

        with zipfile.ZipFile(self.twx_path, "r") as zf:
            entries = zf.namelist()
            self._parse_manifest(zf, entries, package)

            for entry in entries:
                if entry.startswith("__MACOSX") or entry.endswith("/"):
                    continue
                suffix = Path(entry).suffix.lower()
                artifact_type = ARTIFACT_EXTENSIONS.get(suffix)
                if not artifact_type:
                    continue

                raw = zf.read(entry).decode("utf-8", errors="replace")
                artifact = TWXArtifact(
                    path=entry,
                    artifact_type=artifact_type,
                    name=self._extract_name(entry, raw),
                    raw_xml=raw,
                )
                try:
                    artifact.tree = ET.ElementTree(ET.fromstring(raw))
                    root = artifact.tree.getroot()
                    artifact.guid = root.get("id") or root.get("guid") or self._attr(root, "id")
                    artifact.version = root.get("version") or root.get("snapshotVersion")
                    artifact.description = self._find_text(root, "description") or \
                                           self._find_text(root, "Documentation")
                    artifact.tags = self._find_tags(root)
                except ET.ParseError:
                    pass

                package.artifacts.append(artifact)

        return package

    # ------------------------------------------------------------------ helpers

    def _parse_manifest(self, zf: zipfile.ZipFile, entries: list, package: TWXPackage) -> None:
        manifest_candidates = [e for e in entries if e.endswith("MANIFEST.MF") or e.endswith("manifest.xml")]
        for candidate in manifest_candidates:
            raw = zf.read(candidate).decode("utf-8", errors="replace")
            package.manifest["raw"] = raw

            name_m = re.search(r"Process-App-Name:\s*(.+)", raw)
            guid_m = re.search(r"Process-App-ID:\s*(.+)", raw)
            ver_m  = re.search(r"Snapshot-Name:\s*(.+)", raw)
            acr_m  = re.search(r"Process-App-Acronym:\s*(.+)", raw)
            tk_m   = re.search(r"Is-Toolkit:\s*(.+)", raw)

            if name_m:
                package.app_name = name_m.group(1).strip()
            if guid_m:
                package.app_guid = guid_m.group(1).strip()
            if ver_m:
                package.app_version = ver_m.group(1).strip()
            if acr_m:
                package.app_acronym = acr_m.group(1).strip()
            if tk_m:
                package.toolkit = tk_m.group(1).strip().lower() == "true"
            return

        # Fallback: infer name from TWX filename
        package.app_name = self.twx_path.stem

    def _extract_name(self, entry: str, raw: str) -> str:
        # Try to get name from XML attribute first
        name_m = re.search(r'\bname=["\']([^"\']+)["\']', raw[:500])
        if name_m:
            return name_m.group(1)
        return Path(entry).stem

    def _attr(self, el: ET.Element, attr: str) -> Optional[str]:
        for key, val in el.attrib.items():
            if key.split("}")[-1] == attr:
                return val
        return None

    def _find_text(self, root: ET.Element, tag: str) -> Optional[str]:
        for el in root.iter():
            if el.tag.split("}")[-1] == tag and el.text:
                return el.text.strip()
        return None

    def _find_tags(self, root: ET.Element) -> list:
        tags = []
        for el in root.iter():
            if el.tag.split("}")[-1] in ("tag", "Tag", "keyword"):
                if el.text:
                    tags.append(el.text.strip())
        return tags
