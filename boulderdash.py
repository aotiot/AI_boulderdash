import pygame
import sys
import math
import random
import array

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

TILE_SIZE = 40
WIDTH = 10 * TILE_SIZE
HEIGHT = 10 * TILE_SIZE
UI_HEIGHT = 40
WINDOW_HEIGHT = HEIGHT + UI_HEIGHT
FPS = 30

ruutu = pygame.display.set_mode((WIDTH, WINDOW_HEIGHT))
kangas = pygame.Surface((WIDTH, HEIGHT))
valo_kangas = pygame.Surface((WIDTH, HEIGHT))
pygame.display.set_caption("Boulder Dash - Kirkkaampi tausta")
kello = pygame.time.Clock()
fontti_ui = pygame.font.SysFont(None, 28)

# --- UUSI PERUSVALAISTUS ---
YMPARISTO_VALO = (150, 150, 165) # Paljon kirkkaampi, hieman sinertävä "hämärä"

# --- ÄÄNET ---
def luo_aani(taajuus, kesto_ms, aaltomuoto='sini', liuku=0):
    sample_rate = 44100
    n_samples = int(sample_rate * (kesto_ms / 1000.0))
    buf = array.array('h')
    max_amp = 8000
    for i in range(n_samples):
        t = float(i) / sample_rate
        nyky_taajuus = max(10, taajuus + (liuku * i / n_samples))
        if aaltomuoto == 'sini':
            val = int(max_amp * math.sin(2 * math.pi * nyky_taajuus * t))
        elif aaltomuoto == 'kantti':
            val = max_amp if math.sin(2 * math.pi * nyky_taajuus * t) > 0 else -max_amp
        elif aaltomuoto == 'kohina':
            val = random.randint(-max_amp, max_amp)
        buf.append(val)
        buf.append(val)
    return pygame.mixer.Sound(buffer=buf)

aani_timantti = luo_aani(800, 100, 'sini', 800)
aani_kaivuu = luo_aani(100, 50, 'kohina')
aani_kivi = luo_aani(60, 150, 'kantti', -30)
aani_kuolema = luo_aani(200, 600, 'kantti', -150)
aani_avain = luo_aani(500, 200, 'sini', 500)
aani_ovi = luo_aani(400, 400, 'kantti', 400)
aani_murskaus = luo_aani(100, 200, 'kohina')

pisteet = 0

kentat = [
    ["WWWWWWWWWW","WP..D..O.W","W.W.D....W","W.O......W","W.D.D.*D.W","W.DWW..D.W","W..*DD.O.W","W.W.WWW..W","WKDD...X.W","WWWWWWWWWW"],
    ["WWWWWWWWWW","W...O....W","W.P.D.*..W","W.O.D.O..W","W.D.D.D..W","W.D.D.D.*W","W.DDDDD..W","W.K*O.O.DW","W.WWW.W.XW","WWWWWWWWWW"],
    ["WWWWWWWWWW","WP.D...O.W","W.WD.O...W","W.O......W","W.O.D.W..W","W.W.D.*D.W","W.KDD..X.W","W.W.WWW..W","W.*......W","WWWWWWWWWW"],
    ["WWWWWWWWWW","W.H.W..O.W","W.D.W.H..W","W.D.W.D..W","WP..D.*D.W","W.O.D.W..W","W...D...XW","W.W.W.WK.W","W...D....W","WWWWWWWWWW"],
    ["WWWWWWWWWW","W...D..X.W","W.P.D.K..W","W.O.D.W..W","W.W.D...*W","W.W.*..H.W","W.W.D.D..W","W.W.O....W","W.H......W","WWWWWWWWWW"],
    ["WWWWWWWWWW","WP.O.O.O.W","W.DDDDDD.W","W.D.H..D.W","W.D.*..D.W","W.W.D..D.W","W.X.DW.K.W","W...D....W","W.H.D....W","WWWWWWWWWW"],
    ["WWWWWWWWWW","W...Z....W","W.P...K..W","W.W.D.D..W","W.D.O.W..W","W.D.*...ZW","W.O.D.W..W","W.D.D..X.W","W.W.W.D..W","WWWWWWWWWW"],
    ["WWWWWWWWWW","W.O...D..W","W..*Z.D.KW","WP.D..D..W","W.D.D.W..W","W.O.O....W","W.D.D.W..W","W.Z.*.W.XW","W.D.D.D..W","WWWWWWWWWW"],
    ["WWWWWWWWWW","W...*...XW","W.P.D.D..W","W.O.D.W..W","W.D.O.K..W","W.W.D...ZW","W.O...W..W","W.D.D.*..W","W.Z.D.Z..W","WWWWWWWWWW"],
    ["WWWWWWWWWW","WP.D..W..W","W.WD..W..W","W.O...O..W","W.D.D.W.ZW","W.Z.D.*..W","W.W.K.W..W","W...D....W","W.*.D...XW","WWWWWWWWWW"],
    ["WWWWWWWWWW","W.X.D...*W","W.O...Z..W","W.D.W.W..W","W.D.O.K..W","WP..D...ZW","W.W.D.W..W","W.D.*.W..W","W.Z...W..W","WWWWWWWWWW"],
    ["WWWWWWWWWW","WP..O.O.XW","W...D.D..W","W.O.D.W..W","W.K.D.*..W","W.W.D..Z.W","W.D.*.W..W","W.Z...Z..W","W.W.W.W..W","WWWWWWWWWW"]
]

