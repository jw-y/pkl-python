import argparse
from pathlib import Path

import requests

VERSION = "0.25.2"

BASE_PATH = "https://github.com/apple/pkl/releases/download/"
filenames = [
    "pkl-macos-aarch64",
    "pkl-macos-amd64",
    "pkl-linux-aarch64",
    "pkl-linux-amd64",
    "pkl-alpine-linux-amd64",
]
JAVA_FILE = f"https://repo1.maven.org/maven2/org/pkl-lang/pkl-cli-java/{VERSION}/pkl-cli-java-{VERSION}.jar"


def main(save_path):
    urls = [BASE_PATH + VERSION + "/" + file for file in filenames]
    urls.append(JAVA_FILE)

    for url in urls:
        file = url.split("/")[-1]
        fp = save_path / file

        response = requests.get(url)
        with open(fp, "wb") as f:
            f.write(response.content)

        print("written to", fp)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "output_path", help="Directory where binaries will be downloaded"
    )

    args = parser.parse_args()

    main(Path(args.output_path))
