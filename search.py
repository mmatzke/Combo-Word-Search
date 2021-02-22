import math
import fitz


def distance(p1, p2):
    return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


def get_pos_of_word(rect, cur_page):
    page_y = cur_page * doc[page].bound().y1
    x = rect.x0
    y = rect.y0
    # calculates a position of the middle of the word-box
    return [x + abs(rect.x0 - rect.x1) / 2,
            page_y + y + abs(rect.y0 - rect.y1) / 2]


# define you pdf here:
doc = fitz.open("Sample.pdf")

# define you search-words here:
searchWords = ["house", "tree"]


print("Searching...")

founds = [[] for i in range(len(searchWords))]
founds_by_word = [[] for i in range(len(searchWords))]

# Find all search-words
for cur in range(len(searchWords)):
    for page in range(len(doc)):
        founds[cur].append(doc[page].searchFor(searchWords[cur]))

for cur in range(len(searchWords)):
    for page in range(len(doc)):
        for word in range(len(founds[cur][page])):
            founds_by_word[cur].append([founds[cur][page][word], 0, page, searchWords[cur]])

# Calculate
# loop thought a single word
for word in range(len(founds_by_word)):
    for cur_entry in range(len(founds_by_word[word])):
        pos = get_pos_of_word(founds_by_word[word][cur_entry][0],
                              founds_by_word[word][cur_entry][2])
        # compare it to all other search words
        for compare_word in range(len(founds_by_word)):
            if compare_word != word:
                cur_best_value = math.inf
                for cur_compare_entry in range(len(founds_by_word[compare_word])):
                    compare_pos = get_pos_of_word(founds_by_word[compare_word][cur_compare_entry][0],
                                                  founds_by_word[compare_word][cur_compare_entry][2])
                    # calculate distance to word
                    dist = distance(pos, compare_pos)
                    # check if better the current best distance on this search word
                    if dist < cur_best_value:
                        cur_best_value = dist
                founds_by_word[word][cur_entry][1] += cur_best_value

best_entry = None
best_value = math.inf

# get best word
for word in range(len(founds_by_word)):
    for cur_entry in range(len(founds_by_word[word])):
        if founds_by_word[word][cur_entry][1] < best_value:
            best_entry = founds_by_word[word][cur_entry]
            best_value = founds_by_word[word][cur_entry][1]

print("Found on page: ", best_entry[2])
highlight = doc[best_entry[2]].addHighlightAnnot(best_entry[0])
doc.save("output.pdf", garbage=4, deflate=True, clean=True)
doc.close()
