"""Install PyTorch with CUDA 12.4 in the current environment (e.g. poetry run)."""
import subprocess
import sys

URL = "https://download.pytorch.org/whl/cu124"


def main() -> None:
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "torch", "--index-url", URL, "-U"],
        check=True,
    )
    print("Done. Run: poetry run python paragliding/script/check_cuda.py")


if __name__ == "__main__":
    main()
