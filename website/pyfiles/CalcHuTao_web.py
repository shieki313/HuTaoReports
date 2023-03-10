import os
import tkinter
import numpy as np
import time
import tkinter.filedialog
import threading
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import csv
from scipy.optimize import minimize

Normalfilepath = 'media/csv/胡桃通常天賦.csv'
Skillfilepath = 'media/csv/胡桃スキル天賦.csv'
Burstfilepath = 'media/csv/胡桃爆発天賦.csv'


class Status:
    def __init__(self, Baselist = [15552, 106, 876, 0.384], Pluslist=[0, 0.0, 0, 0.0, 0, 0.0, 0.05, 0.5, 0, 100.0, 0.0], skillLV=[1,1,1], constellation=1, Weaponlist=[608, 1], artifact=[False], buffs=[0.0, 0.0, 0.0, 0.0, 0.0], debuffs=[0.0,0.0]):
        super().__init__()

        # ここに書いてあることは一度だけ実行される
        # Base
        self.BaseHP = Baselist[0]
        self.BaseATKC = Baselist[1]
        self.BaseDEF = Baselist[2]
        self.SpStat = Baselist[3]  # CritDMG%
        # self.BaseCr = 5.0
        # self.BaseCd = 50.0
        # self.BaseEm = 0
        # self.BaseEr = 100.0

        # Added Status
        self.HP = Pluslist[0]
        self.HPper = Pluslist[1]
        self.ATK = Pluslist[2]
        self.ATKper = Pluslist[3]
        self.DEF = Pluslist[4]
        self.DEFper = Pluslist[5]
        self.Cr = Pluslist[6]
        self.Cd = Pluslist[7] + self.SpStat
        self.Em = Pluslist[8]
        self.Er = Pluslist[9]
        self.EmBuff = Pluslist[10]
        self.list = [self.HP, self.HPper, self.ATK, self.ATKper, self.DEF, self.DEFper, self.Cr, self.Cd, self.Em,
                     self.Er, self.EmBuff]

        # Weapon
        self.HPper += 0  # 16.0

        # 聖遺物
        self.CW = artifact[0]

        with open(Normalfilepath) as f:
            reader = csv.DictReader(f)
            Normals = [row for row in reader]
        with open(Skillfilepath) as f:
            reader = csv.DictReader(f)
            Skills = [row for row in reader]
        with open(Burstfilepath) as f:
            reader = csv.DictReader(f)
            Bursts = [row for row in reader]
        self.Normaldmgper = Normals[skillLV[0]-1]
        self.Skilldmgper = Skills[skillLV[1]-1]
        self.Burstdmgper = Bursts[skillLV[2]-1]

        homaR = 5  # 非護摩は5番
        self.skillbuffper = float(Skills[skillLV[1]-1]['S_Buff'])
        if Weaponlist[0] == 13501:
            self.skillbuffper += 0.014 + 0.004*Weaponlist[1]
            homaR = Weaponlist[1] - 1

        self.C6 = False
        if constellation == 6:
            self.C6 = True

        self.f = 0.82  # 蒸発率


        # 攻撃力
        Attack = self.BaseATKC*(self.ATKper+1) + self.ATK + self.skillbuffper*(self.BaseHP*(self.HPper+1) + self.HP)
        # 換算HP
        ConvertedHP = (self.BaseATKC*(self.ATKper+1) + self.ATK)/self.skillbuffper + (self.BaseHP*(self.HPper+1) + self.HP)
        ConvertedHPper = (ConvertedHP/self.BaseHP - 1)

        self.DamageIndicator = self.damageIndication(self.list[0],self.list[1],self.list[2],self.list[3],self.list[4],
                                                     self.list[5],self.list[6],self.list[7],self.list[8],self.list[9],
                                                     self.list[10])

        self.status = [self.BaseATKC*(self.ATKper+1) + self.ATK, self.BaseHP*(self.HPper+1) + self.HP, Attack,
                       ConvertedHP, ConvertedHPper, self.Cr, self.Cd, self.Em, self.EmBuff]
        self.status_forGraph = [self.BaseHP, self.BaseHP*(self.HPper+1) + self.HP,
                                self.BaseATKC*(self.ATKper+1) + self.ATK, self.Cr*100, self.Cd*100, homaR, skillLV[1]]

        self.damageIndicate = self.damageCalcindicator(*self.list, buffs)
        self.DMGsDict = self.damageCalc(self.damageIndicate)


    def idealScore(self, indication=8510.414912, baselist=[]):
        # 予め加算しておく部分
        # 武器
        # 目的関数
        def objective_fnc(x):
            Cd = x[0]
            Cr = x[1]
            hpper = x[2]
            em = x[3]
            return ((4 * hpper) / 3. + Cd + 2 * Cr + em / 300) * 100

        # 等式制約条件
        def equality_constraint(x):
            Cd = x[0]
            Cr = x[1]
            hpper = x[2]
            em = x[3]

            l = np.array([0.0, hpper, 0.0, 0.0, 0.0, 0.0, Cr, Cd, em, 0.0, 0.0]) + np.array(baselist)

            return self.damageIndication(*l) + -indication
            # return (self.BaseATKC*(self.ATKper+1) + self.ATK + 0.0806*(self.BaseHP*(hpper+1) + self.HP) * (1 + Cd * Cr)) + -indication

        bounds_Cd = (0.0, 5.0)
        bounds_Cr = (0.00, 1.0-(baselist[6]))
        bounds_atk = (0.0, 10.0)
        bounds_em = (0.0, 1200)

        bounds = [bounds_Cd, bounds_Cr, bounds_atk, bounds_em]

        constraint1 = {"type": "eq", "fun": equality_constraint}
        # constraint2={"type":"ineq","fun":inequality_constraint}
        # constraint=[constraint1,constraint2]
        constraint = constraint1

        x0 = [0.1, 0.3, 1.0, 80]

        result = minimize(objective_fnc, x0, method="SLSQP", bounds=bounds, constraints=constraint)
        return result.fun

    # ダメージ指標の定義
    def damageIndication(self, HP, HPper, ATK, ATKper, DEF, DEFper, Cr, Cd, Em, Er, EmBuff):
        # 攻撃力
        Attack = self.BaseATKC*(ATKper+1) + ATK + self.skillbuffper*(self.BaseHP*(HPper+1) + HP)
        # 換算HP
        ConvertedHP = (self.BaseATKC*(ATKper+1) + ATK)/self.skillbuffper + (self.BaseHP*(HPper+1) + HP)
        ConvertedHPper = (ConvertedHP/self.BaseHP - 1)
        # 攻撃倍率
        Magnification = 1.0
        # 会心期待値
        EofCritical = Cr*Cd+1
        EofCritical_C6 = (3+2*Cr*Cd+Cd)/3
        EofCritical_C6_2 = (2+Cr*Cd+Cd)/2
        if self.C6 == True:
            EofCritical = (3+2*Cr*Cd+Cd)/3
        # ダメージバフ
        DMGBuff = (EmBuff+1)
        # 蒸発・溶解ボーナス(蒸発率あり)
        CW = 0.0  # 火魔女用変数
        if self.CW == True:
            CW = 0.15
        EMBonus = 1.5*(CW + 2.78 * Em / (Em + 1400))*self.f + 0.5*self.f + 1
        # 防御補正
        DEFMul = 0.5
        # 元素耐性補正
        RESMul = 0.9
        DamageIndicator = Attack*Magnification*EofCritical*DMGBuff*EMBonus*DEFMul*RESMul

        return DamageIndicator

    def damageCalcindicator(self, HP, HPper, ATK, ATKper, DEF, DEFper, Cr, Cd, Em, Er, EmBuff, buffs=[0.0, 0.0, 0.0, 0.0, 0.0], Def=0.5, Res=0.9):
        # 攻撃力
        Attack = self.BaseATKC*(ATKper+1) + ATK + self.skillbuffper*(self.BaseHP*(HPper+1) + HP)
        # 換算HP
        ConvertedHP = (self.BaseATKC*(ATKper+1) + ATK)/self.skillbuffper + (self.BaseHP*(HPper+1) + HP)
        ConvertedHPper = (ConvertedHP/self.BaseHP - 1)
        # 攻撃倍率
        Magnification = 1.0
        # 会心期待値
        EofCritical = Cr*Cd+1
        EofCritical_C6 = (3+2*Cr*Cd+Cd)/3
        EofCritical_C6_2 = (2+Cr*Cd+Cd)/2
        if self.C6 == True:
            EofCritical = (3+2*Cr*Cd+Cd)/3
        # ダメージバフ
        DMGBuff = (EmBuff+1) + np.array(buffs)
        # 蒸発・溶解ボーナス(蒸発率あり)
        CW = 0.0  # 火魔女用変数
        if self.CW == True:
            CW = 0.15
        EofEMBonus = 1.5*(CW + 2.78 * Em / (Em + 1400))*self.f + 0.5*self.f + 1
        EmBonus = 1.5*(1 + CW + 2.78 * Em / (Em + 1400))
        # 防御補正
        DEFMul = 0.5
        # 元素耐性補正
        RESMul = 0.9
        DamageIndicator = Attack*Magnification*EofCritical*DMGBuff*EofEMBonus*DEFMul*RESMul
        DamageBase = Attack*Magnification*DMGBuff*DEFMul*RESMul  # 非会心かつ非蒸発

        Data = {'Indicator': DamageIndicator, 'DamageBase': DamageBase, 'EofCritical': EofCritical,
                'Critical': (Cd+1), 'EofVape': EofEMBonus, 'Vape': EmBonus}

        return Data

    def damageCalc(self, indicator={'Indicator': ([12990.7117578, 12990.7117578,  8660.4745052,  8660.4745052,
        8660.4745052]), 'DamageBase': ([2236.880016, 2236.880016, 1491.253344, 1491.253344, 1491.253344]), 'EofCritical': 3.2272, 'Critical': 3.784, 'EofVape': 1.7995518987341772, 'Vape': 1.9750632911392405}):

        def damagearray(id, num, dmgper):
            allDMG = {'id': id, 'E': indicator['Indicator'][num] * dmgper, 'NN': indicator['DamageBase'][num] * dmgper,
                      'CN': indicator['DamageBase'][num] * indicator['Critical'] * dmgper,
                      'NV': indicator['DamageBase'][num] * indicator['Vape'] * dmgper,
                      'CV': indicator['DamageBase'][num] * indicator['Critical'] * indicator['Vape'] * dmgper}
            return allDMG

        DMGs = [0] * (len(self.Normaldmgper)+2)
        for count, id in enumerate(list(self.Normaldmgper.keys())):
            if 'N' in id:
                data = damagearray(id, 0, float(self.Normaldmgper[id]))
            elif 'C' in id:
                data = damagearray(id, 1, float(self.Normaldmgper[id]))
            elif 'F' in id:
                data = damagearray(id, 2, float(self.Normaldmgper[id]))
            DMGs[count] = data

        DMGs[len(self.Normaldmgper)] = damagearray('S', 3, float(self.Skilldmgper['S']))
        DMGs[len(self.Normaldmgper)+1] = damagearray('B_LHP', 3, float(self.Burstdmgper['B_LHP']))
        return DMGs





# x = Status([15552, 715, 876, 0.384], [4600, 0.60, 311, 0.0, 0, 0.0, 0.80, 2.40, 180, 1.0, 0.0], [9,9,9], 1,
#            [13501, 1], [False], [0.5, 0.5, 0.0, 0.0, 0.0])
# x.idealScore(x.DamageIndicator,[4600, 0.40, 311, 0.0, 0, 0.0, 0.34, 1.40, 180, 1.0, 0.0])
# x.HPGraph(100.0, np.arange(150.0, 450.0, 0.1))
# x.CdGraph(np.arange(150, 350.0, 0.1))
# x.ChargeGraph(np.arange(3500.0, 5500.0, 1.))
# x.CrGraph(np.arange(30.0, 100.0, 0.1))
