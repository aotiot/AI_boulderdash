"""Boulder Dash - korjattu versio.

Korjatut virheet:
  1. Liukuluvut väriarvoissa kaatoivat pelin Z-vihollista piirrettäessä.
  2. Vihollistörmäys tarkistetaan heti pelaajan siirron jälkeen, ei vasta
     vihollisvuorolla.
  3. Oikealle vierivä kivi ei enää liiku kahta ruutua samalla tikillä.
  4. Vain putoava kivi tappaa - paikallaan lepäävä ei.
  5. Pisteet palautuvat tason alkutilanteeseen kuollessa.
  6. Kaksi vihollista ei voi enää olla samassa ruudussa.
  7. Kaikki kartan indeksit rajatarkistettu.
  8. Valot sekoitetaan BLEND_RGB_MAX:lla, eivät ylikirjoita toisiaan.
  9. Nuolinäppäimen pohjassa pitäminen liikuttaa (oma liikeajastin).
 10. Fontit luodaan kerran, ääniin lisätty verhokäyrä.
 11. Ruudun tärinä ei enää valu UI-palkin päälle.
 12. Uudelleenaloitus nollaa ajastimet; R = alusta taso, ESC = poistu.

Uusi sääntö: avain on piilossa, kunnes vähintään puolet tason timanteista
on kerätty.
"""

import array
import math
import random
import sys

import pygame

# --- Vakiot ---
TILE_SIZE = 40
LEVEYS_RUUDUT = 10
KORKEUS_RUUDUT = 10
WIDTH = LEVEYS_RUUDUT * TILE_SIZE
HEIGHT = KORKEUS_RUUDUT * TILE_SIZE
UI_HEIGHT = 44
WINDOW_HEIGHT = HEIGHT + UI_HEIGHT
FPS = 60

YMPARISTO_VALO = (150, 150, 165)

VIIVE_PUTOAMINEN = 150
VIIVE_VIHOLLINEN = 300
VIIVE_LIIKE = 110

KULJETTAVAT = ('.', 'D', '*', 'K')

kentat = [
    ["WWWWWWWWWW", "WP..D..O.W", "W.W.D....W", "W.O......W", "W.D.D.*D.W",
     "W.DWW..D.W", "W..*DD.O.W", "W.W.WWW..W", "WKDD...X.W", "WWWWWWWWWW"],
    ["WWWWWWWWWW", "W...O....W", "W.P.D.*..W", "W.O.D.O..W", "W.D.D.D..W",
     "W.D.D.D.*W", "W.DDDDD..W", "W.K*O.O.DW", "W.WWW.W.XW", "WWWWWWWWWW"],
    ["WWWWWWWWWW", "WP.D...O.W", "W.WD.O...W", "W.O......W", "W.O.D.W..W",
     "W.W.D.*D.W", "W.KDD..X.W", "W.W.WWW..W", "W.*......W", "WWWWWWWWWW"],
    ["WWWWWWWWWW", "W.H.W..O.W", "W.D.W.H..W", "W.D.W.D..W", "WP..D.*D.W",
     "W.O.D.W..W", "W...D...XW", "W.W.W.WK.W", "W...D....W", "WWWWWWWWWW"],
    ["WWWWWWWWWW", "W...D..X.W", "W.P.D.K..W", "W.O.D.W..W", "W.W.D...*W",
     "W.W.*..H.W", "W.W.D.D..W", "W.W.O....W", "W.H......W", "WWWWWWWWWW"],
    ["WWWWWWWWWW", "WP.O.O.O.W", "W.DDDDDD.W", "W.D.H..D.W", "W.D.*..D.W",
     "W.W.D..D.W", "W.X.DW.K.W", "W...D....W", "W.H.D....W", "WWWWWWWWWW"],
    ["WWWWWWWWWW", "W...Z....W", "W.P...K..W", "W.W.D.D..W", "W.D.O.W..W",
     "W.D.*...ZW", "W.O.D.W..W", "W.D.D..X.W", "W.W.W.D..W", "WWWWWWWWWW"],
    ["WWWWWWWWWW", "W.O...D..W", "W..*Z.D.KW", "WP.D..D..W", "W.D.D.W..W",
     "W.O.O....W", "W.D.D.W..W", "W.Z.*.W.XW", "W.D.D.D..W", "WWWWWWWWWW"],
    ["WWWWWWWWWW", "W...*...XW", "W.P.D.D..W", "W.O.D.W..W", "W.D.O.K..W",
     "W.W.D...ZW", "W.O...W..W", "W.D.D.*..W", "W.Z.D.Z..W", "WWWWWWWWWW"],
    ["WWWWWWWWWW", "WP.D..W..W", "W.WD..W..W", "W.O...O..W", "W.D.D.W.ZW",
     "W.Z.D.*..W", "W.W.K.W..W", "W...D....W", "W.*.D...XW", "WWWWWWWWWW"],
    ["WWWWWWWWWW", "W.X.D...*W", "W.O...Z..W", "W.D.W.W..W", "W.D.O.K..W",
     "WP..D...ZW", "W.W.D.W..W", "W.D.*.W..W", "W.Z...W..W", "WWWWWWWWWW"],
    ["WWWWWWWWWW", "WP..O.O.XW", "W...D.D..W", "W.O.D.W..W", "W.K.D.*..W",
     "W.W.D..Z.W", "W.D.*.W..W", "W.Z...Z..W", "W.W.W.W..W", "WWWWWWWWWW"],
]


