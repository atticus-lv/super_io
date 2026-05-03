import argparse
import subprocess
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


ROOT = Path(__file__).parent


def read_manifest() -> dict:
    with open(ROOT / "blender_manifest.toml", "rb") as f:
        return tomllib.load(f)


def build_extension(blender: str, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = read_manifest()
    print(f'Extension name: {manifest["name"]}')
    print(f'Version: {manifest["version"]}')

    subprocess.run(
        [
            blender,
            "--factory-startup",
            "--command",
            "extension",
            "build",
            "--source-dir",
            str(ROOT),
            "--output-dir",
            str(output_dir),
        ],
        check=True,
    )


def main():
    parser = argparse.ArgumentParser(description="Build the Super IO Blender extension")
    parser.add_argument("blender", help="Path to blender.exe")
    parser.add_argument("--output-dir", default=str(ROOT / "build"))
    args = parser.parse_args()

    build_extension(args.blender, Path(args.output_dir))


if __name__ == "__main__":
    sys.exit(main())
