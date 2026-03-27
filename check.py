import pandas as pd
df = pd.read_csv('transformed_safety.csv')
print(df['risk_category'].value_counts())
print()
print(df[df['year']==2022].nlargest(10,'safety_score')[['state_name','district_name','safety_score','risk_category','total_crimes']])