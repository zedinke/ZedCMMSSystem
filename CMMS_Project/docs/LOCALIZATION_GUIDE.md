# Lokalizációs Útmutató

## Áttekintés

A CMMS rendszer teljes lokalizációt támogat magyar és angol nyelven. Minden felhasználó által látható szöveg lokalizált, beleértve az UI elemeket, hibaüzeneteket, és API válaszokat.

## Lokalizációs Rendszer

### Translation Fájlok

A fordításkulcsok JSON formátumban tárolódnak:
- `localization/translations/hu.json` - Magyar fordítások
- `localization/translations/en.json` - Angol fordítások

### Translation Kulcsok Struktúrája

```json
{
  "common": {
    "buttons": { ... },
    "messages": { ... }
  },
  "errors": {
    "user_not_found": "...",
    "validation": { ... }
  },
  "messages": {
    "user_created": "..."
  },
  "worksheets": { ... },
  "assets": { ... }
}
```

## Használat

### UI Rétegben (Flet)

```python
from localization.translator import translator

# Egyszerű szöveg
ft.Text(translator.get_text("worksheets.title"))

# Paraméterekkel
translator.get_text("users.greeting", name="John")

# Gombok
ft.ElevatedButton(translator.get_text("common.buttons.save"))
```

### Services Rétegben

```python
from utils.localization_helper import get_localized_error, get_localized_message

# Hibaüzenet
raise UserServiceError(get_localized_error("user_not_found"))

# Sikeres üzenet
logger.info(get_localized_message("user_created"))
```

### API Rétegben

```python
from api.dependencies import get_user_language
from utils.localization_helper import get_localized_error

async def my_endpoint(
    lang_code: str = Depends(get_user_language)
):
    raise HTTPException(
        status_code=404,
        detail=get_localized_error("user_not_found", lang_code=lang_code)
    )
```

## Új Szövegek Hozzáadása

1. **Hozzáadás a translation fájlokhoz:**
   - `hu.json` - Magyar fordítás
   - `en.json` - Angol fordítás

2. **Használat a kódban:**
   ```python
   translator.get_text("my.new.key")
   ```

3. **Paraméterek:**
   ```json
   {
     "greeting": "Üdvözöljük, {name}!"
   }
   ```
   ```python
   translator.get_text("greeting", name="John")
   ```

## Best Practices

1. **Ne használj hardcode szövegeket** - Mindig használd a translator-t
2. **Konzisztens kulcsnevek** - Használj logikus hierarchiát (pl. `worksheets.title`)
3. **Paraméterek** - Használj paramétereket dinamikus tartalomhoz
4. **Hibaüzenetek** - Mindig lokalizáld a hibaüzeneteket
5. **Tesztelés** - Teszteld mindkét nyelven

## Hardcode Detektálás

Futtasd a hardcode detektáló scriptet:

```bash
python scripts/check_hardcoded_strings.py
```

Ez a script az összes potenciális hardcode szöveget megtalálja.