class Vihollinen:
    def __init__(self, x, y, tyyppi):
        self.x = x; self.y = y; self.tyyppi = tyyppi
        self.suunta = 1; self.suunnat = [(0, -1), (-1, 0), (0, 1), (1, 0)]
        self.suunta_idx = random.randint(0, 3)

def lataa_kentta(indeksi):
    if indeksi >= len(kentat): return None, 1, 1, [], False
    kartta = [list(rivi) for rivi in kentat[indeksi]]
    px, py = 1, 1
    viholliset = []
    for y in range(len(kartta)):
        for x in range(len(kartta[0])):
            if kartta[y][x] == 'P': px, py = x, y
            elif kartta[y][x] == 'Z': viholliset.append(Vihollinen(x, y, 'Z')); kartta[y][x] = '.' 
            elif kartta[y][x] == 'H': viholliset.append(Vihollinen(x, y, 'H')); kartta[y][x] = '.' 
    return kartta, px, py, viholliset, False

tausta_tekstuurit = {}
for y in range(20):
    for x in range(20):
        tausta_tekstuurit[(x, y)] = {
            'multa': [(random.randint(2, TILE_SIZE-2), random.randint(2, TILE_SIZE-2)) for _ in range(8)],
            'seina': [(random.randint(5, TILE_SIZE-5), random.randint(5, TILE_SIZE-5)) for _ in range(4)]
        }

partikkelit = []
ruudun_tarina = 0

def luo_partikkeleita(x, y, vari, maara=5):
    for _ in range(maara):
        partikkelit.append({
            'x': x * TILE_SIZE + TILE_SIZE // 2, 'y': y * TILE_SIZE + TILE_SIZE // 2,
            'vx': random.uniform(-3, 3), 'vy': random.uniform(-4, 1),
            'elama': random.randint(10, 20), 'vari': vari
        })

def piirra_varjo(x, y, sade_x=16, sade_y=8):
    pygame.draw.ellipse(kangas, (10, 10, 15), (x - sade_x, y + 10, sade_x*2, sade_y))

# UUSI: Valaistuksen sulautus koodi
def piirra_valo(x, y, max_sade, max_voimakkuus, vari):
    for sade in range(max_sade, 0, -20):
        v = int((1 - (sade / max_sade)) * max_voimakkuus)
        # Käytetään max(), jotta valo ei koskaan renderöidy taustaa tummempana
        c = (
            min(255, max(YMPARISTO_VALO[0], vari[0] + v)),
            min(255, max(YMPARISTO_VALO[1], vari[1] + v)),
            min(255, max(YMPARISTO_VALO[2], vari[2] + v))
        )
        pygame.draw.circle(valo_kangas, c, (x, y), sade)

nykyinen_kentta = 0
kartta, pelaaja_x, pelaaja_y, viholliset, avain_keratty = lataa_kentta(nykyinen_kentta)
putoamis_ajastin = vihollis_ajastin = 0
VIIVE_PUTOAMINEN, VIIVE_VIHOLLINEN = 150, 300
pelaaja_suunta = (0, 0)
kuollut = peli_lapi = False

