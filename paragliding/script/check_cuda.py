"""Debug script: check PyTorch and CUDA setup."""

import sys


def main() -> None:
    print("Python:", sys.executable)
    print()

    try:
        import torch
    except ImportError as e:
        print("PyTorch not installed:", e)
        print("Run: poetry install")
        return

    print("PyTorch:", torch.__version__)
    cuda_built = torch.version.cuda
    print("Built with CUDA:", cuda_built if cuda_built else "No (CPU-only build)")
    print("CUDA available:", torch.cuda.is_available())

    if torch.cuda.is_available():
        print("Device:", torch.cuda.get_device_name(0))
        print("Device count:", torch.cuda.device_count())
    else:
        print()
        print("To get CUDA support (after poetry install):")
        print("  poetry run python paragliding/script/install_torch_cuda.py")
        print("  Or: poetry run pip install torch --index-url https://download.pytorch.org/whl/cu124 -U")
        print("  Then run this script again. See https://pytorch.org/get-started/locally/")


if __name__ == "__main__":
    main()
