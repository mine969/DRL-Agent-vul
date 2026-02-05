import sys
import os
import time

# Ensure env directory is in path
sys.path.append(os.path.join(os.getcwd(), "env"))

targets = [
    "target_app_ecommerce",
    "target_app_social",
    "target_app_banking",
    "target_app_blog",
    "target_app_fileshare",
]

print("=" * 60)
print("VERIFYING MOCK TARGETS")
print("=" * 60)

failed = []

for t in targets:
    print(f"\n[+] Checking {t}...")
    try:
        module = __import__(t)
        print(f"  OK: Module imported.")

        # Check Flask app
        if hasattr(module, "app"):
            print(f"  OK: Flask app found.")
        else:
            print(f"  WARNING: No 'app' object found.")

        # Check DB Init
        if hasattr(module, "init_db"):
            print(f"  Initializing DB for {t}...")
            try:
                module.init_db()
                print(f"  OK: DB initialized successfully.")
            except Exception as e:
                print(f"  ERROR: DB Init failed: {e}")
                failed.append(t)
        else:
            print(f"  WARNING: No 'init_db' function found.")

    except ImportError as e:
        print(f"  ERROR: Import failed: {e}")
        failed.append(t)
    except Exception as e:
        print(f"  ERROR: Unexpected error: {e}")
        failed.append(t)

print("\n" + "=" * 60)
if failed:
    print(f"❌ VERIFICATION FAILED for: {', '.join(failed)}")
    sys.exit(1)
else:
    print("✅ ALL TARGETS VERIFIED SUCCESSFULLY")
    sys.exit(0)
