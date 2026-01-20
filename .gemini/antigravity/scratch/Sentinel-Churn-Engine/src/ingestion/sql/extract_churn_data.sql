-- Extract customer data joined with usage metrics
SELECT 
    c.id AS customer_id,
    c.join_date,
    c.location,
    c.contract_type,
    u.monthly_gb,
    u.call_duration,
    u.support_calls,
    u.payment_delay,
    c.churn,
    u.monthly_charges,
    u.total_charges
FROM 
    customers_profile c
LEFT JOIN 
    usage_metrics u 
ON 
    c.id = u.id;
