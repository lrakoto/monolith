"""Validate the tracked static release, or publish it to the portfolio directory."""
import argparse
from ftplib import FTP_TLS, error_perm
import os
from pathlib import Path, PurePosixPath
import ssl
import subprocess
import tarfile
import tempfile
from uuid import uuid4


ROOT = Path(__file__).resolve().parents[1]
REMOTE = "threeohfivestudios.com/portfolio"
PAGES = (
    "index.html", "forest.html", "redwoods.html", "temple.html", "monolith.html",
    "forest-study.html", "redwoods-study.html", "pond-study.html",
    "temple-study.html", "light-pulse.html",
)
FILES = PAGES + (
    ".htaccess", "COLOPHON.md", "FONT-LICENSES.md", "LICENSE", "funding.json",
    "assets/fonts.css", "assets/metrics.js", "assets/portfolio-polish.css",
    "assets/three.min.js",
)
DIRECTORIES = (
    "assets/brand", "assets/redwoods", "assets/resume", "assets/temple",
    "assets/temple-study", "assets/work", "blockshooter", "pyxel",
)
EXTENSIONS = {
    ".css", ".glb", ".html", ".jpg", ".js", ".json", ".md", ".mp4",
    ".pdf", ".png", ".txt", ".webp", ".woff2",
}


def inventory(archive):
    """Reject an incomplete or nonstatic release before opening the connection."""
    files = {}
    for member in archive.getmembers():
        name = member.name
        path = PurePosixPath(name)
        if (path.is_absolute() or str(path) != name or ".." in path.parts
                or any(ord(c) < 32 or c == "\\" for c in name)):
            raise ValueError(f"invalid release path: {name!r}")
        if member.isdir():
            continue
        if not member.isfile() or name in files:
            raise ValueError(f"not a unique regular file: {name!r}")
        if name not in FILES and not (
            any(name.startswith(folder + "/") for folder in DIRECTORIES)
            and path.suffix.lower() in EXTENSIONS
            and not any(part.startswith(".") for part in path.parts)
        ):
            raise ValueError(f"not a public release file: {name!r}")
        files[name] = member
    missing = set(FILES) - files.keys()
    missing.update(folder for folder in DIRECTORIES
                   if not any(name.startswith(folder + "/") for name in files))
    if missing:
        raise ValueError(f"missing release content: {', '.join(sorted(missing))}")
    return files


def upload(ftp, archive, files):
    # the remote portfolio directory must already exist. only subdirectories
    # of that directory can be created by the publisher.
    ftp.cwd(REMOTE)
    root = ftp.pwd()
    # upload dependencies before entry pages so users arriving during an
    # update do not see an html file that points at assets yet to be copied.
    for name in sorted(files, key=lambda name: (name.endswith(".html"), name == "index.html", name)):
        path = PurePosixPath(name)
        ftp.cwd(root)
        for folder in path.parts[:-1]:
            try:
                ftp.cwd(folder)
            except error_perm as error:
                if not str(error).startswith("550 "):
                    raise
                ftp.mkd(folder)
                ftp.cwd(folder)
        # the previous version remains readable until the full replacement
        # is present. a failure may leave a temporary file for manual cleanup.
        pending = f".portfolio-upload-{uuid4().hex}"
        with archive.extractfile(files[name]) as content:
            ftp.storbinary(f"STOR {pending}", content)
        ftp.rename(pending, path.name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--publish", action="store_true", help="write the validated release over FTPS")
    args = parser.parse_args()
    with tempfile.TemporaryFile() as staging:
        subprocess.run(
            ["git", "archive", "--format=tar", "HEAD", "--", *FILES, *DIRECTORIES],
            cwd=ROOT, stdout=staging, check=True,
        )
        staging.seek(0)
        with tarfile.open(fileobj=staging, mode="r:") as archive:
            files = inventory(archive)
            print(f"Validated {len(files)} static files for /portfolio/.", flush=True)
            if args.publish:
                # FTP_TLS upgrades the control channel before login; prot_p
                # requires encrypted transfer channels as well.
                with FTP_TLS(context=ssl.create_default_context(), timeout=30) as ftp:
                    ftp.connect(os.environ["FTP_SERVER"])
                    ftp.login(os.environ["FTP_USERNAME"], os.environ["FTP_PASSWORD"])
                    ftp.prot_p()
                    upload(ftp, archive, files)
                print(f"Published {len(files)} files to /portfolio/.")


if __name__ == "__main__":
    main()
