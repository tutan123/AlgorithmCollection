
# coding: utf-8

# In[1]:

# data from http://grouplens.org/datasets/movielens/


# In[2]:

import os
# data_folder = os.path.join(os.path.expanduser("~"), "Data", "ml-100k")
data_folder = ''
ratings_filename = os.path.join(data_folder, "u.data")


# In[3]:

import pandas as pd


# In[4]:

all_ratings = pd.read_csv(ratings_filename, delimiter="\t", header=None, names = ["UserID", "MovieID", "Rating", "Datetime"])
all_ratings["Datetime"] = pd.to_datetime(all_ratings['Datetime'],unit='s')
all_ratings[:5]


# In[5]:

# As you can see, there are no review for most movies, such as #213
all_ratings[all_ratings["UserID"] == 675].sort_values("MovieID")


# In[6]:

# Not all reviews are favourable! Our goal is "other recommended books", so we only want favourable reviews
all_ratings["Favorable"] = all_ratings["Rating"] > 3
all_ratings[10:15]


# In[7]:

all_ratings[all_ratings["UserID"] == 1][:5]


# In[8]:

# Sample the dataset. You can try increasing the size of the sample, but the run time will be considerably longer
ratings = all_ratings[all_ratings['UserID'].isin(range(200))]  # & ratings["UserID"].isin(range(100))]


# In[9]:

# We start by creating a dataset of each user's favourable reviews
favorable_ratings = ratings[ratings["Favorable"]]
favorable_ratings[:5]


# In[10]:

# We are only interested in the reviewers who have more than one review
favorable_reviews_by_users = dict((k, frozenset(v.values)) for k, v in favorable_ratings.groupby("UserID")["MovieID"])
print(favorable_reviews_by_users)
len(favorable_reviews_by_users)


# In[11]:

# Find out how many movies have favourable ratings
num_favorable_by_movie = ratings[["MovieID", "Favorable"]].groupby("MovieID").sum()
num_favorable_by_movie.sort_values("Favorable", ascending=False)[:5]


# In[12]:

from collections import defaultdict

def find_frequent_itemsets(favorable_reviews_by_users, k_1_itemsets, min_support):
    counts = defaultdict(int)
    for user, reviews in favorable_reviews_by_users.items():
        for itemset in k_1_itemsets:
            if itemset.issubset(reviews):
                for other_reviewed_movie in reviews - itemset:
                    current_superset = itemset | frozenset((other_reviewed_movie,))
                    counts[current_superset] += 1
    return dict([(itemset, frequency) for itemset, frequency in counts.items() if frequency >= min_support])


# In[13]:

import sys
frequent_itemsets = {}  # itemsets are sorted by length
min_support = 50

# k=1 candidates are the isbns with more than min_support favourable reviews
frequent_itemsets[1] = dict((frozenset((movie_id,)), row["Favorable"])
                                for movie_id, row in num_favorable_by_movie.iterrows()
                                if row["Favorable"] > min_support)

print("There are {} movies with more than {} favorable reviews".format(len(frequent_itemsets[1]), min_support))
sys.stdout.flush()
for k in range(2, 20):
    # Generate candidates of length k, using the frequent itemsets of length k-1
    # Only store the frequent itemsets
    cur_frequent_itemsets = find_frequent_itemsets(favorable_reviews_by_users, frequent_itemsets[k-1],
                                                   min_support)
    if len(cur_frequent_itemsets) == 0:
        print("Did not find any frequent itemsets of length {}".format(k))
        sys.stdout.flush()
        break
    else:
        print("I found {} frequent itemsets of length {}".format(len(cur_frequent_itemsets), k))
        #print(cur_frequent_itemsets)
        sys.stdout.flush()
        frequent_itemsets[k] = cur_frequent_itemsets
# We aren't interested in the itemsets of length 1, so remove those
del frequent_itemsets[1]


# In[14]:

print("Found a total of {0} frequent itemsets".format(sum(len(itemsets) for itemsets in frequent_itemsets.values())))


# In[15]:

# Now we create the association rules. First, they are candidates until the confidence has been tested
candidate_rules = []
for itemset_length, itemset_counts in frequent_itemsets.items():
    for itemset in itemset_counts.keys():
        for conclusion in itemset:
            premise = itemset - set((conclusion,))
            candidate_rules.append((premise, conclusion))
print("There are {} candidate rules".format(len(candidate_rules)))


# In[16]:

print(candidate_rules[:5])


# In[17]:

