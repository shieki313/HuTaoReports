#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
import io
import PIL


class Status:
    def __init__(self):
        super().__init__()

    def graphCheck(self, arrayx, arrayy, pointx, pointy):
        checker = False
        for i in range(arrayx.size):
            if pointx <= arrayx[i]:
                if pointy >= arrayy[i]:
                    checker = True
        return checker

    def HPGraph(self, baseHP, HP, ATK, Crnow, Cdnow, weapon, skillLV, filename):
        Cr = np.arange(30.0, 100.1, 0.1)
        print(baseHP, HP, ATK, Crnow, Cdnow)

        # サブステータスの比率を記載
        crper = 2.0
        cdper = 4.0
        hpper = 3.0
        atkper = 3.0

        # weaponbuff = [1.8, 2.2, 2.6, 3.0, 3.4, 0.0]
        # 護摩のバフ量とスキルLVを指定(護摩でないときは5番を指定)
        weaponbuff = [1.8, 2.2, 2.6, 3.0, 3.4, 0.0]
        skillbuff = [0.0, 3.84, 4.07, 4.30, 4.60, 4.83, 5.06, 5.36, 5.66, 5.96, 6.26, 6.56, 6.85, 7.15]

        Skillbuffper = skillbuff[int(skillLV)] + weaponbuff[int(weapon)]

        # 攻撃力表示
        BuffedATK = ATK + HP * (Skillbuffper * 0.01)

        # 3Dプロット用設定
        X = Cr
        Y = BuffedATK

        # Cd(cr)の関数(多分)
        Cd2_3 = (Y * cdper * 0.01) / (baseHP * hpper * 0.01 * (Skillbuffper * 0.01)) - \
              (1 / (X * 0.01))  # 夜蘭用ステータス

        # Cr(cd)の関数(多分)をCd(cr)に直したもの
        Cddash3 = 1 / ((Y * crper * 0.01) / (baseHP * hpper * 0.01 * (Skillbuffper * 0.01)) - (X * 0.01))  # 夜蘭用ステータス

        Cd2_3 = Cd2_3 * 100
        Cddash3 = Cddash3 * 100

        Cd2_3alt = np.zeros(Cd2_3.size)
        Cd2_3alt2 = np.zeros(Cd2_3.size)

        # 数値の発散を抑制する関数
        test = Cddash3.size
        for j in range(test):
            if Cddash3[j] < 0:
                Cddash3[j] = 10000
                j += 1

        i = 0
        for c in Cd2_3:
            if c > Cddash3[i]:
                Cd2_3alt[i] = Cddash3[i]
                Cd2_3alt2[i] = Cd2_3[i]
            else:
                Cd2_3alt[i] = Cd2_3[i]
                Cd2_3alt2[i] = Cddash3[i]
            i += 1


        # print(self.graphCheck(X, Cd2_3alt2, Crnow, Cdnow))
        # print(self.graphCheck(X, Cd2_3alt, Crnow, Cdnow))
        if Crnow >= 100.0:
            over100 = True
            Crnowalt = 100.0
        else:
            Crnowalt = Crnow
            over100 = False
        Crline = self.graphCheck(X, Cddash3, Crnowalt, Cdnow)
        Cdline = self.graphCheck(X, Cd2_3, Crnowalt, Cdnow)
        # print(Crline)
        # print(Cdline)

        self.hpfull = False
        for i in range(Cd2_3alt.size):
            if Cd2_3alt2[i] == Cd2_3[i]:
                self.hpfull = True

        self.substatus = "判定失敗"
        if Crline == True:
            if Cdline == True:
                # print("会心率不足")
                self.substatus = "会心率不足 ダメ < HP < 率"
            else:
                # print("HP充分")
                self.substatus = "HP充分 HP < 会心系"
        else:
            if Cdline == True:
                # print("HP不足")
                self.substatus = "HP不足 会心系 < HP"
            else:
                # print("会心ダメージ不足")
                self.substatus = "会心ダメージ不足 率 < HP < ダメ"
        if over100:
            if Cdline == True:
                # print("会心率不足")
                self.substatus = "会心MAX HP不足 ダメ < HP"
            else:
                # print("HP充分")
                self.substatus = "会心MAX HP充分 HP < 会心ダメ"

        # グラフ設定
        # plt.plot(X, Cd1)
        # plt.plot(X, Cd2)
        # plt.plot(X, Cd2_2)
        # plt.plot(X, Cd2_3)
        # plt.plot(X, X*2)
        # plt.plot(X, Cddash)
        # plt.plot(X, Cd2_3)
        # plt.fill_between(X, Cd2, color="lightblue")
        # plt.fill_between(X, Cd2, color="m", alpha=0.3)
        # plt.fill_between(X, Cddash, 1000, color="g", alpha=0.3)
        # plt.fill_between(X, Cd2, Cddash, color="c", alpha=0.3)
        # plt.fill_between(X, Cd2_2, color="m", alpha=0.3)
        # plt.fill_between(X, Cddash2, 1000, color="g", alpha=0.3)
        # plt.fill_between(X, Cd2_2, Cddash2, color="c", alpha=0.3)
        color = '#e41a1c'
        plt.fill_between(X, Cd2_3alt, color="m", alpha=0.3)
        plt.fill_between(X, Cd2_3alt2, 1000, color="g", alpha=0.3)
        plt.fill_between(X, Cd2_3alt, Cddash3, color="c", alpha=0.3)
        plt.fill_between(X, Cd2_3alt, Cd2_3, color="y", alpha=0.3)
        # plt.fill_between(X, Cd2_3, 300, color="red", alpha=0.5)
        # plt.plot(X, X*2)
        plt.text(65, 20, "会心ダメ不足", fontname="MS Gothic", size=24)
        plt.text(35, 250, "会心率不足", fontname="MS Gothic", size=24)
        plt.text(30, 60, "HP不足", fontname="MS Gothic", size=24)
        # plt.text(70, 160, "HP不足", fontname="MS Gothic", size=24)
        if self.hpfull:
            plt.text(70, 170, "HP充分", fontname="MS Gothic", size=24)

        plt.xlabel("会心率 (％)", fontname="MS Gothic", size=16)
        plt.ylabel("会心ダメージ (％)", fontname="MS Gothic", size=16)
        plt.title('胡桃 スキルLV{2:.0f} HP {0:.0f} スキル時攻撃力 {1:.0f}'.format(HP, BuffedATK, skillLV), fontname="MS Gothic", size=16)
        if Crnow < 65:
            loc = (0.6, 0.75)
        else:
            loc = (0.05, 0.4)
        plt.legend(["会心ダメージ不足", "会心率不足", "HP不足", "HP充分"], prop={"family":"MS Gothic"}, loc=loc)
        plt.plot(X, X * 2)
        plt.grid()
        plt.ylim(0, 300)
        plt.plot(Crnow, Cdnow, marker='.', color="r", markersize=15)

        filepath = filename + ".png"
        plt.savefig(filepath)

        # PILに変換する
        print(BuffedATK*(1+Crnow+Cdnow))
        buf = io.BytesIO() # bufferを用意
        plt.savefig(buf, format='png') # bufferに保持
        buf.seek(0) # バッファの先頭に移動
        img2=PIL.Image.open(buf).convert('RGB') # RGBAになるので変換
        print(type(img2))    # <class 'PIL.Image.Image'>
        print(img2.mode)     # RGB
        print(img2.size)     # (400, 300)

        plt.clf()

        return img2

    def EmGraph(self, baseHP, HP, ATK, Crnow, Cdnow, weapon, skillLV, Em, CWornot, f, filename):
        Cr = np.arange(30.0, 100.1, 0.1)
        print(baseHP, HP, ATK, Crnow, Cdnow)

        # サブステータスの比率を記載
        crper = 2.0
        cdper = 4.0
        hpper = 3.0
        atkper = 3.0

        # weaponbuff = [1.8, 2.2, 2.6, 3.0, 3.4, 0.0]
        # 護摩のバフ量とスキルLVを指定(護摩でないときは5番を指定)
        weaponbuff = [1.8, 2.2, 2.6, 3.0, 3.4, 0.0]
        skillbuff = [0.0, 3.84, 4.07, 4.30, 4.60, 4.83, 5.06, 5.36, 5.66, 5.96, 6.26, 6.56, 6.85, 7.15]
        print(f'スキルダメージ量：{skillbuff[int(skillLV)]}')
        print(f'武器ダメージ量：{weaponbuff[int(weapon)]}')

        Skillbuffper = skillbuff[int(skillLV)] + weaponbuff[int(weapon)]

        # 攻撃力表示
        BuffedATK = ATK + HP * (Skillbuffper * 0.01)
        print(f'攻撃力：{BuffedATK}')

        # 3Dプロット用設定
        X = Cr
        Y = BuffedATK

        # 火魔女用の係数
        CW = 0.0
        if CWornot == True:
            CW = 0.15

        # Cd(cr)の関数(多分)
        Cd2_3 = (-450*((-139*Em)/(50.*(1400 + Em)*(1400 + Em)) + 139/(50.*(1400 + Em)))*f +
                 (Cr/100)*(1 + f/2. + (3*(CW + (139*Em)/(50.*(1400 + Em)))*f)/2.))/(450.*(Cr/100)*((-139*Em)/(50.*(1400 + Em)*(1400 + Em)) +
                139/(50.*(1400 + Em)))*f)  # 夜蘭用ステータス

        # Cr(cd)の関数(多分)をCd(cr)に直したもの
        Cddash3 = (-450*((-139*Em)/(50.*(1400 + Em)*(1400 + Em)) +
                    139/(50.*(1400 + Em)))*f)/(450*(Cr/100)*((-139*Em)/(50.*(1400 + Em)*(1400 + Em)) +
                    139/(50.*(1400 + Em)))*f + (-1 - f/2. - (3*(CW + (139*Em)/(50.*(1400 + Em)))*f)/2.)/2.)

        Cd2_3 = Cd2_3 * 100
        Cddash3 = Cddash3 * 100

        Cd2_3alt = np.zeros(Cd2_3.size)
        Cd2_3alt2 = np.zeros(Cd2_3.size)

        # 数値の発散を抑制する関数
        test = Cddash3.size
        for j in range(test):
            if Cddash3[j] < 0:
                Cddash3[j] = 10000
                j += 1

        i = 0
        for c in Cd2_3:
            if c > Cddash3[i]:
                Cd2_3alt[i] = Cddash3[i]
                Cd2_3alt2[i] = Cd2_3[i]
            else:
                Cd2_3alt[i] = Cd2_3[i]
                Cd2_3alt2[i] = Cddash3[i]
            i += 1

        if Crnow >= 100.0:
            over100 = True
            Crnowalt = 100.0
        else:
            Crnowalt = Crnow
            over100 = False
        Crline = self.graphCheck(X, Cddash3, Crnowalt, Cdnow)
        Cdline = self.graphCheck(X, Cd2_3, Crnowalt, Cdnow)
        # print(Crline)
        # print(Cdline)

        self.hpfull = False
        for i in range(Cd2_3alt.size):
            if Cd2_3alt2[i] == Cd2_3[i]:
                self.hpfull = True

        self.substatus = "判定失敗"
        if Crline == True:
            if Cdline == True:
                # print("会心率不足")
                self.substatus = "会心率不足 ダメ < 熟知 < 率"
            else:
                # print("HP充分")
                self.substatus = "熟知充分 熟知 < 会心系"
        else:
            if Cdline == True:
                # print("HP不足")
                self.substatus = "熟知不足 会心系 < 熟知"
            else:
                # print("会心ダメージ不足")
                self.substatus = "会心ダメージ不足 率 < 熟知 < ダメ"
        if over100:
            if Cdline == True:
                # print("会心率不足")
                self.substatus = "会心MAX 熟知不足 ダメ < 熟知"
            else:
                # print("HP充分")
                self.substatus = "会心MAX 熟知充分 熟知 < 会心ダメ"

        # グラフ設定
        color = '#e41a1c'
        plt.fill_between(X, Cd2_3alt, color="m", alpha=0.3)
        plt.fill_between(X, Cd2_3alt2, 1000, color="g", alpha=0.3)
        plt.fill_between(X, Cd2_3alt, Cddash3, color="c", alpha=0.3)
        plt.fill_between(X, Cd2_3alt, Cd2_3, color="y", alpha=0.3)
        # plt.fill_between(X, Cd2_3, 300, color="red", alpha=0.5)
        # plt.plot(X, X*2)
        plt.text(65, 20, "会心ダメ不足", fontname="MS Gothic", size=24)
        plt.text(35, 250, "会心率不足", fontname="MS Gothic", size=24)
        plt.text(30, 60, "熟知不足", fontname="MS Gothic", size=24)
        # plt.text(70, 160, "HP不足", fontname="MS Gothic", size=24)
        if self.hpfull:
            plt.text(70, 170, "熟知充分", fontname="MS Gothic", size=24)

        plt.xlabel("会心率 (％)", fontname="MS Gothic", size=16)
        plt.ylabel("会心ダメージ (％)", fontname="MS Gothic", size=16)
        plt.title('胡桃 スキルLV{2:.0f} 熟知 {0:.0f} スキル時攻撃力 {1:.0f}'.format(Em, BuffedATK, skillLV), fontname="MS Gothic", size=16)
        if Crnow < 65:
            loc = (0.6, 0.75)
        else:
            loc = (0.05, 0.4)
        plt.legend(["会心ダメージ不足", "会心率不足", "熟知不足", "熟知充分"], prop={"family":"MS Gothic"}, loc=loc)
        plt.plot(X, X * 2)
        plt.grid()
        plt.ylim(0, 300)
        plt.plot(Crnow, Cdnow, marker='.', color="r", markersize=15)

        # filepath = filename + ".png"
        # plt.savefig(filepath)

        # PILに変換する
        buf = io.BytesIO() # bufferを用意
        plt.savefig(buf, format='png') # bufferに保持
        buf.seek(0) # バッファの先頭に移動
        img2=PIL.Image.open(buf).convert('RGB') # RGBAになるので変換

        plt.clf()

        return img2

x = Status()
# x.HPGraph(100.0, np.arange(150.0, 450.0, 0.1))
# x.CdGraph(np.arange(150, 350.0, 0.1))
# x.ChargeGraph(np.arange(3500.0, 5500.0, 1.))

"""
img = x.HPGraph(14459, 14459+20899, 707+443, 65.3, 228.4, 0, 8, "a")
print(x.substatus)
img.show()
img2 = x.EmGraph(14459, 14459+19393, 707+410, 68.4, 233.8, 0, 8, 200, True, 0.82, "b")
img2.show()
print(x.substatus)
"""
