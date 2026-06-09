import pandas as pd
from pathlib import Path

# File paths (repo root)
INPUT_CSV = "master_timetable.csv"
OUTPUT_CSV = "master_timetable_pivoted.csv"

# Read CSV
if not Path(INPUT_CSV).exists():
    raise SystemExit(f"Input file not found: {INPUT_CSV}")

df = pd.read_csv(INPUT_CSV)

# Create joined-entry string
df['Faculty'] = df['Faculty'].fillna('')

def make_entry(row):
    room = str(row.get('Room',''))
    course = str(row.get('Course',''))
    faculty = str(row.get('Faculty',''))
    entry = f"{room} — {course} ({faculty})"
    return entry

df['entry'] = df.apply(make_entry, axis=1)

# Preserve weekday order (only include days present)
day_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
present_days = [d for d in day_order if d in df['Day'].unique()]

df['Day'] = pd.Categorical(df['Day'], categories=present_days, ordered=True)

# Preserve time slot order as they appear in the file
time_order = list(dict.fromkeys(df['Time_Slot'].tolist()))
df['Time_Slot'] = pd.Categorical(df['Time_Slot'], categories=time_order, ordered=True)

# Group and join multiple entries in same Day+Time_Slot cell
pivot = df.groupby(['Time_Slot', 'Day'])['entry'] \
          .apply(lambda x: ' | '.join(x.dropna().astype(str))) \
          .unstack(fill_value='')

# Ensure columns are in Monday->Friday order (or present_days)
pivot = pivot.reindex(columns=present_days, fill_value='')

# Reset index so Time_Slot becomes a column
pivot_reset = pivot.reset_index()

# Save to CSV
pivot_reset.to_csv(OUTPUT_CSV, index=False)

print(f"Pivot saved to {OUTPUT_CSV}")
