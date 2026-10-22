import tarfile


def extract_upload(archive_path: str, dest_dir: str) -> list[str]:
    """Extract a user-uploaded .tar.gz into dest_dir and return the member names."""
    with tarfile.open(archive_path) as tar:
        tar.extractall(dest_dir)
        return tar.getnames()
