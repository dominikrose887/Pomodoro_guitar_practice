# 🎸 Pomodoro Guitar Practice

Gitár gyakorló alkalmazás Pomodoro időzítővel, BPM és sebesség követéssel.

## Leírás

Ez az alkalmazás segít a hatékony gitárgyakorlásban. A Pomodoro technikát alkalmazza:
**20 perc gyakorlás**, majd **10 perc szünet**, ismétlődő ciklusokban.

A program nyomon követi a tempót, és szabályozott módon engedi az emelést:
csak akkor emelheted a tempót, ha legalább **3-szor hibátlanul** eljátszottad az adott lick-et.
Ha hibázol, a számláló nullázódik, és újra kell kezdened.

### Két mód

- **BPM mód**: klasszikus BPM beállítás (pl. 60, 80, 120 BPM)
- **Sebesség mód**: Reaper-stílusú sebesség szorzó (pl. 0.30x, 0.50x, 1.00x)

### Világos / Sötét téma

Az alkalmazás két színtémával rendelkezik, amelyek között bármikor válthatunk:

- **Világos mód**: meleg krém háttér, zsálya-zöld akcentusok (`#FAF9EE`, `#A2AF9B`, `#DCCFC0`, `#EEEEEE`)
- **Sötét mód**: mély kékesszürke háttér, arany akcentusok (`#537188`, `#CBB279`, `#E1D4BB`, `#EEEEEE`)

Témaváltás: `D` billentyű vagy a `🌙 Sötét / ☀ Világos` gombbal.

## Funkciók

- **Pomodoro időzítő**: 20 perc gyakorlás / 10 perc szünet ciklusok
- **Két mód**: BPM mód és Sebesség mód (Reaper-hez)
- **BPM kezelés**: aktuális BPM beállítása és követése (20–300)
- **Sebesség kezelés**: Reaper-stílusú szorzó (0.05x – 2.00x)
- **Hibátlan játék számláló**: sikeres lejátszások számlálása (● ○ ○ vizuális jelzés)
- **Automatikus tempó emelés**: 3 hibátlan lejátszás után emelhető
- **Hiba reset**: hibás lejátszásnál a számláló nullázódik
- **Szünet / Folytatás**: időzítő szüneteltetése és folytatása
- **Progress bar**: vizuális előrehaladás jelző
- **Session statisztikák**: hibátlan / hiba / befejezett ciklusok száma
- **Always on top**: ablak mindig felül tartása
- **Világos / Sötét téma**: két szép színtéma váltása
- **Hangjelzés**: értesítő hang a gyakorlás/szünet váltásnál
- **GUI felület**: modern, kártya-alapú grafikus felület (tkinter)

## Billentyűparancsok

| Billentyű | Funkció                          |
|-----------|----------------------------------|
| `Space`   | Indítás / Szünet / Folytatás     |
| `S`       | Leállítás (reset)                |
| `N`       | Átugrás (következő fázis)        |
| `H` / `1` | Hibátlan lejátszás               |
| `E` / `2` | Hibás lejátszás                  |
| `U` / `3` | Tempó emelés                     |
| `T`       | Always on top ki/be              |
| `D`       | Világos / Sötét téma váltás      |

## Követelmények

- Python 3.14.3
- Csak standard könyvtárak (tkinter – a Python része)

## Telepítés

Nincs szükség külön telepítésre, a program kizárólag a Python standard könyvtárait használja.

```bash
git clone <repo-url>
cd Pomodoro_guitar_practice
```

## Használat

```bash
python main.py
```

### Kezelés

1. **Mód választás**: Válaszd ki a BPM módot vagy Sebesség módot (Reaper)
2. **Tempó beállítása**: Írd be a kívánt kezdő értéket (BPM: pl. 60 | Speed: pl. 0.30)
3. **Gyakorlás indítása**: Kattints az "▶ Indítás" gombra – elindul a 20 perces időzítő
4. **Sikeres lejátszás**: Kattints a "✅ Hibátlan" gombra, ha hiba nélkül eljátszottad a lick-et
5. **Hibás lejátszás**: Kattints a "❌ Hiba" gombra, ha elrontottad – a számláló nullázódik
6. **Tempó emelés**: 3 hibátlan lejátszás után aktívvá válik a "⬆ Emelés" gomb
7. **Szünet/Gyakorlás váltás**: A program automatikusan jelez, amikor lejár a 20 perc (gyakorlás) vagy a 10 perc (szünet)
8. **Témaváltás**: A `D` billentyűvel vagy a `🌙 Sötét` gombbal válthatsz a világos és sötét téma között

### Munkafolyamat

```
Gyakorlás (20 perc)
  │
  ├─ Lick lejátszása adott BPM-en / sebességen
  │   ├─ Hibátlan? → számláló +1 (●○○ → ●●○ → ●●●)
  │   └─ Hibás?    → számláló = 0 (○○○)
  │
  ├─ Ha számláló ≥ 3 → Tempó emelhető (BPM +5 vagy Speed +0.05x)
  │
  └─ 20 perc letelt → SZÜNET értesítés
        │
        Szünet (10 perc)
        │
        └─ 10 perc letelt → GYAKORLÁS értesítés
              │
              └─ Új ciklus kezdődik
```

## EXE készítés

Az alkalmazás egyetlen `.exe` fájllá alakítható a mellékelt build script segítségével:

```bash
pip install pyinstaller pillow
python build.py
```

Az EXE a `dist/` mappában jelenik meg egyedi ikonnal.

## Projekt struktúra

```
Pomodoro_guitar_practice/
├── README.md          # Dokumentáció
├── main.py            # Fő alkalmazás (GUI + logika)
├── create_icon.py     # Ikon generáló script
└── build.py           # EXE builder script (PyInstaller)
```

## Licenc

MIT

---

**By DominikRose** · v1.0.0