# Now, we compute the confidence of each of these rules. This is very similar to what we did in chapter 1
correct_counts = defaultdict(int)
incorrect_counts = defaultdict(int)
for user, reviews in favorable_reviews_by_users.items():
    for candidate_rule in candidate_rules:
        premise, conclusion = candidate_rule
        if premise.issubset(reviews):
            if conclusion in reviews:
                correct_counts[candidate_rule] += 1
            else:
                incorrect_counts[candidate_rule] += 1
rule_confidence = {candidate_rule: correct_counts[candidate_rule] / float(correct_counts[candidate_rule] + incorrect_counts[candidate_rule])
              for candidate_rule in candidate_rules}


# In[18]:

# Choose only rules above a minimum confidence level
min_confidence = 0.9


# In[19]:

# Filter out the rules with poor confidence
rule_confidence = {rule: confidence for rule, confidence in rule_confidence.items() if confidence > min_confidence}
print(len(rule_confidence))


# In[20]:

from operator import itemgetter
sorted_confidence = sorted(rule_confidence.items(), key=itemgetter(1), reverse=True)


# In[21]:

for index in range(5):
    print("Rule #{0}".format(index + 1))
    (premise, conclusion) = sorted_confidence[index][0]
    print("Rule: If a person recommends {0} they will also recommend {1}".format(premise, conclusion))
    print(" - Confidence: {0:.3f}".format(rule_confidence[(premise, conclusion)]))
    print("")


# In[22]:

# Even better, we can get the movie titles themselves from the dataset
movie_name_filename = os.path.join(data_folder, "u.item")
movie_name_data = pd.read_csv(movie_name_filename, delimiter="|", header=None, encoding = "mac-roman")
movie_name_data.columns = ["MovieID", "Title", "Release Date", "Video Release", "IMDB", "<UNK>", "Action", "Adventure",
                           "Animation", "Children's", "Comedy", "Crime", "Documentary", "Drama", "Fantasy", "Film-Noir",
                           "Horror", "Musical", "Mystery", "Romance", "Sci-Fi", "Thriller", "War", "Western"]


# In[23]:

def get_movie_name(movie_id):
    title_object = movie_name_data[movie_name_data["MovieID"] == movie_id]["Title"]
    title = title_object.values[0]
    return title


# In[24]:

get_movie_name(4)


# In[25]:

for index in range(5):
    print("Rule #{0}".format(index + 1))
    (premise, conclusion) = sorted_confidence[index][0]
    premise_names = ", ".join(get_movie_name(idx) for idx in premise)
    conclusion_name = get_movie_name(conclusion)
    print("Rule: If a person recommends {0} they will also recommend {1}".format(premise_names, conclusion_name))
    print(" - Confidence: {0:.3f}".format(rule_confidence[(premise, conclusion)]))
    print("")


# In[26]:

# Evaluation using test data
test_dataset = all_ratings[~all_ratings['UserID'].isin(range(200))]
test_favorable = test_dataset[test_dataset["Favorable"]]
#test_not_favourable = test_dataset[~test_dataset["Favourable"]]
test_favorable_by_users = dict((k, frozenset(v.values)) for k, v in test_favorable.groupby("UserID")["MovieID"])
#test_not_favourable_by_users = dict((k, frozenset(v.values)) for k, v in test_not_favourable.groupby("UserID")["MovieID"])
#test_users = test_dataset["UserID"].unique()


# In[27]:

test_dataset[:5]


# In[28]:

correct_counts = defaultdict(int)
incorrect_counts = defaultdict(int)
for user, reviews in test_favorable_by_users.items():
    for candidate_rule in candidate_rules:
        premise, conclusion = candidate_rule
        if premise.issubset(reviews):
            if conclusion in reviews:
                correct_counts[candidate_rule] += 1
            else:
                incorrect_counts[candidate_rule] += 1


# In[29]:

test_confidence = {candidate_rule: correct_counts[candidate_rule] / float(correct_counts[candidate_rule] + incorrect_counts[candidate_rule])
                   for candidate_rule in rule_confidence}
print(len(test_confidence))


# In[30]:

sorted_test_confidence = sorted(test_confidence.items(), key=itemgetter(1), reverse=True)
print(sorted_test_confidence[:5])


# In[31]:

for index in range(10):
    print("Rule #{0}".format(index + 1))
    (premise, conclusion) = sorted_confidence[index][0]
    premise_names = ", ".join(get_movie_name(idx) for idx in premise)
    conclusion_name = get_movie_name(conclusion)
    print("Rule: If a person recommends {0} they will also recommend {1}".format(premise_names, conclusion_name))
    print(" - Train Confidence: {0:.3f}".format(rule_confidence.get((premise, conclusion), -1)))
    print(" - Test Confidence: {0:.3f}".format(test_confidence.get((premise, conclusion), -1)))
    print("")


# In[31]:



