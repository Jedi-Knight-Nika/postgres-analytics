import psycopg2
from databend_py import Client
import time
import random

def timeit(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.4f} seconds")
        return result
    return wrapper

# PostgreSQL connection
pg_conn = psycopg2.connect("dbname=testdb user=testuser password=testpass host=localhost port=5432")
pg_cur = pg_conn.cursor()

# Citus connection
citus_conn = psycopg2.connect("dbname=citus user=citus password=citus host=localhost port=5434")
citus_cur = citus_conn.cursor()

# Databend connection
databend_client = Client('root:@127.0.0.1', port=8000, secure=False)
databend_client.execute("USE default")

@timeit
def insert_record(cur, conn, is_databend=False):
    if is_databend:
        databend_client.execute("INSERT INTO transactions (user_id, amount) VALUES (%d, %f)" % 
                                (random.randint(1, 1000), random.uniform(1, 1000)))
    else:
        cur.execute("INSERT INTO transactions (user_id, amount) VALUES (%s, %s)", 
                    (random.randint(1, 1000), random.uniform(1, 1000)))
        conn.commit()

@timeit
def update_record(cur, conn, is_databend=False):
    if is_databend:
        databend_client.execute("UPDATE transactions SET amount = %f WHERE id = (SELECT id FROM transactions ORDER BY RANDOM() LIMIT 1)" % 
                                random.uniform(1, 1000))
    else:
        cur.execute("UPDATE transactions SET amount = %s WHERE id = (SELECT id FROM transactions ORDER BY RANDOM() LIMIT 1)", 
                    (random.uniform(1, 1000),))
        conn.commit()
@timeit
def delete_record(cur, conn, is_databend=False):
    if is_databend:
        databend_client.execute("DELETE FROM transactions WHERE id = (SELECT id FROM transactions ORDER BY RANDOM() LIMIT 1)")
    else:
        cur.execute("DELETE FROM transactions WHERE id = (SELECT id FROM transactions ORDER BY RANDOM() LIMIT 1)")
        conn.commit()

@timeit
def batch_insert(cur, conn, n=1000, is_databend=False):
    data = [(random.randint(1, 1000), random.uniform(1, 1000)) for _ in range(n)]
    if is_databend:
        values = ", ".join([f"({d[0]}, {d[1]})" for d in data])
        databend_client.execute(f"INSERT INTO transactions (user_id, amount) VALUES {values}")
    else:
        cur.executemany("INSERT INTO transactions (user_id, amount) VALUES (%s, %s)", data)
        conn.commit()

# Test PostgreSQL
print("Testing PostgreSQL:")
insert_record(pg_cur, pg_conn)
update_record(pg_cur, pg_conn)
delete_record(pg_cur, pg_conn)
batch_insert(pg_cur, pg_conn)

# Test Citus
print("\nTesting Citus:")
insert_record(citus_cur, citus_conn)
update_record(citus_cur, citus_conn)
delete_record(citus_cur, citus_conn)
batch_insert(citus_cur, citus_conn)

# Test Databend
print("\nTesting Databend:")
insert_record(None, None, is_databend=True)
update_record(None, None, is_databend=True)
delete_record(None, None, is_databend=True)
batch_insert(None, None, is_databend=True)

# Close connections
pg_conn.close()
citus_conn.close()
databend_client.disconnect()