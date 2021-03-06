#!/usr/bin/env python
# coding: utf-8

# # Project 6: Analyzing Stock Sentiment from Twits
# ## Instructions
# Each problem consists of a function to implement and instructions on how to implement the function.  The parts of the function that need to be implemented are marked with a `# TODO` comment.
# 
# ## Packages
# When you implement the functions, you'll only need to you use the packages you've used in the classroom, like [Pandas](https://pandas.pydata.org/) and [Numpy](http://www.numpy.org/). These packages will be imported for you. We recommend you don't add any import statements, otherwise the grader might not be able to run your code.
# 
# ### Load Packages

# In[83]:


import json
import nltk
import os
import random
import re
import torch

from torch import nn, optim
import torch.nn.functional as F


# In[84]:


import numpy as np


# ## Introduction
# When deciding the value of a company, it's important to follow the news. For example, a product recall or natural disaster in a company's product chain. You want to be able to turn this information into a signal. Currently, the best tool for the job is a Neural Network. 
# 
# For this project, you'll use posts from the social media site [StockTwits](https://en.wikipedia.org/wiki/StockTwits). The community on StockTwits is full of investors, traders, and entrepreneurs. Each message posted is called a Twit. This is similar to Twitter's version of a post, called a Tweet. You'll build a model around these twits that generate a sentiment score.
# 
# We've collected a bunch of twits, then hand labeled the sentiment of each. To capture the degree of sentiment, we'll use a five-point scale: very negative, negative, neutral, positive, very positive. Each twit is labeled -2 to 2 in steps of 1, from very negative to very positive respectively. You'll build a sentiment analysis model that will learn to assign sentiment to twits on its own, using this labeled data.
# 
# The first thing we should to do, is load the data.
# 
# ## Import Twits 
# ### Load Twits Data 
# This JSON file contains a list of objects for each twit in the `'data'` field:
# 
# ```
# {'data':
#   {'message_body': 'Neutral twit body text here',
#    'sentiment': 0},
#   {'message_body': 'Happy twit body text here',
#    'sentiment': 1},
#    ...
# }
# ```
# 
# The fields represent the following:
# 
# * `'message_body'`: The text of the twit.
# * `'sentiment'`: Sentiment score for the twit, ranges from -2 to 2 in steps of 1, with 0 being neutral.
# 
# 
# To see what the data look like by printing the first 10 twits from the list. 

# In[85]:


with open(os.path.join('..', '..', 'data', 'project_6_stocktwits', 'twits.json'), 'r') as f:
    twits = json.load(f)

print(twits['data'][:10])


# ### Length of Data
# Now let's look at the number of twits in dataset. Print the number of twits below.

# In[3]:


"""print out the number of twits"""
print(len(twits['data']))


# ### Split Message Body and Sentiment Score

# In[88]:


messages = [twit['message_body'] for twit in twits['data']]
# Since the sentiment scores are discrete, we'll scale the sentiments to 0 to 4 for use in our network
sentiments = [twit['sentiment'] + 2 for twit in twits['data']]
messages[:10]


# ## Preprocessing the Data
# With our data in hand we need to preprocess our text. These twits are collected by filtering on ticker symbols where these are denoted with a leader $ symbol in the twit itself. For example,
# 
# `{'message_body': 'RT @google Our annual look at the year in Google blogging (and beyond) http://t.co/sptHOAh8 $GOOG',
#  'sentiment': 0}`
# 
# The ticker symbols don't provide information on the sentiment, and they are in every twit, so we should remove them. This twit also has the `@google` username, again not providing sentiment information, so we should also remove it. We also see a URL `http://t.co/sptHOAh8`. Let's remove these too.
# 
# The easiest way to remove specific words or phrases is with regex using the `re` module. You can sub out specific patterns with a space:
# 
# ```python
# re.sub(pattern, ' ', text)
# ```
# This will substitute a space with anywhere the pattern matches in the text. Later when we tokenize the text, we'll split appropriately on those spaces.

