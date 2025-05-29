import pdfplumber
import re
import json

def clean_text(text):
    lines = text.split('\n')
    clean_lines = []
    for line in lines:
        l = line.strip()
        if not l:
            continue
        if re.match(r'\d{2}\.\d{2}\.\d{4}, \d{2}:\d{2}', l):
            continue
        if 'aniagotuje.pl' in l:
            continue
        clean_lines.append(l)
    return '\n'.join(clean_lines)

def extract_recipe_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = "".join(page.extract_text() for page in pdf.pages)
    text = clean_text(text)

    # WYCIĄGANIE TYTUŁU
    after_slogan = text.split("Tylko najlepsze przepisy")[1]
    possible_titles = [line.strip() for line in after_slogan.split('\n') if line.strip()]
    tytul = possible_titles[0]

    # WEGE opcjonalny
    dieta = None
    match_dieta = re.search(r'Dieta:\s*(wegeta[a-ząńska]*)', text, re.IGNORECASE)
    if match_dieta:
        dieta = match_dieta.group(1).lower()

    # CZAS PRZYGOTOWANIA
    match_czas = re.search(r'Czas przygotowania: ([^\n]+)', text)
    czas_przygotowania = match_czas.group(1).strip() if match_czas else None

    # SKŁADNIKI (od "Składniki" do "Ukryj zdjęcia")
    skladniki = []
    skladniki_pattern = re.compile(r'Składniki([\s\S]+?)Ukryj zdjęcia')
    match_skladniki = skladniki_pattern.search(text)
    if match_skladniki:
        for line in match_skladniki.group(1).split('\n'):
            line = line.strip('• ')
            if line and not line.startswith('Składniki'):
                skladniki.append(line)

    # WARTOŚCI ODŻYWCZE - lepsza detekcja kcal!
    wartosci_odzywcze = {}
    match_blk = re.search(r'W 100 [^\n]*\n([\s\S]{0,150})', text)
    if match_blk:
        fragment = match_blk.group(1)
        kcal = re.search(r'Wartość energetyczna\s*(\d+)\s*kcal', fragment)
        if not kcal:
            kcal = re.search(r'(\d+)\s*kcal', fragment)
        if kcal:
            wartosci_odzywcze['kalorie'] = int(kcal.group(1))

    # PRZYGOTOWANIE (od "Ukryj zdjęcia" do "Dziękuję za wspólne gotowanie.")
    przygotowanie = None
    if "Ukryj zdjęcia" in text:
        _txt = text.split("Ukryj zdjęcia", 1)[1]
        if "Dziękuję za wspólne gotowanie." in _txt:
            przygotowanie = _txt.split("Dziękuję za wspólne gotowanie.")[0].strip()
        else:
            przygotowanie = _txt.strip()
        # Zamiana enterów na spację i redukcja wielokrotnych spacji
        przygotowanie = re.sub(r'\s+', ' ', przygotowanie)

    recipe_json = {
        "tytul": tytul,
        "skladniki": skladniki,
        "czas_przygotowania": czas_przygotowania,
        "wartosci_odzywcze": wartosci_odzywcze,
        "przygotowanie": przygotowanie
    }
    if dieta:
        recipe_json["wege"] = dieta

    return recipe_json

# Przykład użycia:
json_recipe = extract_recipe_from_pdf('przepisy_pdf\Chleb rwany.pdf')
print(json.dumps(json_recipe, ensure_ascii=False, indent=2))