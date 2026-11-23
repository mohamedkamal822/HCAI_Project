
import json
from pathlib import Path

# Project paths
project_dir = Path(__file__).resolve().parent.parent
dataset_dir = project_dir / "dataset"
output_file = Path(__file__).resolve().parent / "signs.json"

existing_signs = {}
if output_file.exists():
    with output_file.open("r", encoding="utf-8") as file:
        existing_signs = json.load(file)

# Franco word: (Arabic meaning, English meaning)
translations = {
    "3amel eh": ("عامل إيه", "How are you"),
    "3ieb": ("عيب", "Shame"),
    "3rabia": ("عربية", "Car"),
    "3waz": ("عاوز", "Want"),
    "akhoia": ("أخويا", "My brother"),
    "alam": ("ألم", "Pain"),
    "bhab": ("بحب", "I love"),
    "bkrh": ("بكره", "I hate"),
    "bsor3a": ("بسرعة", "Quickly"),
    "delwaty": ("دلوقتي", "Now"),
    "docktor": ("دكتور", "Doctor"),
    "efrdha": ("افرضها", "Suppose it"),
    "ehtrem nfsk": ("احترم نفسك", "Respect yourself"),
    "elnhrda": ("النهارده", "Today"),
    "ermy wra dhrk": ("ارمي ورا ضهرك", "Forget about it"),
    "fatan": ("فتان", "Troublemaker"),
    "fe sark": ("في سرك", "In secret"),
    "flos": ("فلوس", "Money"),
    "fokk many": ("فكك مني", "Leave me alone"),
    "gomma": ("جمعة", "Friday"),
    "harmy": ("حرامي", "Thief"),
    "hba hba": ("حبة حبة", "Little by little"),
    "helw awy": ("حلو أوي", "Very nice"),
    "hta hta": ("حتة حتة", "Piece by piece"),
    "kdab": ("كداب", "Liar"),
    "khaif": ("خايف", "Afraid"),
    "khaly balk": ("خلي بالك", "Be careful"),
    "khatbty": ("خطيبتي", "My fiancée"),
    "kolya": ("كلية", "College"),
    "ktab": ("كتاب", "Book"),
    "mafish": ("مفيش", "There is none"),
    "makar": ("مكار", "Cunning"),
    "manzel": ("منزل", "House"),
    "mash mashy": ("مش ماشي", "Not working"),
    "mashy": ("ماشي", "Okay"),
    "meraty": ("مراتي", "My wife"),
    "mohands": ("مهندس", "Engineer"),
    "moshwash": ("مشوش", "Confused"),
    "msh 3waz": ("مش عاوز", "Don't want"),
    "oda": ("أوضة", "Room"),
    "sabhl elkheer": ("صباح الخير", "Good morning"),
    "sabhlala": ("سبهللة", "Carelessly"),
    "sadak": ("صدق", "Truth"),
    "sahby": ("صاحبي", "My friend"),
    "sbak": ("سباك", "Plumber"),
    "shar3": ("شارع", "Street"),
    "shbak": ("شباك", "Window"),
    "t3ban": ("تعبان", "Tired"),
    "tmam": ("تمام", "Fine"),
    "whashny": ("وحشني", "I miss him"),
    "whda whda": ("واحدة واحدة", "Slowly"),
    "y7takr": ("يحتقر", "Despise"),
    "yabky": ("يبكي", "Cry"),
    "yadhk": ("يضحك", "Laugh"),
    "yallhwy": ("يا لهوي", "Oh my goodness"),
    "yshtm": ("يشتم", "Insult"),
}

signs = {}

if not dataset_dir.exists():
    raise FileNotFoundError(
        f"Dataset folder not found: {dataset_dir}"
    )

for word_folder in sorted(dataset_dir.iterdir()):

    if not word_folder.is_dir():
        continue

    word = word_folder.name

    if word not in translations:
        print(f"Warning: No translation found for {word}")
        continue

    videos = [
        file for file in word_folder.iterdir()
        if file.is_file() and file.suffix.lower() == ".mp4"
    ]

    if len(videos) != 1:
        print(f"Warning: {word} has {len(videos)} videos. Skipped.")
        continue

    arabic, english = translations[word]
    video = videos[0]
    existing = existing_signs.get(word, {})

    signs[word] = {
        "id": word,
        "franco": word,
        "arabic": arabic,
        "english": english,
        "aliases": existing.get("aliases", []),
        "relations": existing.get("relations", []),
        "relation_notes": existing.get("relation_notes", {}),
        "video": video.relative_to(project_dir).as_posix()
    }

# Save the index
with open(output_file, "w", encoding="utf-8") as file:
    json.dump(signs, file, ensure_ascii=False, indent=4)

print("\nJSON Index created successfully!")
print("Total indexed words:", len(signs))
print("Expected words:", len(translations))
print("Output file:", output_file)