# ### Pre-Processing

# In[90]:


nltk.download('wordnet')
nltk.download('stopwords')


def preprocess(message):
    """
    This function takes a string as input, then performs these operations: 
        - lowercase
        - remove URLs
        - remove ticker symbols 
        - removes punctuation
        - tokenize by splitting the string on whitespace 
        - removes any single character tokens
    
    Parameters
    ----------
        message : The text message to be preprocessed.
        
    Returns
    -------
        tokens: The preprocessed text into tokens.
    """ 
    #TODO: Implement 
    
    # Lowercase the twit message
    text = message.lower()
    #print(text)
    
    # Replace URLs with a space in the message
    text = re.sub('https?:\/\/[a-zA-Z0-9@:%._\/+~#=?&;-]*', ' ', text)
    #print(text)
    
    # Replace ticker symbols with a space. The ticker symbols are any stock symbol that starts with $.
    text = re.sub('\$[a-zA-Z0-9]*', ' ', text)
    #print(text)
    
    # Replace StockTwits usernames with a space. The usernames are any word that starts with @.
    text = re.sub('\@[a-zA-Z0-9]*', ' ', text)
    #print(text)

    # Replace everything not a letter with a space
    text = re.sub('[^a-zA-Z]', ' ', text)
    #print(text)
    
    # Tokenize by splitting the string on whitespace into a list of words
    #text_split = text.split('\n')
    #text = ' '.join(text_split)
    tokens = text.split()
    #print(tokens)

    # Lemmatize words using the WordNetLemmatizer. You can ignore any word that is not longer than one character.
    wnl = nltk.stem.WordNetLemmatizer()
    #stop_words = set(nltk.corpus.stopwords.words('english'))
    #tokens = [wnl.lemmatize(wnl.lemmatize(word, 'n'), 'v') for word in tokens if word not in stop_words]
    tokens = [wnl.lemmatize(wnl.lemmatize(word, 'n'), 'v') for word in tokens]
    #print(tokens)
    
    return tokens


# ### Preprocess All the Twits 
# Now we can preprocess each of the twits in our dataset. Apply the function `preprocess` to all the twit messages.

# In[94]:


# TODO Implement
tokenized = [preprocess(i) for i in messages]
print(tokenized[:10])


# ### Bag of Words
# Now with all of our messages tokenized, we want to create a vocabulary and count up how often each word appears in our entire corpus. Use the [`Counter`](https://docs.python.org/3.1/library/collections.html#collections.Counter) function to count up all the tokens.

# In[93]:


from collections import Counter


"""
Create a vocabulary by using Bag of words
"""

# TODO: Implement 
all_words = [word for message in tokenized for word in message]
counts = Counter(all_words)
bow = sorted(counts, key=counts.get, reverse=True)
print(bow[:20])


# ### Frequency of Words Appearing in Message
# With our vocabulary, now we'll remove some of the most common words such as 'the', 'and', 'it', etc. These words don't contribute to identifying sentiment and are really common, resulting in a lot of noise in our input. If we can filter these out, then our network should have an easier time learning.
# 
# We also want to remove really rare words that show up in a only a few twits. Here you'll want to divide the count of each word by the number of messages. Then remove words that only appear in some small fraction of the messages.

# In[202]:


"""
Set the following variables:
    freqs
    low_cutoff
    high_cutoff
    K_most_common
"""

# TODO Implement
freqs = {}
num_words = len(all_words)
print('len(all_words): ', len(all_words))
for key in counts:
    freqs[key] = counts[key]/num_words
print('len(freqs): ', len(freqs))

# Float that is the frequency cutoff. Drop words with a frequency that is lower or equal to this number.
low_cutoff = 0.00001
# low_cutoff = 0.000001

# Integer that is the cut off for most common words. Drop words that are the `high_cutoff` most common words.
high_cutoff = 10

# The k most common words in the corpus. Use `high_cutoff` as the k.
K_most_common, K_most_common_values = zip(*counts.most_common()[:high_cutoff])

