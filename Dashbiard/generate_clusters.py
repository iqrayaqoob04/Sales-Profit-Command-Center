import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

DATA_DIR = Path(__file__).resolve().parent

# Load data
df = pd.read_csv(DATA_DIR / 'superstore_cleaned.csv')

# Aggregate by customer
customer_df = df.groupby('Customer ID').agg(
    total_sales=('Sales', 'sum'),
    total_profit=('Profit', 'sum'),
    order_count=('Order ID', 'nunique'),
    avg_discount=('Discount', 'mean'),
    avg_quantity=('Quantity', 'mean'),
    customer_name=('Customer Name', 'first')
).reset_index()

# Features for clustering
features = ['total_sales', 'total_profit', 'order_count', 'avg_discount']
X = customer_df[features]

# Standardize
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# KMeans clustering (4 clusters for meaningful segmentation)
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
customer_df['cluster'] = kmeans.fit_predict(X_scaled)

# Label clusters by their value profile (high-value = high profit + high sales)
cluster_profiles = customer_df.groupby('cluster')[features].mean()
sorted_clusters = sorted(cluster_profiles.index, key=lambda c: cluster_profiles.loc[c, 'total_profit'], reverse=True)
label_map = {}
for rank, c in enumerate(sorted_clusters):
    if rank == 0:
        label_map[c] = 'High-Value'
    elif rank == 1:
        label_map[c] = 'Mid-High'
    elif rank == 2:
        label_map[c] = 'Mid-Low'
    else:
        label_map[c] = 'Low-Value'

customer_df['cluster_label'] = customer_df['cluster'].map(label_map)

# Save
customer_df.to_csv(DATA_DIR / 'customer_segments.csv', index=False)
print(f"Generated customer_segments.csv with {len(customer_df)} customers and {customer_df['cluster'].nunique()} clusters")
print("\nCluster counts:")
print(customer_df['cluster_label'].value_counts())
print("\nCluster profiles:")
print(customer_df.groupby('cluster_label')[features].mean().round(2))