import math
# pip install PyMuPDF
import fitz


def distance(p1, p2):
    return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


def get_pos_of_word(rect, cur_page):
    page_y = cur_page * doc[cur_page].bound().y1
    x = rect.x0
    y = rect.y0
    # calculates a position of the middle of the word-box
    return [x + abs(rect.x0 - rect.x1) / 2,
            page_y + y + abs(rect.y0 - rect.y1) / 2]


# define your pdf here:
doc = fitz.open("Sample.pdf")

# define your search-words here:
searchWords = ["just", "Memories", "HOME"]

print("Searching...")

founds = [[] for i in range(len(searchWords))]
founds_by_word = [[] for i in range(len(searchWords))]

found_something = False
# Find all search-words
for cur in range(len(searchWords)):
    for page in range(len(doc)):
        founds[cur].append(doc[page].searchFor(searchWords[cur]))

for cur in range(len(searchWords)):
    for page in range(len(doc)):
        for word in range(len(founds[cur][page])):
            founds_by_word[cur].append([founds[cur][page][word], 0, page, searchWords[cur]])
            found_something = True

if not found_something:
    print("No search words found")
    exit()

# Calculate
# loops thought a single word
for word in range(len(founds_by_word)):
    for cur_entry in range(len(founds_by_word[word])):
        pos = get_pos_of_word(founds_by_word[word][cur_entry][0],
                              founds_by_word[word][cur_entry][2])
        # compares it to all other search words
        for compare_word in range(len(founds_by_word)):
            if compare_word != word:
                cur_best_value = math.inf
                for cur_compare_entry in range(len(founds_by_word[compare_word])):
                    compare_pos = get_pos_of_word(founds_by_word[compare_word][cur_compare_entry][0],
                                                  founds_by_word[compare_word][cur_compare_entry][2])
                    # calculates distance to given word
                    dist = distance(pos, compare_pos)
                    # checks if the current word has a shorter distance
                    if dist < cur_best_value:
                        cur_best_value = dist
                if cur_best_value != math.inf:
                    founds_by_word[word][cur_entry][1] += cur_best_value

# gets best word
lowest_page = len(doc)
lowest_y = doc[0].bound().y1
highest_page = 0
highest_y = 0
all_entries = []

for word in range(len(founds_by_word)):
    best_entry = None
    best_value = math.inf
    for cur_entry in range(len(founds_by_word[word])):
        if founds_by_word[word][cur_entry][1] < best_value:
            best_entry = founds_by_word[word][cur_entry]
            best_value = founds_by_word[word][cur_entry][1]
    if best_entry is not None:
        if lowest_page > best_entry[2]:
            lowest_page = best_entry[2]
            lowest_y = best_entry[0].y0
        elif lowest_page == best_entry[2]:
            if lowest_y > best_entry[0].y0:
                lowest_y = best_entry[0].y0
        if highest_page < best_entry[2]:
            highest_page = best_entry[2]
            highest_y = best_entry[0].y1
        elif highest_page == best_entry[2]:
            if highest_y < best_entry[0].y1:
                highest_y = best_entry[0].y1
        highlight = doc[best_entry[2]].addHighlightAnnot(best_entry[0])
        all_entries.append(best_entry)

# adds a rect around the are of words
cur_annotate_page = lowest_page
while cur_annotate_page <= highest_page:
    if cur_annotate_page == lowest_page:
        if highest_page != lowest_page:
            highlight = doc[cur_annotate_page].addRectAnnot(fitz.Rect(0,
                                                                      lowest_y,
                                                                      doc[cur_annotate_page].bound().x1,
                                                                      doc[cur_annotate_page].bound().y1))
        else:
            highlight = doc[cur_annotate_page].addRectAnnot(fitz.Rect(0,
                                                                      lowest_y,
                                                                      doc[cur_annotate_page].bound().x1,
                                                                      highest_y))
    elif cur_annotate_page == highest_page:
        highlight = doc[cur_annotate_page].addRectAnnot(fitz.Rect(0,
                                                                  0,
                                                                  doc[cur_annotate_page].bound().x1,
                                                                  highest_y))
    else:
        highlight = doc[cur_annotate_page].addRectAnnot(fitz.Rect(0,
                                                                  0,
                                                                  doc[cur_annotate_page].bound().x1,
                                                                  doc[cur_annotate_page].bound().y1))
    cur_annotate_page += 1

print("First found on page: ", lowest_page+1)
print("Last found on page: ", highest_page+1)
print("...Search ended")
doc.save("output.pdf", garbage=4, deflate=True, clean=True)
doc.close()
