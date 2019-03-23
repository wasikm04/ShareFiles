# ShareFiles

## 1.Opis

Aplikacja została stworzona w ramach przedmiotu Programowanie Aplikacji
Mobilnych i Webowych prowadzonego na Informatyce Stosowanej na Politechnice Warszawskiej. 

Aplikacja zbudowana jest z kilku serwerów mających za zadanie współpracować ze sobą w celu umożliwienia użytkownikowi przechowywania kilku plików i udostępniania innym.

## 2.Budowa

- Serwer aplikacji __webapp.py__
- Serwer plików __dl.py__ 
Obia serwery zostały napisane w Pythonie z wykorzystaniem Flask, do zabezpieczenia komunikacji wykorzystują tokeny JWT. Sesje użytkowników są przechowywane w bazie __Redis__. Dostęp do aplikacji uzyskuje się poprzez logowanie, można zamiast tego uruchomić serwer __webapp_auth0.py__ który pozwala na pobranie danych od innych dostawców usług wykorzystując standard OAuth.

- Serwer tworzący ikony plików __receiver.py__ wykorzystujący klient Pika do pobierania zadań zakolejkowanych przez serwer plików w __RabbitMQ__. Jego zadaniem jest pobieranie dodanych plików graficznych w celu utworzenia na ich podstawie ikon o rozmiarze 64x64.

- Serwer Server-Sent Events __sse.js__ napisany w __node.js__ z wykorzystaniem Express. Jego celem jest odbieranie od serwera plików sygnałów o dodaniu nowego pliku i wysłaniu powiadomienia o tym do nasłuchujących aplikacji odpowiedniego użytownika.

## 3.Wymagania
- Nginx(dostępne pliki .ini dla webapp i dl)/ Apache z mod_wsgi
- Zainstalowany i uruchomiony serwer Redis z zainicjowanymi użytkownikami za pomocą skryptu __redis_init.py__
- Import Express
- Importy Flask, Jinja2, werkzeug, Pika, jwt, redis, authlib.flask.client

## 4. Przykładowe widoki aplikacji
<img src="https://github.com/wasikm04/ShareFiles/blob/master/Images/pi5.png" width="800"/>
<img src="https://github.com/wasikm04/ShareFiles/blob/master/Images/pi1.png" width="800"/>
<img src="https://github.com/wasikm04/ShareFiles/blob/master/Images/pi2.png" width="800"/>
<img src="https://github.com/wasikm04/ShareFiles/blob/master/Images/pi4.png" width="800"/>
<img src="https://github.com/wasikm04/ShareFiles/blob/master/Images/pi6.png" width="500"/>
