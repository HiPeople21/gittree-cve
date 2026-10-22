import io
import tarfile

from uploads.extract import extract_upload


def test_extracts_regular_file(tmp_path):
    archive = tmp_path / "a.tar.gz"
    with tarfile.open(archive, "w:gz") as tar:
        data = b"hello"
        info = tarfile.TarInfo("docs/readme.txt")
        info.size = len(data)
        tar.addfile(info, io.BytesIO(data))
    out = tmp_path / "out"
    assert extract_upload(str(archive), str(out)) == ["docs/readme.txt"]
    assert (out / "docs" / "readme.txt").read_bytes() == b"hello"
