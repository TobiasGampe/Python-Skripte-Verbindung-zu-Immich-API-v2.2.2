# Immich: Doppelte Videos von Google Fotos markieren

Dieses Repository enthält ein Python-Skript, das ein spezifisches Problem für Benutzer löst, die ihre Fotos von Google Fotos nach Immich importiert haben.

## Das Problem

Google Fotos erstellt bei "Motion Photos" (bewegten Bildern) neben der `.jpg`-Datei oft eine zusätzliche `.MP4`-Videodatei. Beide Dateien haben denselben Basis-Dateinamen (z.B. `20230630_164222.jpg` und `20230630_164222.MP4`).

Da Immich bewegte Bilder korrekt darstellt und das Video direkt in der `.jpg`-Datei abspielen kann, ist die separate `.MP4`-Datei überflüssig und verbraucht unnötig Speicherplatz. Diese doppelten Videos manuell zu finden und zu löschen, kann bei Tausenden von Fotos sehr aufwendig sein.

## Die Lösung

Das Python-Skript `tag_duplicate_videos.py` automatisiert diesen Prozess:

1.  **Verbindung zur Immich-API:** Das Skript stellt eine Verbindung zu Ihrer Immich-Instanz her.
2.  **Alle Medien abrufen:** Es ruft eine Liste all Ihrer Fotos und Videos ab.
3.  **Duplikate identifizieren:** Es durchsucht die Liste und findet Paare aus `.jpg`-Bildern und `.MP4`-Videos, die denselben Basis-Dateinamen haben.
4.  **Tag erstellen & zuweisen:** Das Skript stellt sicher, dass ein Tag namens `"Duplicate Video From Google Photos"` in Immich existiert (und erstellt es, falls nicht vorhanden). Anschließend wird dieser Tag allen identifizierten, überflüssigen `.MP4`-Videos zugewiesen.

Nachdem das Skript gelaufen ist, können Sie in der Immich-Oberfläche einfach nach diesem Tag filtern, alle markierten Videos auswählen und sie sicher löschen.

## Anleitung zur Verwendung

### Voraussetzungen

1.  **Python 3:** Stellen Sie sicher, dass Python auf Ihrem System installiert ist.
2.  **Requests-Bibliothek:** Sie benötigen die `requests`-Bibliothek für Python. Installieren Sie sie mit dem folgenden Befehl in Ihrem Terminal:
    ```bash
    pip install requests
    ```

### Schritt 1: Skript herunterladen

Laden Sie das Skript `tag_duplicate_videos.py` aus diesem Repository herunter und speichern Sie es an einem Ort Ihrer Wahl.

### Schritt 2: Skript konfigurieren

Öffnen Sie die Datei `tag_duplicate_videos.py` mit einem Texteditor. Sie müssen zwei Zeilen am Anfang der `main`-Funktion (ca. Zeile 140) anpassen:

```python
def main():
    # --- BITTE HIER IHRE DATEN EINTRAGEN ---
    # Tragen Sie hier Ihren Immich API-Schlüssel in Anführungszeichen ein.
    api_key = "IHR_API_SCHLÜSSEL_HIER_EINFÜGEN"

    # Tragen Sie hier die vollständige URL zu Ihrer Immich API ein.
    # WICHTIG: Die URL muss auf "/api" enden.
    api_url = "http://IHRE_IP_ADRESSE:2283/api"
    # -----------------------------------------
```

1.  Ersetzen Sie `"IHR_API_SCHLÜSSEL_HIER_EINFÜGEN"` durch Ihren echten Immich-API-Schlüssel.
2.  Ersetzen Sie `"http://IHRE_IP_ADRESSE:2283/api"` durch die korrekte URL Ihrer Immich-Instanz. Achten Sie darauf, dass die Adresse mit `/api` endet.

Speichern Sie die Änderungen in der Datei.

### Schritt 3: Skript ausführen

1.  Öffnen Sie ein Terminal oder eine Eingabeaufforderung.
2.  Navigieren Sie in das Verzeichnis, in dem Sie die `tag_duplicate_videos.py`-Datei gespeichert haben.
3.  Führen Sie das Skript mit dem folgenden Befehl aus:
    ```bash
    python tag_duplicate_videos.py
    ```

Das Skript wird nun gestartet. Es informiert Sie im Terminal über seinen Fortschritt, z.B. wie viele Assets es abruft und wie viele doppelte Videos es zum Markieren gefunden hat. Nach Abschluss des Vorgangs können Sie die markierten Videos in Immich überprüfen und löschen.
