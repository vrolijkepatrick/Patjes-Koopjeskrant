# Patjes Koopjeskrant — eerste proefversie

**Inbegrepen**: mobielvriendelijke digitale koopjeskrant, zoeken, winkelfilters, favorieten op hetzelfde apparaat, sorteervolgorde, 25%-ondergrens, gekoppelde bronvermelding, data-update script en een geplande workflow (zondag en woensdag).

**Vier live-bronnen zodra de update werkt**: Albert Heijn, Hoogvliet, Jumbo, Aldi via de gratis publieke API van PrijsProfeet. **Nog niet aangesloten**: Action, Kruidvat, Trekpleister. Dit is geen volledige zeven-winkels-versie.

## Installeren met GitHub Desktop

1. Pak de zip uit.
2. Maak via GitHub Desktop een nieuwe repository **Patjes-Koopjeskrant** met de uitgepakte map als lokale map (of zet de bestanden in een bestaande nieuwe repo). Publiceer **Public** naar GitHub.
3. Ga op github.com naar de repo > **Actions** > workflow **Vernieuw aanbiedingen** > **Run workflow**. Als het ophalen lukt verschijnt in `data/aanbiedingen.json` een gevulde lijst. Bij falen blijven de bestaande gegevens behouden. Controleer de Actions-logs; het API-formaat is op dit moment nog niet live vanuit deze omgeving getest.
4. Ga naar repo > **Settings > Pages** > Deploy from a branch > `main` en `/ (root)` > Save.
5. Je site verschijnt normaal op `https://<gebruikersnaam>.github.io/Patjes-Koopjeskrant/` (na succesvolle publicatie). De geplande workflow probeert zondag en woensdag te verversen. GitHub kan geplande taken vertragen.

## Lokaal testen

Open de map in de terminal en voer uit: `python -m http.server 8000`, ga dan naar `http://localhost:8000`. Met `python update.py` probeer je de live data handmatig op te halen (internet nodig). Rechtstreeks dubbelklikken op index.html laadt het JSON-bestand doorgaans niet.

## Betrouwbaarheid

- Bij fouten in de API stopt de update zonder het bestaande bestand te vervangen. De website toont altijd de laatst geladen update en waarschuwt bij ontbrekende data.
- Datum-/statusfilters weren toekomstige en verlopen aanbiedingen zodra die velden beschikbaar zijn. De API kan `valid_until_estimated` bevatten: dit wordt gemeld.
- Prijzen afkomstig van PrijsProfeet zijn niet door de winkel bevestigd; actuele kassa-/winkelprijzen kunnen afwijken.
- Sommige acties vereisen meer stuks of een pas: controleer de voorwaarden. Dit script toont nog niet alle varianten van dergelijke mechanieken nauwkeurig; voor verantwoord gebruik moet dit in de volgende test worden aangescherpt.
- Favorieten worden alleen per browser/device in localStorage opgeslagen (geen sync tussen iPhone en laptop).
- De gratis API heeft geen generieke cross-retailer schapprijsvergelijking. Die functie is **nog niet** gebouwd.
- Als de API response verandert of extra paginering gebruikt, kan `update.py` aanpassing vragen. **API-ophalen en end-to-end-publicatie zijn nog niet getest**.

Bron: https://github.com/PrijsProfeet/supermarkt-api/blob/main/README.md en https://www.prijsprofeet.nl/api-voorwaarden
