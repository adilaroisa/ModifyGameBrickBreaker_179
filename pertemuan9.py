import tkinter as tk


class ObjekGame:
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_koordinat(self):
        return self.canvas.coords(self.item)  # Mendapatkan koordinat objek di canvas.

    def gerak(self, x, y):
        self.canvas.move(self.item, x, y)  # Menggerakkan objek di canvas.

    def hapus(self):
        self.canvas.delete(self.item)  # Menghapus objek dari canvas.


class Bola(ObjekGame):
    def __init__(self, canvas, x, y, kecepatan):
        self.radius = 10  # Radius bola.
        self.arah = [1, -1]  # Arah gerakan bola (horizontal dan vertikal).
        self.kecepatan = kecepatan  # Kecepatan bola, akan meningkat per level.
        item = canvas.create_oval(
            x - self.radius, y - self.radius, x + self.radius, y + self.radius, fill='#FFDEE9'  # Warna bola lembut.
        )
        super().__init__(canvas, item)

    def update(self):
        koordinat = self.get_koordinat()
        lebar_canvas = self.canvas.winfo_width()
        # Memantulkan bola jika mencapai tepi layar (horizontal).
        if koordinat[0] <= 0 or koordinat[2] >= lebar_canvas:
            self.arah[0] *= -1
        # Memantulkan bola jika mencapai atas layar.
        if koordinat[1] <= 0:
            self.arah[1] *= -1
        x = self.arah[0] * self.kecepatan
        y = self.arah[1] * self.kecepatan
        self.gerak(x, y)

    def tabrakan(self, objek_game):
        koordinat = self.get_koordinat()
        x = (koordinat[0] + koordinat[2]) / 2
        if len(objek_game) > 1:  # Jika tabrakan dengan lebih dari satu objek, pantul vertikal.
            self.arah[1] *= -1
        elif len(objek_game) == 1:
            objek = objek_game[0]
            koordinat_objek = objek.get_koordinat()
            if x > koordinat_objek[2]:  # Bola di sisi kanan objek.
                self.arah[0] = 1
            elif x < koordinat_objek[0]:  # Bola di sisi kiri objek.
                self.arah[0] = -1
            else:
                self.arah[1] *= -1  # Bola memantul ke atas/bawah.
        for objek in objek_game:
            if isinstance(objek, Balok):
                objek.kena()  # Mengurangi pukulan balok.


class Pemukul(ObjekGame):
    def __init__(self, canvas, x, y):
        self.lebar = 80  # Lebar paddle.
        self.tinggi = 15  # Paddle lebih tebal.
        self.bola = None
        item = canvas.create_rectangle(
            x - self.lebar / 2,
            y - self.tinggi / 2,
            x + self.lebar / 2,
            y + self.tinggi / 2,
            fill='#1D4E89',  # Paddle berwarna biru tua.
        )
        super().__init__(canvas, item)

    def pasang_bola(self, bola):
        self.bola = bola  # Menghubungkan paddle dengan bola.

    def gerak(self, offset):
        koordinat = self.get_koordinat()
        lebar_canvas = self.canvas.winfo_width()
        if 0 <= koordinat[0] + offset and koordinat[2] + offset <= lebar_canvas:
            super().gerak(offset, 0)
            if self.bola:  # Jika bola terpasang, bola ikut bergerak.
                self.bola.gerak(offset, 0)


class Balok(ObjekGame):
    WARNA = {1: '#FDE2E4', 2: '#FAD2E1', 3: '#D8E2DC'}  # Warna balok berdasarkan pukulan tersisa.

    def __init__(self, canvas, x, y, pukulan):
        self.lebar = 75
        self.tinggi = 20
        self.pukulan = pukulan  # Jumlah pukulan yang diperlukan untuk menghancurkan balok.
        warna = Balok.WARNA[pukulan]
        item = canvas.create_rectangle(
            x - self.lebar / 2,
            y - self.tinggi / 2,
            x + self.lebar / 2,
            y + self.tinggi / 2,
            fill=warna,
            tags='balok',
        )
        super().__init__(canvas, item)

    def kena(self):
        self.pukulan -= 1  # Mengurangi jumlah pukulan saat terkena bola.
        if self.pukulan == 0:
            self.hapus()  # Menghapus balok jika pukulan habis.
        else:
            self.canvas.itemconfig(self.item, fill=Balok.WARNA[self.pukulan])


