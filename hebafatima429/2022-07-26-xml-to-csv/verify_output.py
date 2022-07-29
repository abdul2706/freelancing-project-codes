import pandas as pd
df_given = pd.read_csv('heba_test_1_final.csv')
df_output = pd.read_csv('output.csv')
print(all(df_given == df_output))