# --- Äänet ---
class HiljainenAani:
    """Korvike ennen mikserin alustusta / jos ääni ei ole käytettävissä."""

    def play(self):
        pass


AANET = {}


def soita(nimi):
    aani = AANET.get(nimi)
    if aani is not None:
        aani.play()


def luo_aani(taajuus, kesto_ms, aaltomuoto='sini', liuku=0):
    sample_rate = 44100
    n_samples = max(1, int(sample_rate * (kesto_ms / 1000.0)))
    buf = array.array('h')
    max_amp = 8000
    nousu_kesto = max(1, int(n_samples * 0.05))
    lasku_kesto = max(1, int(n_samples * 0.20))

    for i in range(n_samples):
        t = float(i) / sample_rate
        nyky_taajuus = max(10.0, taajuus + (liuku * i / n_samples))

        if aaltomuoto == 'kantti':
            val = max_amp if math.sin(2 * math.pi * nyky_taajuus * t) > 0 else -max_amp
        elif aaltomuoto == 'kohina':
            val = random.randint(-max_amp, max_amp)
        else:  # 'sini' ja kaikki tuntemattomat
            val = max_amp * math.sin(2 * math.pi * nyky_taajuus * t)

        # Verhokäyrä poistaa napsahdukset alusta ja lopusta
        verho = min(1.0, i / nousu_kesto, (n_samples - i) / lasku_kesto)
        naytto = int(val * verho)
        buf.append(naytto)
        buf.append(naytto)

    return pygame.mixer.Sound(buffer=buf)


def alusta_aanet():
    AANET['timantti'] = luo_aani(800, 100, 'sini', 800)
    AANET['kaivuu'] = luo_aani(100, 50, 'kohina')
    AANET['kivi'] = luo_aani(60, 150, 'kantti', -30)
    AANET['kuolema'] = luo_aani(200, 600, 'kantti', -150)
    AANET['avain'] = luo_aani(500, 200, 'sini', 500)
    AANET['ovi'] = luo_aani(400, 400, 'kantti', 400)
    AANET['murskaus'] = luo_aani(100, 200, 'kohina')
    AANET['ilmestyy'] = luo_aani(300, 450, 'sini', 900)


class Vihollinen:
    def __init__(self, x, y, tyyppi):
        self.x = x
        self.y = y
        self.tyyppi = tyyppi
        self.suunta = 1
        self.suunnat = [(0, -1), (-1, 0), (0, 1), (1, 0)]
        self.suunta_idx = random.randint(0, 3)


# --- Pelitila ---
kartta = []
pelaaja_x = pelaaja_y = 1
pelaaja_suunta = (0, 0)
viholliset = []
partikkelit = []
putoavat = set()

pisteet = 0
pisteet_tason_alussa = 0
nykyinen_kentta = 0

