import pdfplumber
import re
import json

def extract_recipe_from_pdf(pdf_path):
    # Odczytaj cały tekst z PDF
    with pdfplumber.open(pdf_path) as pdf:
        text = "".join(page.extract_text() for page in pdf.pages)

    # KATEGORIE do wyciągnięcia:
    # 1. tytuł (pierwsza linia po autorze)
    # 2. czas przygotowania
    # 3. składniki
    # 4. przygotowanie (całość kroków)
    # 5. wartości odżywcze
    # 6. pochodzenie_dania (tutaj możemy wpisać np. "brak danych")

    # Tytuł
    match_title = re.search(r'Zupa z łososia', text)
    tytul = match_title.group(0) if match_title else None

    # Czas przygotowania
    match_czas = re.search(r'Czas przygotowania: ([^\n]+)', text)
    czas_przygotowania = match_czas.group(1).strip() if match_czas else None

    # Składniki (od słowa "Składniki" do pierwszego "Krok ")
    match_skladniki = re.search(r'Składniki(.+?)Krok 1:', text, re.DOTALL)
    skladniki = []
    if match_skladniki:
        for line in match_skladniki.group(1).split('\n'):
            line = line.strip('• ')
            if line and not line.startswith('Zupa z łososia'):
                skladniki.append(line)

    # Wartości odżywcze (w 100 ml)
    match_wartosci = re.search(r'W 100 ml zupy:[^0-9]*([\s\S]+?)Składniki', text)
    wartosci_odzywcze = {}
    if match_wartosci:
        for line in match_wartosci.group(1).split('\n'):
            if ':' in line or not line.strip():
                continue
            line = line.strip()
            if 'kcal' in line: 
                wartosci_odzywcze['kalorie'] = re.search(r'(\d+)\s?kcal', line).group(1)
            elif 'Węglowodany' in line:
                wartosci_odzywcze['weglowodany'] = re.search(r'(\d+\s?g)', line).group(1)
            elif 'cukry' in line:
                wartosci_odzywcze['cukry'] = re.search(r'(\d+\s?g)', line).group(1)
            elif 'Białko' in line:
                wartosci_odzywcze['bialko'] = re.search(r'(\d+\s?g)', line).group(1)
            elif 'Tłuszcze' in line:
                wartosci_odzywcze['tluszcze'] = re.search(r'(\d+\s?g)', line).group(1)

    # Przygotowanie (wszystkie kroki)
    match_kroki = re.search(r'Krok 1:(.+)Dziękuję za wspólne gotowanie.', text, re.DOTALL)
    przygotowanie = match_kroki.group(1).strip() if match_kroki else None

    # Pochodzenie dania - BRAK, można dodać jako None lub "Polska" (przykład)
    pochodzenie_dania = None

    recipe_json = {
        "tytul": tytul,
        "skladniki": skladniki,
        "czas_przygotowania": czas_przygotowania,
        "pochodzenie_dania": pochodzenie_dania,
        "wartosci_odzywcze": wartosci_odzywcze,
        "przygotowanie": przygotowanie
    }

    return recipe_json

# Zastosowanie:
json_recipe = extract_recipe_from_pdf('Zupa_z_bobu.pdf')
print(json.dumps(json_recipe, ensure_ascii=False, indent=2))