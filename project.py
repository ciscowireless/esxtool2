"""EsxProject: context-managed lifecycle for an Ekahau .esx file."""

from __future__ import annotations

import os
import shutil
import tempfile
import zipfile

import console
from models import Ap, Floor
from readers import read_aps, read_floors


class EsxProject:
    """An opened Ekahau .esx project backed by a temp directory."""

    def __init__(self, path: str):
        self.source = os.path.abspath(path)
        self.name = os.path.basename(path)
        self.dir = os.path.dirname(self.source)
        self.workdir = self._extract()
        self.floors: list[Floor] = read_floors(self.workdir)
        self.aps: list[Ap] = read_aps(self.workdir, self.floors)

    # -- context manager -----------------------------------------------------

    def __enter__(self) -> EsxProject:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    # -- public --------------------------------------------------------------

    def save(self, suffix: str = ".esxtool") -> str:
        """Zip the working directory back into a new .esx file.

        Returns the path to the new file.
        """
        stem = os.path.splitext(self.name)[0]
        out_name = f"{stem}{suffix}.esx"
        out_path = os.path.join(self.dir, out_name)

        with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for entry in os.listdir(self.workdir):
                zf.write(os.path.join(self.workdir, entry), arcname=entry)

        console.ok(f"Reconstructed ESX file: {console.green(out_path)}")
        return out_path

    def close(self) -> None:
        if os.path.isdir(self.workdir):
            shutil.rmtree(self.workdir, ignore_errors=True)

    # -- private -------------------------------------------------------------

    def _extract(self) -> str:
        workdir = tempfile.mkdtemp(prefix="esxtool_")
        root = os.path.normpath(workdir) + os.sep

        with zipfile.ZipFile(self.source, "r") as zf:
            for member in zf.infolist():
                target = os.path.normpath(os.path.join(workdir, member.filename))
                if not target.startswith(root):
                    raise ValueError(
                        f"Zip entry {member.filename!r} escapes target directory"
                    )
            zf.extractall(workdir)

        return workdir