avain_paikka = None
avain_nakyvissa = False
avain_keratty = False
timantteja_yhteensa = 0
timantteja_keratty = 0
timantteja_vaadittu = 0

kuollut = False
peli_lapi = False
ruudun_tarina = 0
putoamis_ajastin = 0
vihollis_ajastin = 0
liike_ajastin = VIIVE_LIIKE


def kartalla(x, y):
    return 0 <= x < LEVEYS_RUUDUT and 0 <= y < KORKEUS_RUUDUT


def ruutu_on(x, y, merkki):
    return kartalla(x, y) and kartta[y][x] == merkki


def vihollinen_kohdassa(x, y):
    for v in viholliset:
        if v.x == x and v.y == y:
            return v
    return None


def lataa_kentta(indeksi):
    """Lataa kentän pelitilaan. Palauttaa False jos kenttää ei ole."""
    global kartta, pelaaja_x, pelaaja_y, pelaaja_suunta, viholliset
    global avain_paikka, avain_nakyvissa, avain_keratty
    global timantteja_yhteensa, timantteja_keratty, timantteja_vaadittu
    global putoavat, partikkelit, pisteet, pisteet_tason_alussa
    global putoamis_ajastin, vihollis_ajastin, liike_ajastin, ruudun_tarina

    if indeksi >= len(kentat):
        return False

    kartta = [list(rivi) for rivi in kentat[indeksi]]
    pelaaja_x, pelaaja_y = 1, 1
    pelaaja_suunta = (0, 0)
    viholliset = []
    avain_paikka = None
    timantteja_yhteensa = 0

    for y in range(len(kartta)):
        for x in range(len(kartta[y])):
            merkki = kartta[y][x]
            if merkki == 'P':
                pelaaja_x, pelaaja_y = x, y
            elif merkki == 'Z':
                viholliset.append(Vihollinen(x, y, 'Z'))
                kartta[y][x] = '.'
            elif merkki == 'H':
                viholliset.append(Vihollinen(x, y, 'H'))
                kartta[y][x] = '.'
            elif merkki == '*':
                timantteja_yhteensa += 1
            elif merkki == 'K':
                avain_paikka = (x, y)
                kartta[y][x] = '.'  # avain piilotetaan aluksi

    timantteja_keratty = 0
    # Vähintään puolet timanteista, ylöspäin pyöristäen
    timantteja_vaadittu = (timantteja_yhteensa + 1) // 2
    avain_nakyvissa = False
    avain_keratty = False

    putoavat = set()
    partikkelit = []
    pisteet = pisteet_tason_alussa
    putoamis_ajastin = 0
    vihollis_ajastin = 0
    liike_ajastin = VIIVE_LIIKE
    ruudun_tarina = 0

    tarkista_avain()
    return True


def luo_partikkeleita(x, y, vari, maara=5):
    for _ in range(maara):
        partikkelit.append({
            'x': x * TILE_SIZE + TILE_SIZE // 2,
            'y': y * TILE_SIZE + TILE_SIZE // 2,
            'vx': random.uniform(-3, 3),
            'vy': random.uniform(-4, 1),
            'elama': random.randint(10, 20),
            'vari': vari,
        })


def kuole():
    global kuollut, ruudun_tarina
    if kuollut:
        return
    kuollut = True
    ruudun_tarina = 15
    soita('kuolema')
    luo_partikkeleita(pelaaja_x, pelaaja_y, (255, 50, 50), 30)


def tarkista_avain():
    """Paljastaa avaimen kun timanttivaatimus täyttyy ja ruutu on vapaa."""
    global avain_nakyvissa
    if avain_nakyvissa or avain_keratty or avain_paikka is None:
        return
    if timantteja_keratty < timantteja_vaadittu:
        return
    ax, ay = avain_paikka
    if kartta[ay][ax] != '.':
        return  # pelaaja tai kivi ruudussa - odotetaan että se vapautuu
    kartta[ay][ax] = 'K'
    avain_nakyvissa = True
    soita('ilmestyy')
    luo_partikkeleita(ax, ay, (255, 220, 0), 18)


def tarkista_vihollistormays():
    if vihollinen_kohdassa(pelaaja_x, pelaaja_y) is not None:
        kuole()
        return True
    return False


