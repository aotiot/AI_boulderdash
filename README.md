Tässä on kattava `README.md` -tiedosto pelillesi. Voit tallentaa tämän tekstin samaan kansioon pelin kanssa nimellä `README.md`.

---

# Boulder Dash - Python Edition

Tämä on Pythonilla ja Pygame-kirjastolla toteutettu modernisoitu kunnianosoitus klassiselle Commodore 64:n Boulder Dash -pelille. Pelissä yhdistyvät retro-henkinen pulmanratkaisu ja toiminta, mutta siihen on tuotu moderneja mausteita, kuten dynaaminen valaistus, partikkeliefektit, ruudun tärinä sekä ohjelmallisesti generoidut ääniefektit.

## 🌟 Ominaisuudet

* **12 tasoa kiihtyvällä vaikeusasteella:**
* Tasot 1–3: Turvallinen ympäristö pelimekaniikkojen opetteluun.
* Tasot 4–6: Yksinkertaiset, edestakaisin liikkuvat violetit viholliset.
* Tasot 7–12: Älykkäät, seiniä seuraavat punaiset viholliset.


* **Fysiikkamoottori:** Kivet putoavat painovoiman mukaisesti ja vierivät toistensa päältä. Kiviä voi myös työntää sivusuunnassa tyhjään tilaan.
* **Dynaaminen valaistus:** Pelaajan otsalamppu valaisee pimeää kaivosta, ja timantit sekä ovi hohtavat pimeässä.
* **Ohjelmalliset äänet (Syntetisaattori):** Peli ei vaadi erillisiä `.wav` tai `.mp3` -äänitiedostoja. Kaikki äänet generoidaan lennosta puhtaan matematiikan avulla!
* **Visuaaliset efektit:** Partikkelit mullan kaivamisessa ja räjähdyksissä, sekä ruudun tärinä (screen shake) raskaiden kivien iskeytyessä maahan.

---

## 🛠️ Asennus ja käynnistys

### Vaatimukset

* **Python 3.x** asennettuna (suositus: 3.8 tai uudempi)
* **Pygame**-kirjasto

### Ohjeet

1. Varmista, että Python on asennettu. Voit ladata sen osoitteesta [python.org](https://www.python.org/).
2. Asenna Pygame-kirjasto avaamalla komentorivi (Terminal / Command Prompt) ja syöttämällä:
```bash
pip install pygame

```


3. Tallenna pelin koodi tiedostoon, esim. nimellä `boulder.py`.
4. Käynnistä peli komentoriviltä komennolla:
```bash
python boulder.py

```



---

## 🎮 Pelaaminen

### Tavoite

Jokaisen tason tavoitteena on löytää **keltainen avain** ja paeta sen jälkeen avautuvasta **ovesta** seuraavalle tasolle jäämättä kivien alle tai osumatta vihollisiin.

### Ohjaus

* **Nuolinäppäimet (Ylös, Alas, Vasen, Oikea):** Liikuta hahmoa ja kaiva multaa.
* Kiviä voi työntää kulkemalla niitä päin joko vasemmalta tai oikealta, *mikäli kiven takana on tyhjä tila*. Työntäminen onnistuu myös silloin, jos kiven takana on vihollinen (vihollinen murskaantuu).

### Pelin elementit

* **Pelaaja (Kaivosmies):** Sinä! Varustettu otsalampulla ja keltaisella kypärällä.
* **Multa:** Voit kaivaa tiesi mullan läpi.
* **Kivet:** Putoavat tyhjään tilaan. Varo, etteivät ne putoa päällesi! Kiviä voi työntää sivuille.
* **Timantit:** Kerää näitä saadaksesi pisteitä.
* **Avain:** Tarvitaan tason läpäisyyn.
* **Ovi:** Lukittuna punainen. Muuttuu vihreäksi ja hohtavaksi, kun olet kerännyt avaimen.
* **Violetti vihollinen (H):** Liikkuu yksinkertaisesti edestakaisin vaakasuunnassa.
* **Punainen vihollinen (Z):** Älykäs vihollinen, joka pyörii sirkkelimäisesti ja osaa seurata seiniä.

### Pistelasku

* **Timantin kerääminen:** +10 pistettä
* **Vihollisen murskaaminen kivellä:** +50 pistettä

---

## ⚠️ Vinkkejä selviytymiseen

1. **Suunnittele reittisi:** Älä kaiva multaa sokkona kivien alta, tai jäät alle.
2. **Käytä kiviä aseena:** Voit pudottaa kiviä vihollisten niskaan kaivamalla mullan kiven alta juuri oikealla hetkellä, tai työntää kiven kuiluun vihollisen päälle.
3. **Putoamisviive:** Kivet eivät putoa aivan millisekunnissa. Ehdit yleensä siirtyä pois alta, jos kaivat suoraan kiven alta mullan pois ja jatkat matkaasi pysähtymättä.
4. **Varo vieriviä kiviä:** Kivet vierivät sivuille, jos ne putoavat toisen kiven päälle. Pidä tämä mielessä, kun teet kasoja!
