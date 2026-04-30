from core.db.db import WriteDB, ReadDB
from core.db.db_config import WRITE_DB_CONFIG, READ_DB_CONFIG


def test_write():
    print("Testing write connection...")
    with WriteDB(**WRITE_DB_CONFIG) as write_db:
        with write_db.cursor() as cur:
            cur.execute("SELECT 1")
            result = cur.fetchone()
            print(f" Result: {result}")
    print("  ✓ WriteDB OK\n")


def test_read():
    print("Testing ReadDB...")
    with ReadDB(**READ_DB_CONFIG) as read_db:
        result = read_db.fetch_one("SELECT 1 as test")
        print(f" Result: {result}")
        assert result == {"test": 1}, "Read test failed"
    print("  ✓ ReadDB OK\n")


def test_replication():
    print("Testing replication setup (standby should reject writes)...")
    try:
        with ReadDB(**READ_DB_CONFIG) as db:
            with db.cursor() as cur:
                cur.execute("CREATE TEMP TABLE test_replica_check (id int)")
        print("  ⚠ WARNING: Standby accepted write — not a real replica?\n")
    except Exception as e:
        if "read-only" in str(e).lower() or "cannot execute" in str(e).lower():
            print(f"  ✓ Standby correctly rejected write")
            print(f"    ({type(e).__name__}: {str(e)[:80]}...)\n")
        else:
            print(f"  ? Unexpected error: {e}\n")
            raise


with ReadDB(
    host="localhost",
    port=5433,
    database="lidless",
    user="postgres",
    password="password",
) as read_db:
    result = read_db.fetch_one("SELECT 1 as test")
    print(result)


if __name__ == "__main__":
    test_read()
    test_write()
    test_replication()
    print("All tests passed")
