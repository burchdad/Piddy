import sys, os
sys.path.insert(0, os.getcwd())

try:
    from src.api.config_routes import router
    print(f"IMPORT OK: prefix={router.prefix!r}, routes={len(router.routes)}")
    for r in router.routes:
        print(f"  {r.methods if hasattr(r,'methods') else '?'} {r.path}")
except Exception as e:
    print(f"IMPORT FAILED: {type(e).__name__}: {e}")