while True:
    dt = kello.tick(FPS)
    aika = pygame.time.get_ticks()
    
    if not kuollut and not peli_lapi:
        putoamis_ajastin += dt
        vihollis_ajastin += dt
        ruudun_tarina = max(0, ruudun_tarina - 1)
        
        dx, dy = 0, 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT: dx = -1
                elif event.key == pygame.K_RIGHT: dx = 1
                elif event.key == pygame.K_UP: dy = -1
                elif event.key == pygame.K_DOWN: dy = 1

        if dx != 0 or dy != 0:
            pelaaja_suunta = (dx, dy)
            ux, uy = pelaaja_x + dx, pelaaja_y + dy
            kohde = kartta[uy][ux]

            if kohde in ['.', 'D', '*', 'K']:
                if kohde == 'D': 
                    aani_kaivuu.play(); luo_partikkeleita(ux, uy, (139, 69, 19), 8)
                elif kohde == '*': 
                    aani_timantti.play(); pisteet += 10; luo_partikkeleita(ux, uy, (100, 255, 255), 10)
                elif kohde == 'K': 
                    aani_avain.play(); avain_keratty = True
                
                kartta[pelaaja_y][pelaaja_x] = '.'
                pelaaja_x, pelaaja_y = ux, uy
                kartta[pelaaja_y][pelaaja_x] = 'P'
                
            elif kohde == 'O' and dy == 0:
                takana_x = ux + dx
                if kartta[uy][takana_x] == '.':
                    murskattu_v = next((v for v in viholliset if v.x == takana_x and v.y == uy), None)
                    if murskattu_v:
                        aani_murskaus.play(); viholliset.remove(murskattu_v)
                        pisteet += 50; luo_partikkeleita(takana_x, uy, (255, 50, 50), 25)
                        ruudun_tarina = 8
                    kartta[uy][takana_x] = 'O'; kartta[pelaaja_y][pelaaja_x] = '.'
                    pelaaja_x, pelaaja_y = ux, uy; kartta[pelaaja_y][pelaaja_x] = 'P'
            elif kohde == 'X' and avain_keratty:
                aani_ovi.play()
                nykyinen_kentta += 1
                s = lataa_kentta(nykyinen_kentta)
                if s[0] is None: peli_lapi = True
                else: kartta, pelaaja_x, pelaaja_y, viholliset, avain_keratty = s

        if vihollis_ajastin > VIIVE_VIHOLLINEN:
            for v in viholliset:
                if v.tyyppi == 'H':
                    kohde_x = v.x + v.suunta
                    if kohde_x == pelaaja_x and v.y == pelaaja_y:
                        kuollut = True; luo_partikkeleita(pelaaja_x, pelaaja_y, (255, 0, 0), 30)
                    elif kartta[v.y][kohde_x] == '.': v.x = kohde_x
                    else: v.suunta *= -1 
                elif v.tyyppi == 'Z':
                    suunnat = [(v.suunta_idx + 1) % 4, v.suunta_idx, (v.suunta_idx - 1) % 4, (v.suunta_idx + 2) % 4]
                    for u in suunnat:
                        hx, hy = v.x + v.suunnat[u][0], v.y + v.suunnat[u][1]
                        if hx == pelaaja_x and hy == pelaaja_y:
                            kuollut = True; luo_partikkeleita(pelaaja_x, pelaaja_y, (255, 0, 0), 30)
                            v.x, v.y, v.suunta_idx = hx, hy, u; break
                        elif kartta[hy][hx] == '.':
                            v.x, v.y, v.suunta_idx = hx, hy, u; break
            vihollis_ajastin = 0
            if kuollut: aani_kuolema.play(); ruudun_tarina = 15

            if not kuollut:
                for v in viholliset:
                    if v.x == pelaaja_x and v.y == pelaaja_y:
                        kuollut = True; aani_kuolema.play(); ruudun_tarina = 15
                        luo_partikkeleita(pelaaja_x, pelaaja_y, (255, 0, 0), 30)

        if putoamis_ajastin > VIIVE_PUTOAMINEN:
            for y in range(len(kartta)-2, -1, -1):
                for x in range(len(kartta[0])):
                    if kartta[y][x] == 'O':
                        alla = kartta[y+1][x]
                        if alla == '.':
                            osuttu_v = next((v for v in viholliset if v.x == x and v.y == y+1), None)
                            kartta[y+1][x] = 'O'; kartta[y][x] = '.'
                            if osuttu_v:
                                viholliset.remove(osuttu_v); aani_murskaus.play()
                                pisteet += 50; luo_partikkeleita(x, y+1, (255, 50, 50), 25); ruudun_tarina = 8
                            elif y+2 < len(kartta) and kartta[y+2][x] not in ['.', 'P', '*']:
                                aani_kivi.play(); ruudun_tarina = 4; luo_partikkeleita(x, y+1, (150, 150, 150), 4)
                        elif alla == 'P':
                            kuollut = True; aani_kuolema.play(); ruudun_tarina = 15
                            luo_partikkeleita(pelaaja_x, pelaaja_y, (255, 0, 0), 30)
                        elif alla == 'O':
                            if kartta[y][x-1] == '.' and kartta[y+1][x-1] == '.':
                                kartta[y][x-1] = 'O'; kartta[y][x] = '.'
                            elif kartta[y][x+1] == '.' and kartta[y+1][x+1] == '.':
                                kartta[y][x+1] = 'O'; kartta[y][x] = '.'
            putoamis_ajastin = 0

    else:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and kuollut:
                kartta, pelaaja_x, pelaaja_y, viholliset, avain_keratty = lataa_kentta(nykyinen_kentta)
                kuollut = False; partikkelit.clear()

    # Kankaiden nollaus
    kangas.fill((25, 25, 30)) 
    valo_kangas.fill(YMPARISTO_VALO) 
    
    for y, rivi in enumerate(kartta):
        for x, merkki in enumerate(rivi):
            px, py = x * TILE_SIZE, y * TILE_SIZE
            keski_x, keski_y = px + 20, py + 20
            
            if merkki == '.' or merkki == 'P' or merkki == 'O' or merkki == '*':
                pygame.draw.rect(kangas, (30, 30, 35), (px, py, TILE_SIZE, TILE_SIZE), 1)

            if merkki == 'W':
                pygame.draw.rect(kangas, (70, 70, 80), (px, py, TILE_SIZE, TILE_SIZE))
                pygame.draw.polygon(kangas, (100, 100, 110), [(px,py), (px+40,py), (px+35,py+5), (px+5,py+5)])
                pygame.draw.polygon(kangas, (40, 40, 50), [(px,py+40), (px+40,py+40), (px+35,py+35), (px+5,py+35)])
                for hx, hy in tausta_tekstuurit[(x,y)]['seina']:
                    pygame.draw.line(kangas, (50, 50, 60), (px+hx, py+hy), (px+hx+8, py+hy+5), 2)
                    
            elif merkki == 'D':
                pygame.draw.rect(kangas, (101, 53, 15), (px, py, TILE_SIZE, TILE_SIZE))
                for tx, ty in tausta_tekstuurit[(x, y)]['multa']:
                    pygame.draw.rect(kangas, (70, 30, 5), (px+tx, py+ty, 4, 4))
                    
            elif merkki == 'O':
                piirra_varjo(keski_x, keski_y)
                pygame.draw.circle(kangas, (130, 130, 130), (keski_x, keski_y), 16)
                pygame.draw.circle(kangas, (170, 170, 170), (keski_x - 3, keski_y - 3), 13)
                pygame.draw.arc(kangas, (90, 90, 90), (px+8, py+12, 12, 12), 0, 3.14, 2)
                
            elif merkki == '*':
                piirra_valo(keski_x, keski_y, 40, 100, (0, 150, 150))
                y_offset = int(math.sin(aika/200)*2)
                ty = py + 5 + y_offset
                piirra_varjo(keski_x, keski_y, 12, 6)
                pygame.draw.polygon(kangas, (150, 255, 255), [(keski_x, ty), (px+35, keski_y+y_offset), (keski_x, keski_y+y_offset)])
                pygame.draw.polygon(kangas, (255, 255, 255), [(keski_x, ty), (px+5, keski_y+y_offset), (keski_x, keski_y+y_offset)]) 
                pygame.draw.polygon(kangas, (0, 200, 200), [(px+5, keski_y+y_offset), (keski_x, py+35+y_offset), (keski_x, keski_y+y_offset)])
                pygame.draw.polygon(kangas, (0, 150, 150), [(px+35, keski_y+y_offset), (keski_x, py+35+y_offset), (keski_x, keski_y+y_offset)])

            elif merkki == 'K':
                y_leijunta = math.sin(aika / 150.0) * 4
                piirra_valo(keski_x, keski_y, 50, 100, (150, 150, 0))
                pygame.draw.circle(kangas, (255, 220, 0), (keski_x, int(keski_y + y_leijunta - 5)), 6, 2)
                pygame.draw.rect(kangas, (255, 220, 0), (keski_x - 2, int(keski_y + y_leijunta), 4, 10))
                pygame.draw.rect(kangas, (255, 220, 0), (keski_x, int(keski_y + y_leijunta + 6), 6, 3))
                
            elif merkki == 'X':
                if avain_keratty:
                    pulssi = (math.sin(aika / 100.0) + 1) / 2
                    pygame.draw.rect(kangas, (0, int(150 + 105*pulssi), 0), (px+5, py+5, 30, 35))
                    piirra_valo(keski_x, keski_y, 80, 150, (0, 200, 0))
                else:
                    pygame.draw.rect(kangas, (139, 0, 0), (px+5, py+5, 30, 35), border_radius=5)
                    pygame.draw.circle(kangas, (0, 0, 0), (keski_x, keski_y+5), 4)
                    pygame.draw.rect(kangas, (0, 0, 0), (keski_x-1, keski_y+5, 3, 6))
                    
            elif merkki == 'P' and not kuollut:
                piirra_valo(keski_x, keski_y, 160, 200, (150, 150, 100))
                piirra_varjo(keski_x, keski_y)
                
                pygame.draw.circle(kangas, (255, 200, 150), (keski_x, keski_y), 13)
                pygame.draw.polygon(kangas, (255, 200, 0), [(px+5, keski_y-2), (px+35, keski_y-2), (px+28, py+3), (px+12, py+3)])
                pygame.draw.line(kangas, (200, 150, 0), (px+5, keski_y-2), (px+35, keski_y-2), 2)
                
                sx, sy = pelaaja_suunta[0]*3, pelaaja_suunta[1]*3
                pygame.draw.circle(kangas, (255, 255, 255), (keski_x - 5 + sx, keski_y + 3 + sy), 4)
                pygame.draw.circle(kangas, (255, 255, 255), (keski_x + 5 + sx, keski_y + 3 + sy), 4)
                pygame.draw.circle(kangas, (0, 0, 0), (keski_x - 5 + sx*1.5, keski_y + 3 + sy*1.5), 2)
                pygame.draw.circle(kangas, (0, 0, 0), (keski_x + 5 + sx*1.5, keski_y + 3 + sy*1.5), 2)
                pygame.draw.circle(kangas, (255, 255, 200), (keski_x + sx, py + 8 + sy), 4)

    for v in viholliset:
        px, py = v.x * TILE_SIZE, v.y * TILE_SIZE
        keski_x, keski_y = px + 20, py + 20
        pulssi = (math.sin(aika / 100.0) + 1) / 2
        
        piirra_varjo(keski_x, keski_y)
        
        if v.tyyppi == 'H':
            vari = (150, 0, 150)
            piirra_valo(keski_x, keski_y, 60, 100, (100, 0, 100))
        else:
            vari = (200 + 55*pulssi, 0, 0)
            piirra_valo(keski_x, keski_y, 60, 100, (150, 0, 0))
            
        pygame.draw.circle(kangas, vari, (keski_x, keski_y), 13)
        
        kulma = aika / 200.0 if v.tyyppi == 'H' else -aika / 150.0
        for i in range(6):
            k = kulma + i * (math.pi / 3)
            terax = keski_x + math.cos(k) * 16
            teray = keski_y + math.sin(k) * 16
            pygame.draw.circle(kangas, (200, 200, 200), (terax, teray), 3)

        pygame.draw.polygon(kangas, (255, 255, 0), [(px+10, py+15), (px+16, py+18), (px+10, py+20)])
        pygame.draw.polygon(kangas, (255, 255, 0), [(px+30, py+15), (px+24, py+18), (px+30, py+20)])

    for p in partikkelit[:]:
        p['x'] += p['vx']; p['y'] += p['vy']; p['vy'] += 0.5; p['elama'] -= 1
        pygame.draw.circle(kangas, p['vari'], (int(p['x']), int(p['y'])), max(1, p['elama'] // 3))
        if p['elama'] <= 0: partikkelit.remove(p)

    kangas.blit(valo_kangas, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

    offset_x = random.randint(-ruudun_tarina, ruudun_tarina)
    offset_y = random.randint(-ruudun_tarina, ruudun_tarina)
    
    ruutu.fill((10, 10, 15))
    
    taso_teksti = fontti_ui.render(f"Taso: {nykyinen_kentta + 1}/12", True, (200, 200, 200))
    piste_teksti = fontti_ui.render(f"Pisteet: {pisteet}", True, (255, 215, 0))
    ruutu.blit(taso_teksti, (15, 10))
    ruutu.blit(piste_teksti, (WIDTH - piste_teksti.get_width() - 15, 10))
    
    if kuollut:
        fontti = pygame.font.SysFont(None, 48)
        t = fontti.render("KUOLIT!", True, (255, 50, 50))
        kangas.blit(t, (WIDTH//2 - t.get_width()//2, HEIGHT//2))
    elif peli_lapi:
        fontti = pygame.font.SysFont(None, 48)
        t = fontti.render("VOITIT PELIN!", True, (50, 255, 50))
        kangas.blit(t, (WIDTH//2 - t.get_width()//2, HEIGHT//2))

    ruutu.blit(kangas, (offset_x, offset_y + UI_HEIGHT))
    pygame.display.flip()