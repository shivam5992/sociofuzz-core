from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import re, string

lmtzr = WordNetLemmatizer()
exclude = string.punctuation
# stopwords = stopwords.words('english')

stopwords = open("utility/stopwordlist.txt").read().strip().split("\n")

def punctuation_free(text):
  text = "".join([x for x in text if x not in exclude])
  return text


def stopword_free(text):
  puncfree = punctuation_free(text)
  puncFree_words = puncfree.split()
  stopfree = [x for x in puncFree_words if x.lower() not in stopwords]
  stopfree_text = " ".join(stopfree)
  return stopfree_text


def generate_ngrams(inp, n=2, islist=False):
  if not islist:
    inp = inp.split()
  output = []
  for i in range(len(inp)-n+1):
    ngram = " ".join(inp[i:i+n])
    output.append(ngram)
  return output


def lemmatize_word(word):
  wrd = lmtzr.lemmatize(word, 'v')
  if wrd == word:
    wrd = lmtzr.lemmatize(word, 'n')
  return wrd


def lemmatize_sentence(text):
  words = text.split()
  lemmed = []
  for wrd in words:
    wrd = punctuation_free(wrd)
    lem_words = lemmatize_word(wrd)
    lemmed.append(lem_words)
  lem_text = " ".join(lemmed)
  return lem_text



def digit_free(text):
	text_list = text.split()
	text_list = [x for x in text_list if not x.isdigit()]
	text = " ".join(text_list)
	return text


def url_free(text):
	text_list = text.split()
	text_list = [x for x in text_list if not x.startswith("http")]
	text = " ".join(text_list)
	return text

def mention_free(text):
  text_list = text.split()
  text_list = [x for x in text_list if not x.startswith("@")]
  text = " ".join(text_list)
  return text


def splitAttached(text):
  reconstructedWord = []
  for word in text.split():
    if not word.isupper():
      lis = re.findall('[^ ][^A-Z]*', word)
      if len(lis) == 1 or lis[0].islower():
        reconstructedWord.append(word)
      else:
        separateWordReconstruction = ''
        for separateWord in lis:
          # Handling the case of #ItsBMW  # Capital words together
          if(len(separateWord)==1):
            separateWordReconstruction = separateWordReconstruction + separateWord
          else:
            separateWordReconstruction = separateWordReconstruction + " " + separateWord.lower() + " "
        reconstructedWord.append(separateWordReconstruction)
    else:
      reconstructedWord.append(word)

  stringToBeReturned = " ".join(reconstructedWord)
  return ' '.join(stringToBeReturned.split())



