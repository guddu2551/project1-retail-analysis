# ============================================================
# PROJECT 1: Retail Sales Analysis
# ============================================================
# What this script does:
#   1. Loads a messy retail CSV file
#   2. Cleans all the data problems
#   3. Answers 6 real business questions
#   4. Saves 6 charts as PNG files
# ============================================================

# --- IMPORTS ---
# These are libraries (tools) we need
# pandas  = works with tables of data (like Excel but in Python)
# matplotlib = draws charts
# seaborn = makes charts look more professional
# os = lets us create folders on the computer

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os

# ============================================================
# STEP 1: SETUP
# ============================================================

# Create the charts folder if it doesn't exist yet
# exist_ok=True means: don't crash if it already exists
os.makedirs('charts', exist_ok=True)

# Set the visual style for ALL charts in this script
# 'whitegrid' gives clean white background with light grid lines
sns.set_theme(style='whitegrid', palette='Blues_d')

# This sets the default font size for all charts
plt.rcParams['font.size'] = 12

print("=" * 50)
print("RETAIL SALES ANALYSIS")
print("=" * 50)

# ============================================================
# STEP 2: LOAD THE DATA
# ============================================================

# pd.read_csv() reads a CSV file into a DataFrame
# A DataFrame is like a spreadsheet table in Python
# parse_dates tells pandas that OrderDate column contains dates
df_raw = pd.read_csv('data/retail_raw.csv', parse_dates=['OrderDate'])

print(f"\nRaw data loaded: {len(df_raw)} rows, {df_raw.shape[1]} columns")

# ============================================================
# STEP 3: CLEAN THE DATA
# ============================================================
# Rule 1: ALWAYS work on a copy, never change the original
# .copy() creates a brand new independent copy of the table
df = df_raw.copy()

print("\n--- CLEANING ---")

# Remove duplicate rows
# Sometimes data gets entered twice — drop_duplicates removes exact copies
# keep='first' = keep the first one, delete the rest
before = len(df)
df = df.drop_duplicates(keep='first')
print(f"Duplicates removed: {before - len(df)} rows")

# Fix text columns — real data is always inconsistent
# .str.strip() removes spaces at start and end:  "  North  " → "North"
# .str.title() fixes capitalisation: "NORTH" or "north" → "North"
for col in ['CustomerName', 'Region', 'Status', 'Product', 'Category']:
    df[col] = df[col].str.strip().str.title()

print("Text columns standardised (casing + whitespace)")

# Fix invalid numbers
# Quantity and UnitPrice should never be zero or negative
# .loc[condition, column] = value  means: find rows where condition is true, set that column to NaN
# NaN means "missing value" in pandas
df.loc[df['Quantity'] <= 0, 'Quantity'] = None
df.loc[df['UnitPrice'] <= 0, 'UnitPrice'] = None
print("Invalid quantities and prices set to NaN")

# Handle missing values (NaN)
# .dropna(subset=['col']) removes rows where that column is empty
# We drop rows with no CustomerName because they are useless
df = df.dropna(subset=['CustomerName'])

# .fillna() replaces NaN with a value we choose
# For Region and Status: fill with 'Unknown' so we keep the row
df['Region'] = df['Region'].fillna('Unknown')
df['Status'] = df['Status'].fillna('Unknown')

# For numbers: fill with the median (middle value)
# We use median not mean because mean is affected by outliers
df['Quantity']  = df['Quantity'].fillna(df['Quantity'].median())
df['UnitPrice'] = df['UnitPrice'].fillna(df['UnitPrice'].median())

print(f"Nulls handled. Clean rows remaining: {len(df)}")

# ============================================================
# STEP 4: ADD CALCULATED COLUMNS
# ============================================================
# These are new columns we calculate from existing ones
# Called "feature engineering" in data analyst jobs

# Revenue = Quantity × UnitPrice
# .round(2) rounds to 2 decimal places (pence)
df['Revenue'] = (df['Quantity'] * df['UnitPrice']).round(2)

# Extract parts of the date — needed for time analysis
# .dt.month_name() gives "January", "February" etc
# .dt.month gives 1, 2, 3 etc (needed for sorting)
# .dt.day_name() gives "Monday", "Tuesday" etc
df['Month']       = df['OrderDate'].dt.month_name()
df['MonthNum']    = df['OrderDate'].dt.month   # for sorting
df['DayOfWeek']   = df['OrderDate'].dt.day_name()
df['Quarter']     = df['OrderDate'].dt.quarter

print("Revenue, Month, DayOfWeek, Quarter columns added")

