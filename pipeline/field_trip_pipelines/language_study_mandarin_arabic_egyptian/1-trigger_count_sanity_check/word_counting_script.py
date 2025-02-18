from psychopy import data
import pandas as pd


#CSV_FILE_NAME = 'egyptian_list1.csv'


# Load the trial list
#trialList = data.importConditions(r'C:\Users\hz3752\Box\MEG\Data\egyptian-language-study\sub-trigger\derivatives\\' + CSV_FILE_NAME)

FILE_PATH = 'derivatives/emirati_list4.csv'

#output_file = 'word_count_egyptian_list1.csv'
output_file = r'C:\Users\jp6550\Desktop\emirati\word_count_emirati_list4.csv'  # For Windows


trialList = data.importConditions(FILE_PATH)

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
df['wordcount'] = word_counts

# Save the updated DataFrame to a new CSV file with proper encoding

df.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"Updated file saved as {output_file}")
print(f"The longest word is '{longestWord}' with {longestWordCount} characters.")
