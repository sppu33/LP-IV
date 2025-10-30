from functools import reduce

text ='''Once upon a time in a dense forest, a lion ruled proudly over the land. Every morning, the birds sang while the deer grazed near the river. One curious monkey loved to swing from tree to tree, teasing the sleepy tiger below. The elephant marched slowly through the woods, shaking the ground with each step. A clever fox watched everything from a distance, waiting for a chance to steal some fruit. As the sun set, the owl hooted softly, and all the animals returned to their homes. The jungle was peaceful once more, until the next adventure began.'''


words = text.split()
mapped = list(map(lambda w: (w, 1), words))
print("Mapped:", mapped)
shuffle_sort = {}
for word, count in mapped:
    if word in shuffle_sort:
        shuffle_sort[word].append(count)
    else:
        shuffle_sort[word] = [count]

print("Shuffled:", shuffle_sort)

reduced = {word: reduce(lambda a, b: a + b, counts) for word, counts in shuffle_sort.items()}

print("Word counts:", reduced)

