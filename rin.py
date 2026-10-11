
import math
import random
import tkinter.font as tkfont
import turtle

# --- Turli tillardagi "Seni sevaman" -----------------------------------------
SOZLAR = [
    "Men seni sevaman",      # o'zbekcha
    "Seni sevaman",          # o'zbekcha
    "Мен сени севаман",      # o'zbekcha (kirill)
    "I love you",            # inglizcha
    "Te amo",                # ispancha
    "Ich liebe dich",        # nemischa
    "Je t'aime",             # fransuzcha
    "Ti amo",                # italyancha
    "Eu te amo",             # portugalcha
    "Я тебя люблю",          # ruscha
    "Seni seviyorum",        # turkcha
    "Ik hou van je",         # gollandcha
    "Jag älskar dig",        # shvedcha
    "Kocham cię",            # polyakcha
    "我爱你",                 # xitoycha
    "愛してる",               # yaponcha
    "사랑해",                 # koreyscha
]

# Yurakning o'lchamlari (parametrik formulada ~32 x 30 birlik)
BIRLIK_KENGLIK = 32.0
BIRLIK_BALANDLIK = 30.0


def yurak_nuqtalari(olcham, qadam=0.01):
    """Yurak konturi nuqtalari (parametrik tenglama), markazga keltirilgan."""
    nuqtalar = []
    t = 0.0
    while t < 2 * math.pi:
        x = 16 * math.sin(t) ** 3
        y = (13 * math.cos(t) - 5 * math.cos(2 * t)
             - 2 * math.cos(3 * t) - math.cos(4 * t))
        nuqtalar.append((x * olcham, y * olcham))
        t += qadam
    ys = [p[1] for p in nuqtalar]
    oy = (min(ys) + max(ys)) / 2
    return [(x, y - oy) for x, y in nuqtalar]


def kesishmalar(kontur, y):
    """Gorizontal chiziq (y) yurak ichida qoladigan [x1, x2] oraliqlari."""
    xlar = []
    n = len(kontur)
    for i in range(n):
        x1, y1 = kontur[i]
        x2, y2 = kontur[(i + 1) % n]
        if (y1 <= y < y2) or (y2 <= y < y1):
            xlar.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
    xlar.sort()
    return list(zip(xlar[0::2], xlar[1::2]))


def rang_olish(t):
    """t: 0 (pastki uch) -> 1 (tepa). Qizildan pushti-oqqa o'tuvchi rang."""
    g = int(40 + 150 * t + random.randint(-18, 18))
    b = int(70 + 130 * t + random.randint(-18, 18))
    g = max(0, min(255, g))
    b = max(0, min(255, b))
    return (255, g, b)