class Permainan(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.level = 1  # Level awal permainan.
        self.nyawa = 3  # Nyawa awal.
        self.lebar = 610
        self.tinggi = 400
        self.canvas = tk.Canvas(
            self, bg='#CBE8F6', width=self.lebar, height=self.tinggi  # Latar belakang biru muda.
        )
        self.canvas.pack()
        self.pack()

        self.objek = {}
        self.bola = None
        self.pemukul = Pemukul(self.canvas, self.lebar / 2, 350)
        self.objek[self.pemukul.item] = self.pemukul
        self.siapkan_level()
        self.info_nyawa = None
        self.info_level = None
        self.siapkan_game()
        self.canvas.focus_set()
        self.canvas.bind('<Left>', lambda _: self.pemukul.gerak(-10))  # Tombol panah kiri.
        self.canvas.bind('<Right>', lambda _: self.pemukul.gerak(10))  # Tombol panah kanan.

    def siapkan_level(self):
        # Menyiapkan balok untuk level saat ini.
        for x in range(5, self.lebar - 5, 75):
            self.tambah_balok(x + 37.5, 50, 3)
            self.tambah_balok(x + 37.5, 70, 2)
            self.tambah_balok(x + 37.5, 90, 1)

    def siapkan_game(self):
        self.tambah_bola()
        self.update_teks_nyawa()
        self.update_teks_level()
        self.teks_awal = self.tulis_teks(
            self.lebar / 2, self.tinggi / 2, 'Tekan Spasi untuk Mulai', 20
        )
        self.canvas.bind('<space>', lambda _: self.mulai_game())

    def tambah_bola(self):
        if self.bola:
            self.bola.hapus()
        koordinat_pemukul = self.pemukul.get_koordinat()
        x = (koordinat_pemukul[0] + koordinat_pemukul[2]) / 2
        self.bola = Bola(self.canvas, x, 320, kecepatan=4 + self.level)  # Kecepatan bola meningkat tiap level.
        self.pemukul.pasang_bola(self.bola)

    def tambah_balok(self, x, y, pukulan):
        balok = Balok(self.canvas, x, y, pukulan)
        self.objek[balok.item] = balok

    def tulis_teks(self, x, y, teks, ukuran='40'):
        font = ('Arial', ukuran)
        return self.canvas.create_text(x, y, text=teks, font=font)

    def update_teks_nyawa(self):
        teks = f'Nyawa: {self.nyawa}'
        if not self.info_nyawa:
            self.info_nyawa = self.tulis_teks(50, 20, teks, 15)
        else:
            self.canvas.itemconfig(self.info_nyawa, text=teks)

    def update_teks_level(self):
        teks = f'Level: {self.level}'
        if not self.info_level:
            self.info_level = self.tulis_teks(self.lebar - 70, 20, teks, 15)
        else:
            self.canvas.itemconfig(self.info_level, text=teks)

    def mulai_game(self):
        self.canvas.unbind('<space>')
        self.canvas.delete(self.teks_awal)
        self.pemukul.bola = None
        self.loop_game()

    def loop_game(self):
        self.cek_tabrakan()
        if not self.canvas.find_withtag('balok'):  # Jika semua balok hancur.
            self.level += 1
            self.canvas.delete('all')  # Reset canvas.
            self.objek = {}
            self.pemukul = Pemukul(self.canvas, self.lebar / 2, 350)
            self.objek[self.pemukul.item] = self.pemukul
            self.siapkan_level()
            self.siapkan_game()
        elif self.bola.get_koordinat()[3] >= self.tinggi:  # Jika bola jatuh ke bawah.
            self.nyawa -= 1
            if self.nyawa < 0:
                self.tulis_teks(self.lebar / 2, self.tinggi / 2, 'Game Over', 30)
            else:
                self.siapkan_game()
        else:
            self.bola.update()
            self.after(50, self.loop_game)

    def cek_tabrakan(self):
        koordinat_bola = self.bola.get_koordinat()
        objek = self.canvas.find_overlapping(*koordinat_bola)
        objek_game = [self.objek[x] for x in objek if x in self.objek]
        self.bola.tabrakan(objek_game)


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Brick Breaker - Level Edition')
    permainan = Permainan(root)
    permainan.mainloop()
