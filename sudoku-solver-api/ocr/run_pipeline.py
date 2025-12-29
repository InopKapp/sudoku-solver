import sys
import subprocess
import os

def run(cmd):
    print(f"\nRunning: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print("Step failed, stopping pipeline.")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python run_pipeline.py <input_image>")
        sys.exit(1)

    input_image = sys.argv[1]

    if not os.path.exists(input_image):
        print("Input image not found")
        sys.exit(1)

    os.makedirs("debug", exist_ok=True)

    python = sys.executable

    run([python, "ocr/preprocess.py", input_image])

    run([python, "ocr/grid_detect.py", "debug/1_original.png", "debug/4_preprocessed.png"])

    run([python, "ocr/ocr_digits.py"])

    print("\nPipeline completed successfully.")