def yrita_liike(dx, dy):
    """Palauttaa True jos liike toteutui."""
    global pelaaja_x, pelaaja_y, pelaaja_suunta, pisteet
    global timantteja_keratty, avain_keratty, nykyinen_kentta, peli_lapi
    global pisteet_tason_alussa, ruudun_tarina

    pelaaja_suunta = (dx, dy)
    ux, uy = pelaaja_x + dx, pelaaja_y + dy
    if not kartalla(ux, uy):
        return False

    kohde = kartta[uy][ux]

    if kohde in KULJETTAVAT:
        if kohde == 'D':
            soita('kaivuu')
            luo_partikkeleita(ux, uy, (139, 69, 19), 8)
        elif kohde == '*':
            soita('timantti')
            pisteet += 10
            timantteja_keratty += 1
            luo_partikkeleita(ux, uy, (100, 255, 255), 10)
        elif kohde == 'K':
            soita('avain')
            avain_keratty = True

        kartta[pelaaja_y][pelaaja_x] = '.'
        pelaaja_x, pelaaja_y = ux, uy
        kartta[pelaaja_y][pelaaja_x] = 'P'
        tarkista_avain()
        tarkista_vihollistormays()
        return True

    if kohde == 'O' and dy == 0:
        takana_x = ux + dx
        if ruutu_on(takana_x, uy, '.'):
            murskattu = vihollinen_kohdassa(takana_x, uy)
            if murskattu is not None:
                soita('murskaus')
                viholliset.remove(murskattu)
                pisteet += 50
                luo_partikkeleita(takana_x, uy, (255, 50, 50), 25)
                ruudun_tarina = 8
            kartta[uy][takana_x] = 'O'
            kartta[pelaaja_y][pelaaja_x] = '.'
            pelaaja_x, pelaaja_y = ux, uy
            kartta[pelaaja_y][pelaaja_x] = 'P'
            tarkista_avain()
            tarkista_vihollistormays()
            return True
        return False

    if kohde == 'X' and avain_keratty:
        soita('ovi')
        pisteet_tason_alussa = pisteet
        nykyinen_kentta += 1
        if not lataa_kentta(nykyinen_kentta):
            peli_lapi = True
        return True

    return False


def paivita_viholliset():
    varatut = {(v.x, v.y) for v in viholliset}

    for v in viholliset:
        varatut.discard((v.x, v.y))

        if v.tyyppi == 'H':
            kohde_x = v.x + v.suunta
            if (kohde_x, v.y) == (pelaaja_x, pelaaja_y):
                kuole()
            elif ruutu_on(kohde_x, v.y, '.') and (kohde_x, v.y) not in varatut:
                v.x = kohde_x
            else:
                v.suunta *= -1
        else:  # 'Z' seuraa seinää
            jarjestys = [
                (v.suunta_idx + 1) % 4,
                v.suunta_idx,
                (v.suunta_idx - 1) % 4,
                (v.suunta_idx + 2) % 4,
            ]
            for u in jarjestys:
                hx = v.x + v.suunnat[u][0]
                hy = v.y + v.suunnat[u][1]
                if (hx, hy) == (pelaaja_x, pelaaja_y):
                    kuole()
                    v.suunta_idx = u
                    break
                if ruutu_on(hx, hy, '.') and (hx, hy) not in varatut:
                    v.x, v.y, v.suunta_idx = hx, hy, u
                    break

        varatut.add((v.x, v.y))

    tarkista_vihollistormays()