filtered_words = [word for word in freqs if (freqs[word] > low_cutoff and word not in K_most_common)]
print(K_most_common)
print('len(filtered_words): ', len(filtered_words))


# ### Updating Vocabulary by Removing Filtered Words
# Let's creat three variables that will help with our vocabulary.

# In[246]:


"""
Set the following variables:
    vocab
    id2vocab
    filtered
"""

#TODO Implement

from tqdm import tqdm as tqdm

# A dictionary for the `filtered_words`. The key is the word and value is an id that represents the word. 
vocab = {word: ii for ii, word in enumerate(filtered_words, 1)}
# Reverse of the `vocab` dictionary. The key is word id and value is the word. 
id2vocab = {v: k for k, v in vocab.items()}
# tokenized with the words not in `filtered_words` removed.
print(len(tokenized))
print(filtered[:10])
# Memo: Don't use filtered_word but use vocab instead as looking up a dictionary is much faster
filtered = [[word for word in message if word in vocab] for message in tokenized]


# ### Balancing the classes
# Let's do a few last pre-processing steps. If we look at how our twits are labeled, we'll find that 50% of them are neutral. This means that our network will be 50% accurate just by guessing 0 every single time. To help our network learn appropriately, we'll want to balance our classes.
# That is, make sure each of our different sentiment scores show up roughly as frequently in the data.
# 
# What we can do here is go through each of our examples and randomly drop twits with neutral sentiment. What should be the probability we drop these twits if we want to get around 20% neutral twits starting at 50% neutral? We should also take this opportunity to remove messages with length 0.

# In[247]:


balanced = {'messages': [], 'sentiments':[]}

n_neutral = sum(1 for each in sentiments if each == 2)
N_examples = len(sentiments)
keep_prob = (N_examples - n_neutral)/4/n_neutral

for idx, sentiment in enumerate(sentiments):
    message = filtered[idx]
    if len(message) == 0:
        # skip this message because it has length zero
        continue
    elif sentiment != 2 or random.random() < keep_prob:
        balanced['messages'].append(message)
        balanced['sentiments'].append(sentiment) 


# If you did it correctly, you should see the following result 

# In[248]:


n_neutral = sum(1 for each in balanced['sentiments'] if each == 2)
N_examples = len(balanced['sentiments'])
n_neutral/N_examples


# Finally let's convert our tokens into integer ids which we can pass to the network.

# In[249]:


# token_ids = [[vocab[word] for word in message] for message in balanced['messages']]
# sentiments = balanced['sentiments']

token_ids = [[vocab[word] for word in message] for message in balanced['messages']]
sentiments = balanced['sentiments']
len(token_ids)


# ## Neural Network
# Now we have our vocabulary which means we can transform our tokens into ids, which are then passed to our network. So, let's define the network now!
# 
# Here is a nice diagram showing the network we'd like to build: 
# 
# #### Embed -> RNN -> Dense -> Softmax
# ### Implement the text classifier
# Before we build text classifier, if you remember from the other network that you built in  "Sentiment Analysis with an RNN"  exercise  - which there, the network called " SentimentRNN", here we named it "TextClassifer" - consists of three main parts: 1) init function `__init__` 2) forward pass `forward`  3) hidden state `init_hidden`. 
# 
# This network is pretty similar to the network you built expect in the  `forward` pass, we use softmax instead of sigmoid. The reason we are not using sigmoid is that the output of NN is not a binary. In our network, sentiment scores have 5 possible outcomes. We are looking for an outcome with the highest probability thus softmax is a better choice.

# In[250]:


#Just to check the device
if(torch.cuda.is_available()):
    print('Training on GPU.')
else:
    print('No GPU Available, training on CPU.')


# In[214]:


class TextClassifier(nn.Module):
    def __init__(self, vocab_size, embed_size, lstm_size, output_size, lstm_layers=1, dropout=0.1):
        """
        Initialize the model by setting up the layers.
        
        Parameters
        ----------
            vocab_size : The vocabulary size.
            embed_size : The embedding layer size.
            lstm_size : The LSTM layer size.
            output_size : The output size.
            lstm_layers : The number of LSTM layers.
            dropout : The dropout probability.
        """
        
        super().__init__()
        self.vocab_size = vocab_size
        self.embed_size = embed_size
        self.lstm_size = lstm_size
        self.output_size = output_size
        self.lstm_layers = lstm_layers
        self.dropout = dropout
        
        # TODO Implement        

        # Setup embedding layer
        self.embedding = nn.Embedding(vocab_size, embed_size)
        
        # Setup additional layers
        self.lstm = nn.LSTM(embed_size, lstm_size, lstm_layers,
                            dropout=dropout, batch_first=False)
        self.dropout = nn.Dropout(0.2)
        self.fc = nn.Linear(lstm_size, output_size)
        self.softmax = nn.LogSoftmax(dim=1)

    def init_hidden(self, batch_size):
        """ 
        Initializes hidden state
        
        Parameters
        ----------
            batch_size : The size of batches.
        
        Returns
        -------
            hidden_state
            
        """
        
        # TODO Implement 
        
        # Create two new tensors with sizes n_layers x batch_size x hidden_dim,
        # initialized to zero, for hidden state and cell state of LSTM
        weight = next(self.parameters()).data
        
        hidden = (weight.new(self.lstm_layers, batch_size, self.lstm_size).zero_(),
                  weight.new(self.lstm_layers, batch_size, self.lstm_size).zero_())
        
        return hidden


    def forward(self, nn_input, hidden_state):
        """
        Perform a forward pass of our model on nn_input.
        
        Parameters
        ----------
            nn_input : The batch of input to the NN.
            hidden_state : The LSTM hidden state.

        Returns
        -------
            logps: log softmax output
            hidden_state: The new hidden state.

        """
        
        # TODO Implement 
        batch_size = nn_input.size(0)
        
        nn_input = nn_input.long()
        embeds = self.embedding(nn_input)
        
        lstm_out, hidden_state = self.lstm(embeds, hidden_state)
        
        # Stack up LSTM outputs
        # lstm_out = lstm_out.contiguous().view(-1, self.lstm_size)
        lstm_out = lstm_out[-1,:,:]
        
        out = self.dropout(lstm_out)
        out = self.fc(out)
        logps = self.softmax(out)
        
        return logps, hidden_state


# ### View Model

# In[251]:


model = TextClassifier(len(vocab), 10, 6, 5, dropout=0.1, lstm_layers=2)
model.embedding.weight.data.uniform_(-1, 1)
input = torch.randint(0, 1000, (5, 4), dtype=torch.int64)
hidden = model.init_hidden(4)

logps, _ = model.forward(input, hidden)
print(logps)
print(torch.exp(logps))


# ## Training
# ### DataLoaders and Batching
# Now we should build a generator that we can use to loop through our data. It'll be more efficient if we can pass our sequences in as batches. Our input tensors should look like `(sequence_length, batch_size)`. So if our sequences are 40 tokens long and we pass in 25 sequences, then we'd have an input size of `(40, 25)`.
# 
# If we set our sequence length to 40, what do we do with messages that are more or less than 40 tokens? For messages with fewer than 40 tokens, we will pad the empty spots with zeros. We should be sure to **left** pad so that the RNN starts from nothing before going through the data. If the message has 20 tokens, then the first 20 spots of our 40 long sequence will be 0. If a message has more than 40 tokens, we'll just keep the first 40 tokens.

# In[252]:


def dataloader(messages, labels, sequence_length=30, batch_size=32, shuffle=False):
    """ 
    Build a dataloader.
    """
    if shuffle:
        indices = list(range(len(messages)))
        random.shuffle(indices)
        messages = [messages[idx] for idx in indices]
        labels = [labels[idx] for idx in indices]

    total_sequences = len(messages)

    for ii in range(0, total_sequences, batch_size):
        batch_messages = messages[ii: ii+batch_size]
        
        # First initialize a tensor of all zeros
        batch = torch.zeros((sequence_length, len(batch_messages)), dtype=torch.int64)
        for batch_num, tokens in enumerate(batch_messages):
            token_tensor = torch.tensor(tokens)
            # Left pad!
            start_idx = max(sequence_length - len(token_tensor), 0)
            batch[start_idx:, batch_num] = token_tensor[:sequence_length]
        
        label_tensor = torch.tensor(labels[ii: ii+len(batch_messages)])
        
        yield batch, label_tensor


# ### Training and  Validation
# With our data in nice shape, we'll split it into training and validation sets.

# In[253]:


"""
Split data into training and validation datasets. Use an appropriate split size.
The features are the `token_ids` and the labels are the `sentiments`.
"""   

# TODO Implement 

valid_split = int(len(token_ids)*.9)
train_features = token_ids[:valid_split]  
valid_features = token_ids[valid_split:]
train_labels = sentiments[:valid_split] 
valid_labels = sentiments[valid_split:]
print("len(token_ids): ", len(token_ids))
print("len(train_features): ", len(train_features))
print("len(valid_features): ", len(valid_features))


# In[200]:


text_batch, labels = next(iter(dataloader(train_features, train_labels, sequence_length=20, batch_size=64)))
model = TextClassifier(len(vocab)+1, 200, 128, 5, dropout=0.)
hidden = model.init_hidden(64)
logps, hidden = model.forward(text_batch, hidden)
print(logps)


# ### Training
# It's time to train the neural network!

# In[259]:


# device = torch.device("cpu")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = TextClassifier(len(vocab)+1, 1024, 512, 5, lstm_layers=2, dropout=0.2)
model.embedding.weight.data.uniform_(-1, 1)
model.to(device)


# In[258]:


"""
Train your model with dropout. Make sure to clip your gradients.
Print the training loss, validation loss, and validation accuracy for every 100 steps.
"""

epochs = 3
batch_size = 512
learning_rate = 0.001
clip = 5  # for gradient clipping
print_every = 100
criterion = nn.NLLLoss()
optimizer = optim.Adam(model.parameters(), lr=learning_rate)
model.train()
for epoch in range(epochs):
    print('Starting epoch {}'.format(epoch + 1))
    
    steps = 0
    
    for text_batch, labels in dataloader(train_features, 
                                         train_labels, 
                                         batch_size=batch_size, 
                                         sequence_length=20, 
                                         shuffle=True):
        steps += 1
        
        val_h = model.init_hidden(labels.shape[0])
        
        # Set Device
        text_batch, labels = text_batch.to(device), labels.to(device)
        
        for each in val_h:
            each.to(device)
        
        # TODO Implement: Train Model
        
        # zero accumulated gradients
        model.zero_grad()
        # get the output from the model
        output, val_h = model(text_batch, val_h)
        # calculate the loss and perform backprop
        loss = criterion(output.squeeze(), labels) # https://knowledge.udacity.com/questions/31313
        loss.backward()
        
        # `clip_grad_norm` helps prevent the exploding gradient problem in RNNs / LSTMs.
        nn.utils.clip_grad_norm_(model.parameters(), clip)
        optimizer.step() 
        
        if steps % print_every == 0:
            model.eval()
            
            val_losses = []
            
            for inputs, labels in dataloader(valid_features, 
                                             valid_labels, 
                                             batch_size=batch_size):
                # Creating new variables for the hidden state, otherwise
                # we'd backprop through the entire training history
                inputs, labels = inputs.to(device), labels.to(device)
                
                val_h = model.init_hidden(labels.shape[0])
                
                for each in val_h:
                    each.to(device) 
                output, val_h = model(inputs, val_h)
                
                val_loss = criterion(output.squeeze(), labels)
                val_losses.append(val_loss.item())
            # TODO Implement: Print metrics
            
            model.train()
            import numpy as np
            print("Epoch: {}/{}...".format(epoch+1, epochs),
                  "Step: {}...".format(steps),
                  "Loss: {:.6f}...".format(loss.item()),
                  "Val Loss: {:.6f}".format(np.mean(val_losses)))


