from ftplib import error_perm
from io import BytesIO
import tarfile
import unittest

from tools.publish_portfolio import DIRECTORIES, FILES, REMOTE, inventory, upload


class FakeFTPS:
    def __init__(self):
        self.directories = {f"/{REMOTE}"}
        self.files = {}
        self.replaced = []

    def cwd(self, name):
        dest = name if name.startswith("/") else f"/{name}" if not hasattr(self, "current") else f"{self.current}/{name}"
        if dest not in self.directories:
            raise error_perm("550 Directory unavailable")
        self.current = dest

    def pwd(self):
        return self.current

    def mkd(self, name):
        self.directories.add(f"{self.current}/{name}")

    def storbinary(self, command, data):
        verb, name = command.split(" ", 1)
        assert verb == "STOR"
        self.files[f"{self.current}/{name}"] = data.read()

    def rename(self, old, new):
        dest = f"{self.current}/{new}"
        self.files[dest] = self.files.pop(f"{self.current}/{old}")
        self.replaced.append(dest)


class PublishPortfolioTest(unittest.TestCase):
    def release(self, extra=None, omit=None):
        data = BytesIO()
        with tarfile.open(fileobj=data, mode="w") as archive:
            names = list(FILES) + [path + "/preview.png" for path in DIRECTORIES]
            for name in names:
                if name != omit:
                    member = tarfile.TarInfo(name)
                    member.size = len(name.encode())
                    archive.addfile(member, BytesIO(name.encode()))
            if extra:
                archive.addfile(extra)
        data.seek(0)
        return tarfile.open(fileobj=data, mode="r")

    def test_incomplete_release_is_rejected(self):
        with self.release(omit="index.html") as archive:
            with self.assertRaisesRegex(ValueError, "missing release content"):
                inventory(archive)

    def test_server_code_is_not_a_public_asset(self):
        with self.release(extra=tarfile.TarInfo("assets/work/tool.php")) as archive:
            with self.assertRaisesRegex(ValueError, "not a public release file"):
                inventory(archive)

    def test_only_regular_files_can_be_published(self):
        link = tarfile.TarInfo("assets/work/preview.jpg")
        link.type = tarfile.SYMTYPE
        link.linkname = "preview.png"
        with self.release(extra=link) as archive:
            with self.assertRaisesRegex(ValueError, "not a unique regular file"):
                inventory(archive)

    def test_publishes_assets_before_index_and_preserves_other_files(self):
        ftp = FakeFTPS()
        unrelated = f"/{REMOTE}/keep.txt"
        ftp.files[unrelated] = b"independent file"
        ftp.files[f"/{REMOTE}/index.html"] = b"prior index"
        with self.release() as archive:
            release = inventory(archive)
            upload(ftp, archive, release)
        self.assertEqual(ftp.replaced[-1], f"/{REMOTE}/index.html")
        self.assertEqual(
            set(ftp.files), {unrelated} | {f"/{REMOTE}/{name}" for name in release},
        )
        self.assertEqual(ftp.files[unrelated], b"independent file")
        self.assertEqual(ftp.files[f"/{REMOTE}/index.html"], b"index.html")

    def test_missing_remote_root_does_not_create_one(self):
        ftp = FakeFTPS()
        ftp.directories.clear()
        with self.release() as archive:
            with self.assertRaises(error_perm):
                upload(ftp, archive, inventory(archive))
        self.assertEqual(ftp.directories, set())
        self.assertEqual(ftp.files, {})