def paivita_kivet():
    """Kivien putoaminen ja vieriminen. Vain putoava kivi tappaa."""
    global putoavat, pisteet, ruudun_tarina

    uudet_putoavat = set()
    kasitelty = set()

    for y in range(KORKEUS_RUUDUT - 2, -1, -1):
        for x in range(LEVEYS_RUUDUT):
            if kartta[y][x] != 'O' or (x, y) in kasitelty:
                continue

            putoaa = (x, y) in putoavat
            alla = kartta[y + 1][x]

            if alla == '.':
                osuttu = vihollinen_kohdassa(x, y + 1)
                kartta[y][x] = '.'
                kartta[y + 1][x] = 'O'
                # Merkitään siirretty kivi, ettei sitä käsitellä uudestaan
                kasitelty.add((x, y + 1))
                uudet_putoavat.add((x, y + 1))

                if osuttu is not None:
                    viholliset.remove(osuttu)
                    soita('murskaus')
                    pisteet += 50
                    luo_partikkeleita(x, y + 1, (255, 50, 50), 25)
                    ruudun_tarina = 8
                elif y + 2 >= KORKEUS_RUUDUT or kartta[y + 2][x] != '.':
                    soita('kivi')
                    ruudun_tarina = 4
                    luo_partikkeleita(x, y + 1, (150, 150, 150), 4)

            elif alla == 'P':
                if putoaa:
                    kuole()

            elif alla == 'O':
                for suunta in (-1, 1):
                    nx = x + suunta
                    if not kartalla(nx, y):
                        continue
                    if kartta[y][nx] == '.' and kartta[y + 1][nx] == '.':
                        kartta[y][x] = '.'
                        kartta[y][nx] = 'O'
                        kasitelty.add((nx, y))
                        uudet_putoavat.add((nx, y))
                        break

    putoavat = uudet_putoavat
    tarkista_avain()


# --- Piirto ---
tausta_tekstuurit = {}
for _y in range(KORKEUS_RUUDUT):
    for _x in range(LEVEYS_RUUDUT):
        tausta_tekstuurit[(_x, _y)] = {
            'multa': [(random.randint(2, TILE_SIZE - 6), random.randint(2, TILE_SIZE - 6))
                      for _ in range(8)],
            'seina': [(random.randint(5, TILE_SIZE - 12), random.randint(5, TILE_SIZE - 8))
                      for _ in range(4)],
        }

_valo_kakku = {}


def valo_pinta(max_sade, max_voimakkuus, vari):
    """Esirenderöity valokiekko. Musta tausta -> BLEND_RGB_MAX jättää sen huomiotta."""
    avain = (max_sade, max_voimakkuus, vari)
    pinta = _valo_kakku.get(avain)
    if pinta is None:
        pinta = pygame.Surface((max_sade * 2, max_sade * 2))
        pinta.fill((0, 0, 0))
        for sade in range(max_sade, 0, -2):
            v = (1.0 - sade / float(max_sade)) * max_voimakkuus
            c = (min(255, int(vari[0] + v)),
                 min(255, int(vari[1] + v)),
                 min(255, int(vari[2] + v)))
            pygame.draw.circle(pinta, c, (max_sade, max_sade), sade)
        _valo_kakku[avain] = pinta
    return pinta


def piirra_valo(valo_kangas, x, y, max_sade, max_voimakkuus, vari):
    pinta = valo_pinta(max_sade, max_voimakkuus, vari)
    valo_kangas.blit(pinta, (x - max_sade, y - max_sade),
                     special_flags=pygame.BLEND_RGB_MAX)


def piirra_varjo(kangas, x, y, sade_x=16, sade_y=8):
    pygame.draw.ellipse(kangas, (10, 10, 15), (x - sade_x, y + 10, sade_x * 2, sade_y))


