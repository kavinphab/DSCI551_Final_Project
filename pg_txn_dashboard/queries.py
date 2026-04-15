INDEX_DEFINITIONS = {
    "idx_transactions_user_id": "CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);",
    "idx_transactions_user_created": (
        "CREATE INDEX IF NOT EXISTS idx_transactions_user_created "
        "ON transactions(user_id, created_at DESC);"
    ),
}


USER_TRANSACTION_SQL = """
SELECT id, user_id, asset_id, amount, created_at
FROM transactions
WHERE user_id = %s
ORDER BY created_at DESC
LIMIT %s;
"""


RECENT_ACTIVITY_SQL = """
SELECT id, user_id, asset_id, amount, created_at
FROM transactions
WHERE user_id = %s
ORDER BY created_at DESC
LIMIT 20;
"""


JOINED_USER_TRANSACTION_SQL = """
SELECT t.id, t.user_id, u.name, u.email, t.asset_id, t.amount, t.created_at
FROM transactions t
JOIN users u ON t.user_id = u.id
WHERE t.user_id = %s
ORDER BY t.created_at DESC
LIMIT 50;
"""


AGGREGATION_SQL = """
SELECT user_id, COUNT(*) AS txn_count
FROM transactions
GROUP BY user_id
ORDER BY txn_count DESC
LIMIT 20;
"""


INSERT_LOG_SQL = """
INSERT INTO logs (event, created_at)
VALUES (%s, NOW())
RETURNING id, event, created_at;
"""


GET_ASSET_SQL = """
SELECT id, owner_id, asset_name, value, created_at
FROM assets
WHERE id = %s;
"""


UPDATE_ASSET_SQL = """
UPDATE assets
SET value = %s
WHERE id = %s
RETURNING id, owner_id, asset_name, value, created_at;
"""


OPERATION_DETAILS = {
    "User Transaction Search": {
        "business_summary": "Find the transactions for one user and inspect the newest matching rows.",
        "internal_focus": "Shows full scan versus index-supported retrieval, plus heap access after following a secondary B-tree index on `transactions(user_id)`.",
        "sql": USER_TRANSACTION_SQL,
        "default_params": (1, 25),
        "plan_explanation": (
            "This query filters on `user_id` and sorts by `created_at`. Without a useful index PostgreSQL may scan many heap pages, "
            "but with the demo indexes it can use index access to narrow the matching tuples before reading the heap rows that are visible."
        ),
    },
    "Recent Activity Feed": {
        "business_summary": "Show the latest 20 transactions for a selected user.",
        "internal_focus": "Highlights composite index behavior and whether one index can support both the filter and descending order.",
        "sql": RECENT_ACTIVITY_SQL,
        "default_params": (1,),
        "plan_explanation": (
            "The `(user_id, created_at DESC)` index is designed for this pattern. When PostgreSQL chooses it, the same access path can satisfy "
            "the `WHERE user_id = ...` predicate and deliver rows in the requested order."
        ),
    },
    "Joined User Transaction View": {
        "business_summary": "Combine transaction records with user profile details for a richer application view.",
        "internal_focus": "Shows planner join strategy choices such as hash join or nested loop based on selectivity and cost.",
        "sql": JOINED_USER_TRANSACTION_SQL,
        "default_params": (1,),
        "plan_explanation": (
            "The planner compares join algorithms using table size, row estimates, and filter selectivity. Because the query is selective on one user, "
            "the join may favor a plan different from a broad join over the entire dataset."
        ),
    },
    "Aggregation Dashboard": {
        "business_summary": "Compute top users by transaction volume.",
        "internal_focus": "Shows grouping and ordering strategy, including HashAggregate versus sort-based alternatives.",
        "sql": AGGREGATION_SQL,
        "default_params": (),
        "plan_explanation": (
            "This query must inspect many transaction rows to count them by user. Even with indexes, PostgreSQL still needs to aggregate the groups, "
            "so the interesting choice is usually how it groups and sorts rather than whether it can avoid touching lots of data."
        ),
    },
}