# ============================================================
# STEP 5: PRINT SUMMARY STATS
# ============================================================
print("\n" + "=" * 50)
print("BUSINESS SUMMARY")
print("=" * 50)
print(f"Total Revenue:       £{df['Revenue'].sum():>12,.2f}")
print(f"Total Orders:        {len(df):>12,}")
print(f"Avg Order Value:     £{df['Revenue'].mean():>12,.2f}")
print(f"Unique Customers:    {df['CustomerID'].nunique():>12,}")
print(f"Best Month:          {df.groupby('Month')['Revenue'].sum().idxmax():>12}")
print(f"Top Product:         {df.groupby('Product')['Revenue'].sum().idxmax():>12}")
print(f"Top Region:          {df.groupby('Region')['Revenue'].sum().idxmax():>12}")

# ============================================================
# CHART 1: Monthly Revenue Trend (Line Chart)
# ============================================================
# Business question: How did revenue change month by month?

print("\n--- Creating Chart 1: Monthly Revenue Trend ---")

# Group data by month, sum the revenue
# We need MonthNum to sort correctly (Jan=1, Feb=2 etc)
monthly = (
    df.groupby(['MonthNum', 'Month'])['Revenue']
    .sum()
    .reset_index()
    .sort_values('MonthNum')  # sort by month NUMBER not name
)

# Create the figure (canvas) and axis (the actual chart area)
# figsize=(12,5) sets width=12 inches, height=5 inches
fig, ax = plt.subplots(figsize=(12, 5))

# Plot the line
# x = month names, y = revenue values
# marker='o' adds a dot at each data point
# linewidth=2.5 makes the line thicker
# color sets the line colour
ax.plot(monthly['Month'], monthly['Revenue'],
        marker='o', linewidth=2.5, color='#2196F3', markersize=8)

# Fill the area under the line with a light blue colour
# alpha=0.1 makes it 10% opaque (very transparent)
ax.fill_between(monthly['Month'], monthly['Revenue'], alpha=0.1, color='#2196F3')

# Add the revenue value as a label above each data point
for i, row in monthly.iterrows():
    ax.annotate(
        f"£{row['Revenue']:,.0f}",          # the text to show
        (row['Month'], row['Revenue']),      # position
        textcoords="offset points",          # offset from the point
        xytext=(0, 10),                      # 10 points above the dot
        ha='center', fontsize=9, color='#333'
    )

# Labels and title
ax.set_title('Monthly Revenue Trend — 2024', fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('Month', fontsize=12)
ax.set_ylabel('Revenue (£)', fontsize=12)

# Format y-axis to show £ sign with commas: £10,000 not 10000
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'£{x:,.0f}'))

# Rotate x-axis labels so they don't overlap
plt.xticks(rotation=45, ha='right')

# tight_layout() stops labels getting cut off at the edges
plt.tight_layout()

# Save the chart as a PNG file in the charts folder
plt.savefig('charts/01_monthly_revenue.png', dpi=150, bbox_inches='tight')
plt.close()  # close the chart to free memory — important when making many charts
print("  Saved: charts/01_monthly_revenue.png")

# ============================================================
# CHART 2: Revenue by Product (Bar Chart)
# ============================================================
# Business question: Which products make the most money?

print("--- Creating Chart 2: Revenue by Product ---")

# Group by Product, sum revenue, sort highest to lowest
product_rev = (
    df.groupby('Product')['Revenue']
    .sum()
    .reset_index()
    .sort_values('Revenue', ascending=False)  # False = highest first
)

fig, ax = plt.subplots(figsize=(10, 6))

# sns.barplot = seaborn bar chart
# hue='Product' + legend=False colours each bar differently
# palette='Blues_d' = dark-to-light blue colour scheme
bars = sns.barplot(
    data=product_rev,
    x='Product',
    y='Revenue',
    hue='Product',
    palette='Blues_d',
    legend=False,
    ax=ax
)

# Add value labels on top of each bar
for bar in ax.patches:
    height = bar.get_height()
    if height > 0:
        ax.text(
            bar.get_x() + bar.get_width() / 2,  # centre of bar
            height + 500,                         # just above bar
            f'£{height:,.0f}',
            ha='center', va='bottom', fontsize=9, fontweight='bold'
        )

