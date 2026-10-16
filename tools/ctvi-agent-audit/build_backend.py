"""Small stdlib-only PEP 517 backend for offline build/install of this package.

Builds deterministic wheels/sdists from allowlisted source files. It neither
fetches packages nor executes the package's code. This is build-time code only.
"""

import base64
import csv
import gzip
import hashlib
import io
from pathlib import Path
import re
import tarfile
import zipfile

ROOT = Path(__file__).resolve().parent
DIST = "ctvi_agent_audit"
VERSION = re.search(r'__version__ = "([0-9]+\.[0-9]+\.[0-9]+)"', (ROOT / "ctvi_audit/__init__.py").read_text()).group(1)
INFO = DIST + "-" + VERSION + ".dist-info"
FIXED_TIME = (2026, 10, 17, 0, 0, 0)


def _files(folder):
    for path in sorted((ROOT / folder).rglob("*")):
        if path.is_file() and not path.is_symlink() and "__pycache__" not in path.parts and path.suffix not in {".pyc", ".zip", ".whl"}:
            yield path.relative_to(ROOT).as_posix(), path.read_bytes()


def _metadata():
    fields = ["Metadata-Version: 2.4", "Name: ctvi-agent-audit", "Version: " + VERSION,
              "Summary: Offline structural and provenance checks for normalized agent traces",
              "Author: Abdullah Alharbi", "Author-email: albdrani36@gmail.com",
              "Requires-Python: >=3.10", "Classifier: Development Status :: 3 - Alpha",
              "Classifier: Programming Language :: Python :: 3", "Classifier: Operating System :: POSIX",
              "Description-Content-Type: text/markdown"]
    if (ROOT / "LICENSE").is_file():
        fields.append("License-File: LICENSE")
        if (ROOT / "LICENSE_SCOPE.txt").is_file():
            fields.append("License-File: LICENSE_SCOPE.txt")
        # A release-approved SPDX expression may be added explicitly to pyproject.toml.
        match = re.search(r'^license\s*=\s*"([^"\n]+)"\s*$', (ROOT / "pyproject.toml").read_text(), re.M)
        if match:
            fields.append("License-Expression: " + match.group(1))
    return ("\n".join(fields) + "\n\n" + (ROOT / "README.md").read_text()).encode("utf-8")


def _wheel_files():
    files = dict(_files("ctvi_audit"))
    files[INFO + "/METADATA"] = _metadata()
    files[INFO + "/WHEEL"] = b"Wheel-Version: 1.0\nGenerator: ctvi-stdlib-backend-1\nRoot-Is-Purelib: true\nTag: py3-none-any\n"
    files[INFO + "/entry_points.txt"] = b"[console_scripts]\nctvi-agent-audit = ctvi_audit.__main__:main\n"
    if (ROOT / "LICENSE").is_file():
        files[INFO + "/licenses/LICENSE"] = (ROOT / "LICENSE").read_bytes()
        if (ROOT / "LICENSE_SCOPE.txt").is_file():
            files[INFO + "/licenses/LICENSE_SCOPE.txt"] = (ROOT / "LICENSE_SCOPE.txt").read_bytes()
    record = io.StringIO(newline="")
    writer = csv.writer(record, lineterminator="\n")
    for name, data in sorted(files.items()):
        digest = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=").decode("ascii")
        writer.writerow([name, "sha256=" + digest, str(len(data))])
    writer.writerow([INFO + "/RECORD", "", ""])
    files[INFO + "/RECORD"] = record.getvalue().encode("utf-8")
    return files


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    target = Path(wheel_directory); target.mkdir(parents=True, exist_ok=True)
    name = DIST + "-" + VERSION + "-py3-none-any.whl"
    with zipfile.ZipFile(target / name, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        files = _wheel_files()
        for filename in sorted(files, key=lambda s: (s.startswith(INFO + "/"), s)):
            info = zipfile.ZipInfo(filename, FIXED_TIME); info.compress_type = zipfile.ZIP_DEFLATED; info.external_attr = 0o100644 << 16
            archive.writestr(info, files[filename])
    return name


def build_sdist(sdist_directory, config_settings=None):
    target = Path(sdist_directory); target.mkdir(parents=True, exist_ok=True)
    stem = DIST + "-" + VERSION
    files = {}
    for folder in ("ctvi_audit", "tests", "docs", "examples"):
        files.update(_files(folder))
    for name in ("README.md", "SUPPORT.md", "CHANGELOG.md", "pyproject.toml", "build_backend.py", "schema.json", "LICENSE", "LICENSE_SCOPE.txt"):
        if (ROOT / name).is_file(): files[name] = (ROOT / name).read_bytes()
    files["PKG-INFO"] = _metadata()
    with (target / (stem + ".tar.gz")).open("wb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", filename="", mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as archive:
                for name, data in sorted(files.items()):
                    info = tarfile.TarInfo(stem + "/" + name); info.size = len(data); info.mode = 0o644; info.mtime = 0
                    archive.addfile(info, io.BytesIO(data))
    return stem + ".tar.gz"


def get_requires_for_build_wheel(config_settings=None): return []
def get_requires_for_build_sdist(config_settings=None): return []


if __name__ == "__main__":
    print(build_wheel(str(ROOT / "dist")))
    print(build_sdist(str(ROOT / "dist")))
