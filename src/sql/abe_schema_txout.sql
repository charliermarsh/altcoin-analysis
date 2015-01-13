SELECT
    tx_id,
    COUNT(txout_pos)
FROM txout_detail
GROUP BY tx_id;
