from psychopy import data
import pandas as pd

# Load the trial list
trialList = data.importConditions('../egyptian_list3.csv')

# Initialize variables for finding the longest word
longestWordCount = 0
longestWord = 'none'

# Create a list to store word counts
word_counts = []

# Process each trial
for trialIndex in range(len(trialList)):
    words = trialList[trialIndex]['sentence'].split()
    word_counts.append(len(words))  # Append word count for each sentence
    for word in words:
        if len(word) > longestWordCount:
            longestWordCount = len(word)
            longestWord = word

# Convert trialList to a DataFrame
df = pd.DataFrame(trialList)

# Add the word counts as a new column
df['word_count'] = word_counts

# Save the updated DataFrame to a new CSV file with proper encoding
output_file = '../egyptian_list3_updated.csv'
df.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"Updated file saved as {output_file}")
print(f"The longest word is '{longestWord}' with {longestWordCount} characters.")
