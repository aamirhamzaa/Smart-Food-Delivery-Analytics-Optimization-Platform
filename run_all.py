import subprocess
import sys
import time

scripts = [
    ("notebooks/generate_data.py",     "Generating Dataset"),
    ("notebooks/setup_hive.py",        "Setting Up Hive Metastore & Tables"),
    ("notebooks/hive_processing.py",   "Running Hive-Equivalent Queries"),
    ("notebooks/analytics.py",         "Computing Business Metrics"),
    ("notebooks/visualizations.py",    "Creating Statistical Charts"),
    ("notebooks/geospatial.py",        "Building Geospatial Maps"),
    ("notebooks/dashboard.py",         "Building Executive Dashboard"),
    ("notebooks/predictive_model.py",  "Training Predictive Models"),
    ("notebooks/generate_report.py",   "Generating Final Report"),
    ("notebooks/build_viewer.py",      "Building Interactive Viewer"),
]

print("=" * 60)
print("SMART FOOD DELIVERY ANALYTICS PLATFORM")
print("Full Pipeline Execution")
print("=" * 60)

failed = False
for script, description in scripts:
    print(f"\n>>> {description}...")
    print("-" * 40)
    start = time.time()
    result = subprocess.run([sys.executable, script], capture_output=False)
    elapsed = time.time() - start
    if result.returncode == 0:
        print(f"    Completed in {elapsed:.1f}s")
    else:
        print(f"    FAILED with return code {result.returncode}")
        failed = True
        break

print("\n" + "=" * 60)
if failed:
    print("PIPELINE FAILED — check the error above")
else:
    print("PIPELINE COMPLETE")
print("=" * 60)
print("\nOutputs:")
print("  Charts:    output/charts/*.png")
print("  Maps:      output/maps/*.html")
print("  Dashboard: output/reports/executive_dashboard.html")
print("  Report:    output/reports/final_report.txt")
print("  Data:      output/reports/*.csv")
print("  Viewer:    output/viewer.html  ← open this in a browser")
