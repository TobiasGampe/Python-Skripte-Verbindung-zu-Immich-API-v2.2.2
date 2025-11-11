# Immich: Skripte zur Automatisierung

Dieses Repository enthält Python-Skripte, die verschiedene Aufgaben mit der [Immich](https://immich.app/)-API automatisieren.

---

## Immich: Doppelte Videos von Google Fotos markieren

Dieses Skript (`tag_duplicate_videos.py`) löst ein spezifisches Problem für Benutzer, die ihre Fotos von Google Fotos nach Immich importiert haben.

### Das Problem

Google Fotos erstellt bei "Motion Photos" (bewegten Bildern) neben der `.jpg`-Datei oft eine zusätzliche `.MP4`-Videodatei. Beide Dateien haben denselben Basis-Dateinamen (z.B. `20230630_164222.jpg` und `20230630_164222.MP4`).

Da Immich bewegte Bilder korrekt darstellt und das Video direkt in der `.jpg`-Datei abspielen kann, ist die separate `.MP4`-Datei überflüssig und verbraucht unnötig Speicherplatz.

### Die Lösung

Das Skript `tag_duplicate_videos.py` automatisiert diesen Prozess:

1.  **Verbindung zur Immich-API:** Es stellt eine Verbindung zu Ihrer Immich-Instanz her.
2.  **Duplikate identifizieren:** Es findet Paare aus `.jpg`-Bildern und `.MP4`-Videos mit demselben Basis-Dateinamen.
3.  **Tag erstellen & zuweisen:** Es stellt sicher, dass ein Tag namens `"Duplicate Video From Google Photos"` existiert und weist ihn allen identifizierten, überflüssigen `.MP4`-Videos zu.

Nachdem das Skript gelaufen ist, können Sie in Immich nach diesem Tag filtern und die markierten Videos löschen.

### Anleitung zur Verwendung (`tag_duplicate_videos.py`)

#### Voraussetzungen

1.  **Python 3**
2.  **Requests-Bibliothek:** `pip install requests`

#### Schritt 1: Konfigurieren

Öffnen Sie `tag_duplicate_videos.py` und passen Sie die Variablen `api_key` und `api_url` am Anfang der `main`-Funktion an.

#### Schritt 2: Ausführen

Führen Sie das Skript in Ihrem Terminal aus:
```bash
python tag_duplicate_videos.py
```

---

## Immich: Massen-Upload von Dateien per Skript

Dieses Skript (`Python-File-Upload.py`) ermöglicht es, lokale Dateien einfach und automatisiert zu einer Immich-Instanz hochzuladen.

### Die Lösung

Es nutzt die Immich-API, um eine oder mehrere Dateien von Ihrem Computer hochzuladen und Metadaten wie das Erstellungs- und Änderungsdatum zu übermitteln.

### Anleitung zur Verwendung (`Python-File-Upload.py`)

#### Voraussetzungen

1.  **Python 3**
2.  **Requests-Bibliothek:** `pip install requests`

#### Schritt 1: Konfigurieren

Öffnen Sie die Datei `Python-File-Upload.py` mit einem Texteditor:

1.  Passen Sie die Variablen `API_KEY` und `BASE_URL` am Anfang der Datei an.
    ```python
    API_KEY = 'YOUR_API_KEY'
    BASE_URL = 'http://127.0.0.1:2283/api'
    ```
2.  Ändern Sie die letzte Zeile des Skripts, um den Pfad zur hochzuladenden Datei anzugeben.
    ```python
    upload(r'C:\Pfad\zu\Ihrer\Datei.jpg')
    ```
    Um mehrere Dateien hochzuladen, können Sie die `upload()`-Funktion mehrfach aufrufen oder eine Schleife implementieren.

#### Schritt 2: Ausführen

Führen Sie das Skript in Ihrem Terminal aus:
```bash
python Python-File-Upload.py
```

Das Skript lädt die angegebene Datei hoch und gibt die Antwort der Immich-API im Terminal aus.
