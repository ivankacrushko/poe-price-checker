import requests
import json
import parse_item as pi
import modifiers_fetch as mf

# Funkcja wyszukująca przedmioty
def search_items(league, item_type, rarity=None, quality_min=None, level_min=None, mods=None):
    # URL do wyszukiwania
    url = f"https://www.pathofexile.com/api/trade2/search/{league}"
    
    # Parametry wyszukiwania
    query = {
        "query": {
            "status": {"option": "online"},
            'type': item_type,
            'stats': [{
                'type': 'and',
                'filters': []
            }],
            'filters':{                
                #'weapon_filters': {'filters':{}},
                #'armour_filters': {'filters':{}},
                #'socket_filters': {'filters':{}},
                'req_filters':{'filters': {}},
                'misc_filters':{'filters': {}},
                'type_filters': {'filters': {}},
            }
        },
        "sort": {"price": "asc"}
    }

    if rarity:
        query["query"]["filters"]["type_filters"]['filters']["rarity"] = {"option": rarity}

    # Dodajemy minimalną jakość, jeśli jest podana
    if quality_min:
        query["query"]["filters"]["misc_filters"]['filters']["quality"] = {"min": quality_min}

    # Dodajemy minimalny poziom, jeśli jest podany
    if level_min:
        query["query"]["filters"]["misc_filters"]['filters']["ilvl"] = {"min": level_min}

    if mods:
        for mod in mods:
            for section in query['query']['stats']:
                section['filters'].append(mod)
                break

    

    
    # Wysłanie zapytania POST
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36"
    }

    print(json.dumps(query, indent=2))
    response = requests.post(url, headers=headers, json=query)
    
    if response.status_code == 200:
        data = response.json()
        return data["id"], data["result"]
    else:
        print("Błąd wyszukiwania:", response.status_code, response.text)
        return None, None

# Funkcja pobierająca szczegóły przedmiotów
def fetch_item_details(search_id, item_ids):
    # Pobieramy szczegóły dla maksymalnie 10 ID na raz (ograniczenie API)
    ids_to_fetch = ",".join(item_ids[:1])  # Można rozszerzyć obsługę większej liczby wyników
    url = f"https://www.pathofexile.com/api/trade2/fetch/{ids_to_fetch}?query={search_id}"
    
    # Wysłanie zapytania GET
    response = requests.get(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36"
    })
    
    # Logowanie odpowiedzi API dla debugowania
    print("Odpowiedź API fetch:", response.json())
    
    if response.status_code == 200:
        data = response.json()
        return data.get("result", [])
    else:
        print("Błąd pobierania szczegółów:", response.status_code, response.text)
        return []
    
def display_item_details(item):
    item_info = item.get("item", {})
    price_info = item.get("listing", {}).get("price", {})
    seller_info = item.get("listing", {}).get("account", {})
    
    item_name = item_info.get("name", "Nieznana nazwa przedmiotu")
    item_type_line = item_info.get("typeLine", "Nieznany typ")
    item_rarity = item_info.get("rarity", "Nieznana rzadkość")
    item_level = item_info.get("ilvl", "Nieznany poziom")
    item_id = item_info.get("id", "Brak ID")
    
    # Cena
    price_amount = price_info.get("amount", "Brak ceny")
    price_currency = price_info.get("currency", "Brak waluty")
    
    # Sprzedawca
    seller_name = seller_info.get("name", "Nieznany sprzedawca")
    
    # Umiejętności i mody
    granted_skills = item_info.get("grantedSkills", [])
    explicit_mods = item_info.get("explicitMods", [])
    
    # Flavour text
    flavour_text = item_info.get("flavourText", [])

    quality = None
    if "properties" in item_info:
        for prop in item_info["properties"]:
            #print(f'PROP:{prop}')
            if prop.get("name") == "[Quality]":
                
                quality = prop.get("values", [])[0][0]
    
    # Wyświetlanie szczegółowych informacji
    print(f"- {item_name} ({item_type_line})")
    print(f"  Rzadkość: {item_rarity}")
    print(f"  Poziom: {item_level}")
    print(f"  Quality: {quality}")
    print(f"  ID przedmiotu: {item_id}")
    print(f"  Cena: {price_amount} {price_currency}")
    print(f"  Sprzedawca: {seller_name}")
    
    print("\n  Umiejętności przyznawane przez przedmiot:")
    for skill in granted_skills:
        print(f"    - {skill.get('name', 'Brak nazwy umiejętności')}")
    
    print("\n  Modyfikacje przedmiotu:")
    for mod in explicit_mods:
        print(f"    - {mod}")
    
    if flavour_text:
        print("\n  Tekst fabularny:")
        for line in flavour_text:
            print(f"    {line}")

# Główna funkcja programu
def main():
    # Parametry wyszukiwania
    league = "Standard"  # Nazwa ligi
    # item_type = "Intricate Gloves"  # Typ przedmiotu
    # item_rarity = 'rare'
    # item_quality = 20
    # item_level = 34
    # item_mods = {
    #     '+38 to maximum Energy Shield',
    #     '+110 to Accuracy Rating',
    #     '+54 to maximum Mana',
    #     '+13% to Cold Resistance',
    #     '+12% to Lightning Resistance',
    #     'Gain 4 Life per Enemy Hit with Attacks'
    # }

    item_text = input("Podaj przedmiot")
    item_details, item_mods = pi.parse_item_details(item_text)
    print(item_details)

    mods = mf.query_set(item_mods)


    
    
    #print(f"Wyszukiwanie przedmiotu: {item_name} ({item_type}) w lidze {league}...")
    
    # Krok 1: Wyszukiwanie przedmiotów
    search_id, item_ids = search_items(league, item_details['item_type'], item_details['rarity'],
                                       item_details['quality'], item_details['ilvl'], mods)
    
    if not search_id or not item_ids:
        print("Brak wyników wyszukiwania.")
        return
    
    #print(f"Znaleziono {len(item_ids)} wyników. Pobieram szczegóły dla pierwszych 10...")
    
    # Krok 2: Pobieranie szczegółów przedmiotów
    details = fetch_item_details(search_id, item_ids)
    
    if not details:
        print("Nie udało się pobrać szczegółów przedmiotów.")
        return
    
    # Wyświetlanie wyników
    print("\nPrzedmioty znalezione:")
    for item in details:
        display_item_details(item)
        

# Uruchomienie programu
if __name__ == "__main__":
    main()
    item_text = """
    Item Class: Gloves
    Rarity: Rare
    Corruption Hold
    Intricate Gloves
    --------
    Quality: +14% (augmented)
    Energy Shield: 73 (augmented)
    --------
    Requirements:
    Level: 33
    Int: 53
    --------
    Sockets: S 
    --------
    Item Level: 34
    --------
    +12% to Lightning Resistance (rune)
    +38 to maximum Energy Shield
    +110 to Accuracy Rating
    +54 to maximum Mana
    +13% to Cold Resistance
    +12% to Lightning Resistance
    Gain 4 Life per Enemy Hit with Attacks
    """

    # Parsowanie i wypisanie danych
    # item_details, item_mods = pi.parse_item_details(item_text)
    # print(item_details)
