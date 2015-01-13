SELECT
    tx_id,
    COUNT(txin_pos)
FROM txin_detail
GROUP BY tx_id;