def piirra_kentta(kangas, valo_kangas, aika):
    kangas.fill((25, 25, 30))
    valo_kangas.fill(YMPARISTO_VALO)

    for y, rivi in enumerate(kartta):
        for x, merkki in enumerate(rivi):
            px, py = x * TILE_SIZE, y * TILE_SIZE
            keski_x, keski_y = px + 20, py + 20

            if merkki in ('.', 'P', 'O', '*'):
                pygame.draw.rect(kangas, (30, 30, 35), (px, py, TILE_SIZE, TILE_SIZE), 1)

            if merkki == 'W':
                pygame.draw.rect(kangas, (70, 70, 80), (px, py, TILE_SIZE, TILE_SIZE))
                pygame.draw.polygon(kangas, (100, 100, 110),
                                    [(px, py), (px + 40, py), (px + 35, py + 5), (px + 5, py + 5)])
                pygame.draw.polygon(kangas, (40, 40, 50),
                                    [(px, py + 40), (px + 40, py + 40), (px + 35, py + 35), (px + 5, py + 35)])
                for hx, hy in tausta_tekstuurit[(x, y)]['seina']:
                    pygame.draw.line(kangas, (50, 50, 60),
                                     (px + hx, py + hy), (px + hx + 8, py + hy + 5), 2)

            elif merkki == 'D':
                pygame.draw.rect(kangas, (101, 53, 15), (px, py, TILE_SIZE, TILE_SIZE))
                for tx, ty in tausta_tekstuurit[(x, y)]['multa']:
                    pygame.draw.rect(kangas, (70, 30, 5), (px + tx, py + ty, 4, 4))

            elif merkki == 'O':
                piirra_varjo(kangas, keski_x, keski_y)
                pygame.draw.circle(kangas, (130, 130, 130), (keski_x, keski_y), 16)
                pygame.draw.circle(kangas, (170, 170, 170), (keski_x - 3, keski_y - 3), 13)
                pygame.draw.arc(kangas, (90, 90, 90), (px + 8, py + 12, 12, 12), 0, 3.14, 2)

            elif merkki == '*':
                piirra_valo(valo_kangas, keski_x, keski_y, 40, 100, (0, 150, 150))
                y_offset = int(math.sin(aika / 200.0) * 2)
                ty = py + 5 + y_offset
                piirra_varjo(kangas, keski_x, keski_y, 12, 6)
                pygame.draw.polygon(kangas, (150, 255, 255),
                                    [(keski_x, ty), (px + 35, keski_y + y_offset), (keski_x, keski_y + y_offset)])
                pygame.draw.polygon(kangas, (255, 255, 255),
                                    [(keski_x, ty), (px + 5, keski_y + y_offset), (keski_x, keski_y + y_offset)])
                pygame.draw.polygon(kangas, (0, 200, 200),
                                    [(px + 5, keski_y + y_offset), (keski_x, py + 35 + y_offset), (keski_x, keski_y + y_offset)])
                pygame.draw.polygon(kangas, (0, 150, 150),
                                    [(px + 35, keski_y + y_offset), (keski_x, py + 35 + y_offset), (keski_x, keski_y + y_offset)])

            elif merkki == 'K':
                y_leijunta = int(math.sin(aika / 150.0) * 4)
                piirra_valo(valo_kangas, keski_x, keski_y, 60, 130, (150, 150, 0))
                pygame.draw.circle(kangas, (255, 220, 0), (keski_x, keski_y + y_leijunta - 5), 6, 2)
                pygame.draw.rect(kangas, (255, 220, 0), (keski_x - 2, keski_y + y_leijunta, 4, 10))
                pygame.draw.rect(kangas, (255, 220, 0), (keski_x, keski_y + y_leijunta + 6, 6, 3))

            elif merkki == 'X':
                if avain_keratty:
                    pulssi = (math.sin(aika / 100.0) + 1) / 2
                    pygame.draw.rect(kangas, (0, int(150 + 105 * pulssi), 0),
                                     (px + 5, py + 5, 30, 35))
                    piirra_valo(valo_kangas, keski_x, keski_y, 80, 150, (0, 200, 0))
                else:
                    pygame.draw.rect(kangas, (139, 0, 0), (px + 5, py + 5, 30, 35), border_radius=5)
                    pygame.draw.circle(kangas, (0, 0, 0), (keski_x, keski_y + 5), 4)
                    pygame.draw.rect(kangas, (0, 0, 0), (keski_x - 1, keski_y + 5, 3, 6))

            elif merkki == 'P' and not kuollut:
                piirra_valo(valo_kangas, keski_x, keski_y, 160, 200, (150, 150, 100))
                piirra_varjo(kangas, keski_x, keski_y)

                pygame.draw.circle(kangas, (255, 200, 150), (keski_x, keski_y), 13)
                pygame.draw.polygon(kangas, (255, 200, 0),
                                    [(px + 5, keski_y - 2), (px + 35, keski_y - 2),
                                     (px + 28, py + 3), (px + 12, py + 3)])
                pygame.draw.line(kangas, (200, 150, 0),
                                 (px + 5, keski_y - 2), (px + 35, keski_y - 2), 2)

                sx, sy = pelaaja_suunta[0] * 3, pelaaja_suunta[1] * 3
                pygame.draw.circle(kangas, (255, 255, 255), (keski_x - 5 + sx, keski_y + 3 + sy), 4)
                pygame.draw.circle(kangas, (255, 255, 255), (keski_x + 5 + sx, keski_y + 3 + sy), 4)
                pygame.draw.circle(kangas, (0, 0, 0),
                                   (keski_x - 5 + int(sx * 1.5), keski_y + 3 + int(sy * 1.5)), 2)
                pygame.draw.circle(kangas, (0, 0, 0),
                                   (keski_x + 5 + int(sx * 1.5), keski_y + 3 + int(sy * 1.5)), 2)
                pygame.draw.circle(kangas, (255, 255, 200), (keski_x + sx, py + 8 + sy), 4)

    # Viholliset
    for v in viholliset:
        px, py = v.x * TILE_SIZE, v.y * TILE_SIZE
        keski_x, keski_y = px + 20, py + 20
        pulssi = (math.sin(aika / 100.0) + 1) / 2

        piirra_varjo(kangas, keski_x, keski_y)

        if v.tyyppi == 'H':
            vari = (150, 0, 150)
            piirra_valo(valo_kangas, keski_x, keski_y, 60, 100, (100, 0, 100))
        else:
            vari = (int(200 + 55 * pulssi), 0, 0)
            piirra_valo(valo_kangas, keski_x, keski_y, 60, 100, (150, 0, 0))

        pygame.draw.circle(kangas, vari, (keski_x, keski_y), 13)

        kulma = aika / 200.0 if v.tyyppi == 'H' else -aika / 150.0
        for i in range(6):
            k = kulma + i * (math.pi / 3)
            terax = int(keski_x + math.cos(k) * 16)
            teray = int(keski_y + math.sin(k) * 16)
            pygame.draw.circle(kangas, (200, 200, 200), (terax, teray), 3)

        pygame.draw.polygon(kangas, (255, 255, 0),
                            [(px + 10, py + 15), (px + 16, py + 18), (px + 10, py + 20)])
        pygame.draw.polygon(kangas, (255, 255, 0),
                            [(px + 30, py + 15), (px + 24, py + 18), (px + 30, py + 20)])

    # Partikkelit
    for p in partikkelit[:]:
        p['x'] += p['vx']
        p['y'] += p['vy']
        p['vy'] += 0.5
        p['elama'] -= 1
        if p['elama'] <= 0:
            partikkelit.remove(p)
        else:
            pygame.draw.circle(kangas, p['vari'], (int(p['x']), int(p['y'])),
                               max(1, p['elama'] // 3))

    kangas.blit(valo_kangas, (0, 0), special_flags=pygame.BLEND_RGB_MULT)


def piirra_ui(ruutu, fontti):
    pygame.draw.rect(ruutu, (18, 18, 24), (0, 0, WIDTH, UI_HEIGHT))
    pygame.draw.line(ruutu, (60, 60, 70), (0, UI_HEIGHT - 1), (WIDTH, UI_HEIGHT - 1))

    taso_teksti = fontti.render(f"Taso {nykyinen_kentta + 1}/{len(kentat)}", True, (200, 200, 200))
    piste_teksti = fontti.render(f"Pisteet {pisteet}", True, (255, 215, 0))

    if avain_keratty:
        keski_teksti = fontti.render("Avain hallussa", True, (120, 255, 120))
    elif avain_nakyvissa:
        keski_teksti = fontti.render("Avain esilla!", True, (255, 220, 0))
    else:
        keski_teksti = fontti.render(
            f"Timantit {timantteja_keratty}/{timantteja_vaadittu}", True, (150, 255, 255))

    ruutu.blit(taso_teksti, (12, UI_HEIGHT // 2 - taso_teksti.get_height() // 2))
    ruutu.blit(keski_teksti, (WIDTH // 2 - keski_teksti.get_width() // 2,
                              UI_HEIGHT // 2 - keski_teksti.get_height() // 2))
    ruutu.blit(piste_teksti, (WIDTH - piste_teksti.get_width() - 12,
                              UI_HEIGHT // 2 - piste_teksti.get_height() // 2))


def piirra_ilmoitus(ruutu, iso_fontti, pieni_fontti, otsikko, vari, ohje):
    peite = pygame.Surface((WIDTH, HEIGHT))
    peite.set_alpha(150)
    peite.fill((0, 0, 0))
    ruutu.blit(peite, (0, UI_HEIGHT))

    t = iso_fontti.render(otsikko, True, vari)
    o = pieni_fontti.render(ohje, True, (220, 220, 220))
    ruutu.blit(t, (WIDTH // 2 - t.get_width() // 2, UI_HEIGHT + HEIGHT // 2 - 30))
    ruutu.blit(o, (WIDTH // 2 - o.get_width() // 2, UI_HEIGHT + HEIGHT // 2 + 20))


def main():
    global kuollut, peli_lapi, nykyinen_kentta, pisteet, pisteet_tason_alussa
    global putoamis_ajastin, vihollis_ajastin, liike_ajastin, ruudun_tarina

    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    try:
        alusta_aanet()
    except pygame.error:
        pass  # ilman äänilaitetta peli toimii mykkänä

    ruutu = pygame.display.set_mode((WIDTH, WINDOW_HEIGHT))
    kangas = pygame.Surface((WIDTH, HEIGHT))
    valo_kangas = pygame.Surface((WIDTH, HEIGHT))
    pygame.display.set_caption("Boulder Dash")
    kello = pygame.time.Clock()

    fontti_ui = pygame.font.SysFont(None, 24)
    fontti_iso = pygame.font.SysFont(None, 48)
    fontti_ohje = pygame.font.SysFont(None, 22)

    lataa_kentta(nykyinen_kentta)

    while True:
        dt = kello.tick(FPS)
        aika = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if peli_lapi:
                    if event.key == pygame.K_r:
                        nykyinen_kentta = 0
                        pisteet_tason_alussa = 0
                        peli_lapi = False
                        lataa_kentta(nykyinen_kentta)
                elif kuollut or event.key == pygame.K_r:
                    kuollut = False
                    lataa_kentta(nykyinen_kentta)

        if not kuollut and not peli_lapi:
            putoamis_ajastin += dt
            vihollis_ajastin += dt
            liike_ajastin += dt
            ruudun_tarina = max(0, ruudun_tarina - 1)

            if liike_ajastin >= VIIVE_LIIKE:
                napit = pygame.key.get_pressed()
                dx = dy = 0
                if napit[pygame.K_LEFT]:
                    dx = -1
                elif napit[pygame.K_RIGHT]:
                    dx = 1
                elif napit[pygame.K_UP]:
                    dy = -1
                elif napit[pygame.K_DOWN]:
                    dy = 1
                if dx or dy:
                    yrita_liike(dx, dy)
                    liike_ajastin = 0

            if not kuollut and not peli_lapi and vihollis_ajastin >= VIIVE_VIHOLLINEN:
                paivita_viholliset()
                vihollis_ajastin = 0

            if not kuollut and not peli_lapi and putoamis_ajastin >= VIIVE_PUTOAMINEN:
                paivita_kivet()
                putoamis_ajastin = 0

        piirra_kentta(kangas, valo_kangas, aika)

        ruutu.fill((10, 10, 15))
        offset_x = random.randint(-ruudun_tarina, ruudun_tarina)
        offset_y = random.randint(-ruudun_tarina, ruudun_tarina)
        ruutu.blit(kangas, (offset_x, UI_HEIGHT + offset_y))

        # UI viimeisenä, jotta tärinä ei valu palkin päälle
        piirra_ui(ruutu, fontti_ui)

        if kuollut:
            piirra_ilmoitus(ruutu, fontti_iso, fontti_ohje, "KUOLIT!", (255, 50, 50),
                            "Mika tahansa nappi = uudelleen")
        elif peli_lapi:
            piirra_ilmoitus(ruutu, fontti_iso, fontti_ohje, "VOITIT PELIN!", (50, 255, 50),
                            f"Pisteet {pisteet} - R = alusta, ESC = lopeta")

        pygame.display.flip()


if __name__ == "__main__":
    main()