ax.set_title('Total Revenue by Product', fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('Product', fontsize=12)
ax.set_ylabel('Total Revenue (£)', fontsize=12)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'£{x:,.0f}'))
plt.tight_layout()
plt.savefig('charts/02_revenue_by_product.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Saved: charts/02_revenue_by_product.png")

# ============================================================
# CHART 3: Revenue by Region (Horizontal Bar)
# ============================================================
# Business question: Which region is performing best?

print("--- Creating Chart 3: Revenue by Region ---")

region_rev = (
    df.groupby('Region')['Revenue']
    .sum()
    .reset_index()
    .sort_values('Revenue', ascending=True)  # True = smallest at bottom (looks better horizontal)
)

fig, ax = plt.subplots(figsize=(9, 5))

# Horizontal bar chart — good when you have text labels that would overlap vertically
bars = ax.barh(region_rev['Region'], region_rev['Revenue'], color='#2196F3', edgecolor='white')

# Add value labels at the end of each bar
for bar in bars:
    width = bar.get_width()
    ax.text(
        width + 500,                 # just past the end of the bar
        bar.get_y() + bar.get_height() / 2,  # middle of bar height
        f'£{width:,.0f}',
        va='center', fontsize=10, fontweight='bold'
    )

ax.set_title('Total Revenue by Region', fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('Total Revenue (£)', fontsize=12)
ax.set_ylabel('Region', fontsize=12)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'£{x:,.0f}'))
plt.tight_layout()
plt.savefig('charts/03_revenue_by_region.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Saved: charts/03_revenue_by_region.png")

# ============================================================
# CHART 4: Order Status Breakdown (Pie Chart)
# ============================================================
# Business question: What % of orders are completed vs cancelled?

print("--- Creating Chart 4: Order Status Breakdown ---")

# value_counts() counts how many times each value appears
status_counts = df['Status'].value_counts()

fig, ax = plt.subplots(figsize=(8, 6))

# Pie chart
# autopct='%1.1f%%' shows percentage on each slice e.g. "62.3%"
# startangle=90 starts the first slice at the top
# explode separates the slices slightly for visibility
explode = [0.05] * len(status_counts)  # 5% gap for each slice
colors  = ['#2196F3', '#64B5F6', '#BBDEFB', '#90CAF9']

wedges, texts, autotexts = ax.pie(
    status_counts.values,
    labels=status_counts.index,
    autopct='%1.1f%%',
    startangle=90,
    explode=explode,
    colors=colors[:len(status_counts)],
    textprops={'fontsize': 11}
)

# Make percentage text bold
for autotext in autotexts:
    autotext.set_fontweight('bold')

ax.set_title('Order Status Breakdown', fontsize=16, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig('charts/04_order_status.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Saved: charts/04_order_status.png")

# ============================================================
# CHART 5: Top 10 Customers by Revenue (Bar Chart)
# ============================================================
# Business question: Who are our most valuable customers?

print("--- Creating Chart 5: Top 10 Customers ---")

# groupby CustomerName, sum revenue, get top 10
# .nlargest(10) is cleaner than .sort_values().head(10)
top_customers = (
    df.groupby('CustomerName')['Revenue']
    .sum()
    .nlargest(10)
    .reset_index()
    .sort_values('Revenue', ascending=True)  # ascending for horizontal bar
)

fig, ax = plt.subplots(figsize=(10, 6))

bars = ax.barh(top_customers['CustomerName'], top_customers['Revenue'],
               color='#1976D2', edgecolor='white')

for bar in bars:
    width = bar.get_width()
    ax.text(width + 200, bar.get_y() + bar.get_height() / 2,
            f'£{width:,.0f}', va='center', fontsize=9, fontweight='bold')

ax.set_title('Top 10 Customers by Total Revenue', fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('Total Revenue (£)', fontsize=12)
ax.set_ylabel('Customer', fontsize=12)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'£{x:,.0f}'))
plt.tight_layout()
plt.savefig('charts/05_top_customers.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Saved: charts/05_top_customers.png")

# ============================================================
# CHART 6: Revenue Heatmap — Month vs Category
# ============================================================
# Business question: When does each product category sell best?

print("--- Creating Chart 6: Revenue Heatmap ---")

# pivot_table reshapes the data into a grid
# rows = Category, columns = Month, values = Revenue sum
heatmap_data = df.pivot_table(
    values='Revenue',
    index='Category',
    columns='MonthNum',   # use number so months sort correctly
    aggfunc='sum',
    fill_value=0          # replace NaN with 0
)

# Rename columns from numbers to month abbreviations
month_names = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',
               7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}
heatmap_data.columns = [month_names.get(c, c) for c in heatmap_data.columns]

fig, ax = plt.subplots(figsize=(14, 4))

# sns.heatmap draws a colour-coded grid
# annot=True shows the number in each cell
# fmt=',.0f' formats numbers with commas and no decimals
# cmap='Blues' = colour scheme from white (low) to dark blue (high)
sns.heatmap(
    heatmap_data,
    annot=True,
    fmt=',.0f',
    cmap='Blues',
    linewidths=0.5,
    ax=ax,
    cbar_kws={'label': 'Revenue (£)'}
)

ax.set_title('Revenue Heatmap: Category × Month', fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('Month', fontsize=12)
ax.set_ylabel('Category', fontsize=12)
plt.tight_layout()
plt.savefig('charts/06_heatmap.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Saved: charts/06_heatmap.png")

# ============================================================
# DONE
# ============================================================
print("\n" + "=" * 50)
print("ALL DONE!")
print("=" * 50)
print("6 charts saved in the charts/ folder")
print("Ready to upload to GitHub")