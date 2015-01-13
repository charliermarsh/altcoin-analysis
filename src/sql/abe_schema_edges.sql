/*
    Produces one row per input/output pubkey pair
    Input and output pubkey_ids are CSV in columns
    Associated values as of the transaction occurence also included
*/

SELECT
    a.tx_id as tx_id,
    txout.pubkey_id as input_pubkey_id,
    txout.txout_value as input_value,
    a.output_pubkey_id as output_pubkey_id,
    a.output_value as output_value
FROM
(
    SELECT
        tx.tx_id as tx_id,
        txout.pubkey_id as output_pubkey_id,
        txout.txout_value as output_value,
        txin.txout_id AS utxo_txout_id
    FROM tx
    JOIN txin
    ON tx.tx_id = txin.tx_id
    JOIN txout
    ON tx.tx_id = txout.tx_id
) AS a
LEFT OUTER JOIN txout
ON a.utxo_txout_id = txout.txout_id
ORDER BY tx_id ASC
