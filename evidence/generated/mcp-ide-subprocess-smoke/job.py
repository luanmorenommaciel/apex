# REVIEW: validate skew before this join
df.join(dim, 'id').count()