# ## Making Predictions
# ### Prediction 
# Okay, now that you have a trained model, try it on some new twits and see if it works appropriately. Remember that for any new text, you'll need to preprocess it first before passing it to the network. Implement the `predict` function to generate the prediction vector from a message.

# In[242]:


def predict(text, model, vocab):
    """ 
    Make a prediction on a single sentence.

    Parameters
    ----------
        text : The string to make a prediction on.
        model : The model to use for making the prediction.
        vocab : Dictionary for word to word ids. The key is the word and the value is the word id.

    Returns
    -------
        pred : Prediction vector
    """    
    
    # TODO Implement
    
    tokens = preprocess(text)
    
    # Filter non-vocab words
    tokens = [word for word in tokens if word in vocab]
    
    # Convert words to ids
    tokens = [vocab[word] for word in tokens]
        
    # Adding a batch dimension
    text_input = torch.tensor(tokens).view(-1,1)

    # Get the NN output
    
    hidden = model.init_hidden(1)
    logps, _ = model.forward(text_input, hidden)
    
    # Take the exponent of the NN output to get a range of 0 to 1 for each label.
    pred = torch.exp(logps)
#     print(hidden)
#     print(text_input.shape)
    
    return pred


# In[243]:


text = "Google is working on self driving cars, I'm bullish on $goog"
model.eval()
model.to("cpu")
predict(text, model, vocab)


# ### Questions: What is the prediction of the model? What is the uncertainty of the prediction?
# ** TODO: Answer Question**

# In[ ]:


The prediction is positive (+1) with uncertainty of 79.78%.

The model predicts that the twit could be very positive (+2) by 19.75%.


# Now we have a trained model and we can make predictions. We can use this model to track the sentiments of various stocks by predicting the sentiments of twits as they are coming in. Now we have a stream of twits. For each of those twits, pull out the stocks mentioned in them and keep track of the sentiments. Remember that in the twits, ticker symbols are encoded with a dollar sign as the first character, all caps, and 2-4 letters, like $AAPL. Ideally, you'd want to track the sentiments of the stocks in your universe and use this as a signal in your larger model(s).
# 
# ## Testing
# ### Load the Data 

# In[ ]:


with open(os.path.join('..', '..', 'data', 'project_6_stocktwits', 'test_twits.json'), 'r') as f:
    test_data = json.load(f)


# ### Twit Stream

# In[ ]:


def twit_stream():
    for twit in test_data['data']:
        yield twit

next(twit_stream())


# Using the `prediction` function, let's apply it to a stream of twits.

# In[223]:


def score_twits(stream, model, vocab, universe):
    """ 
    Given a stream of twits and a universe of tickers, return sentiment scores for tickers in the universe.
    """
    for twit in stream:

        # Get the message text
        text = twit['message_body']
        symbols = re.findall('\$[A-Z]{2,4}', text)
        score = predict(text, model, vocab)

        for symbol in symbols:
            if symbol in universe:
                yield {'symbol': symbol, 'score': score, 'timestamp': twit['timestamp']}


# In[224]:


universe = {'$BBRY', '$AAPL', '$AMZN', '$BABA', '$YHOO', '$LQMT', '$FB', '$GOOG', '$BBBY', '$JNUG', '$SBUX', '$MU'}
score_stream = score_twits(twit_stream(), model, vocab, universe)

next(score_stream)


# That's it. You have successfully built a model for sentiment analysis! 

# ## Submission
# Now that you're done with the project, it's time to submit it. Click the submit button in the bottom right. One of our reviewers will give you feedback on your project with a pass or not passed grade. You can continue to the next section while you wait for feedback.
