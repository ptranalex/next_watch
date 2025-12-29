def test_movie_storage():
    import subprocess
    import sys

    ***REMOVED*** Import in a subprocess to avoid SQLModel/SQLAlchemy global MetaData collisions
    ***REMOVED*** between backend_api models and the shared `movie_storage` package.
    proc = subprocess.run(
        [sys.executable, "-c", "import movie_storage"],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