class YurakChizuvchi:
    def __init__(self):
        self.ekran = turtle.Screen()
        self.ekran.setup(width=0.8, height=0.85)   # ekranning 80% x 85% qismi
        self.ekran.bgcolor("black")
        self.ekran.title("Men seni sevaman")
        self.ekran.colormode(255)
        self.ekran.tracer(0)

        self.kanvas = self.ekran.getcanvas()
        self.root = self.kanvas.winfo_toplevel()

        self.qalam = turtle.Turtle(visible=False)
        self.qalam.penup()

        self.chizish_id = 0          # eski animatsiyani to'xtatish uchun
        self.kutish = None           # oyna o'lchami o'zgarganda kechiktirish
        self.oxirgi_olcham = (0, 0)

        self.root.bind("<Configure>", self.oyna_ozgardi)
        self.ekran.ontimer(lambda: self.chizish(animatsiya=True), 200)

    # -- Responsive: oyna o'lchami o'zgarganda qayta chizish -------------------
    def oyna_ozgardi(self, hodisa):
        if hodisa.widget is not self.root:
            return
        olcham = (hodisa.width, hodisa.height)
        if olcham == self.oxirgi_olcham:
            return
        self.oxirgi_olcham = olcham
        if self.kutish is not None:
            self.root.after_cancel(self.kutish)
        self.kutish = self.root.after(200, lambda: self.chizish(animatsiya=False))

    # -- Asosiy chizish -----------------------------------------------------------
    def chizish(self, animatsiya):
        self.chizish_id += 1
        mening_id = self.chizish_id

        eni = self.kanvas.winfo_width()
        boyi = self.kanvas.winfo_height()
        if eni < 120 or boyi < 120:
            return

        # Aylanma (scroll) chiziqlari chiqmasligi uchun kanvasni oynaga moslash
        self.ekran.screensize(max(eni - 8, 100), max(boyi - 8, 100))
        self.qalam.clear()
        random.seed(7)               # har safar bir xil joylashuv

        # Yurak o'lchami oyna eni va bo'yiga qarab hisoblanadi
        olcham = min(eni * 0.88 / BIRLIK_KENGLIK, boyi * 0.76 / BIRLIK_BALANDLIK)
        siljish = boyi * 0.05        # pastda yozuvga joy qoldirish
        kontur = [(x, y + siljish) for x, y in yurak_nuqtalari(olcham)]
        ys = [p[1] for p in kontur]
        y_min, y_max = min(ys), max(ys)

        shrift_olchami = max(5, int(olcham * 0.6))
        shrift = ("Arial", shrift_olchami, "bold")
        olchagich = tkfont.Font(root=self.root, family="Arial",
                                size=shrift_olchami, weight="bold")
        ascent = olchagich.metrics("ascent")
        qator_balandligi = olchagich.metrics("linespace") + 1
        oraliq = max(6, int(shrift_olchami * 1.2))     # so'zlar orasidagi bo'shliq
        chekka = max(3, int(olcham * 0.45))            # kontur ichidagi bo'shliq
        kenglik_keshi = {}

        def kenglik(soz):
            if soz not in kenglik_keshi:
                kenglik_keshi[soz] = olchagich.measure(soz)
            return kenglik_keshi[soz]

        def qator_tuzish(uzunlik):
            tanlangan, jami, urinish, oxirgi = [], 0, 0, None
            while urinish < 10:
                soz = random.choice(SOZLAR)
                w = kenglik(soz)
                kerak = w + (oraliq if tanlangan else 0)
                if soz != oxirgi and jami + kerak <= uzunlik:
                    tanlangan.append((soz, w))
                    jami += kerak
                    oxirgi = soz
                    urinish = 0
                else:
                    urinish += 1
            return tanlangan, jami

        # Barcha qatorlarni oldindan hisoblaymiz: [(y, rang, [(soz, x), ...]), ...]
        qatorlar = []
        y = y_min + 2
        while y + ascent < y_max:
            for x1, x2 in kesishmalar(kontur, y + ascent / 2):
                boshi, oxiri = x1 + chekka, x2 - chekka
                if oxiri - boshi < 20:
                    continue
                tanlangan, jami = qator_tuzish(oxiri - boshi)
                if not tanlangan:
                    continue
                x = boshi + (oxiri - boshi - jami) / 2        # markazlashtirish
                t = (y - y_min) / (y_max - y_min)
                soz_joylari = []
                for soz, w in tanlangan:
                    soz_joylari.append((soz, x, rang_olish(t)))
                    x += w + oraliq
                qatorlar.append((y, soz_joylari))
            y += qator_balandligi

        def qator_yozish(qator):
            qy, soz_joylari = qator
            for soz, qx, rang in soz_joylari:
                self.qalam.goto(qx, qy)
                self.qalam.pencolor(rang)
                self.qalam.write(soz, font=shrift)

        def kontur_va_yozuv():
            self.qalam.pensize(max(2, olcham / 5))
            self.qalam.pencolor(255, 45, 85)
            self.qalam.penup()
            self.qalam.goto(kontur[0])
            self.qalam.pendown()
            for nuqta in kontur:
                self.qalam.goto(nuqta)
            self.qalam.goto(kontur[0])
            self.qalam.penup()

            yozuv_olchami = max(10, int(olcham * 1.1))
            self.qalam.goto(0, -boyi / 2 + boyi * 0.05)
            self.qalam.pencolor(255, 200, 215)
            self.qalam.write("Men seni sevaman", align="center",
                             font=("Georgia", yozuv_olchami, "italic"))
            self.ekran.update()

        if not animatsiya:
            for qator in qatorlar:
                qator_yozish(qator)
            kontur_va_yozuv()
        else:
            self.animatsiya_qadami(mening_id, qatorlar, 0,
                                   qator_yozish, kontur_va_yozuv)

    def animatsiya_qadami(self, mening_id, qatorlar, i, qator_yozish, tugatish):
        """Qatorlarni birin-ketin chizadi (oyna o'zgarsa to'xtaydi)."""
        if mening_id != self.chizish_id:
            return
        if i < len(qatorlar):
            qator_yozish(qatorlar[i])
            self.ekran.update()
            self.ekran.ontimer(
                lambda: self.animatsiya_qadami(mening_id, qatorlar, i + 1,
                                               qator_yozish, tugatish), 90)
        else:
            tugatish()


def main():
    YurakChizuvchi()
    turtle.mainloop()


if __name__ == "__main__":
    main()
