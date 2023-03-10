import asyncio

from .enkanetwork2 import EnkaNetworkAPI
from .enkanetwork2 import EquipmentsType, DigitType
from .CalcHuTao_web import Status
import numpy as np
from collections import Counter
from .CardMakerA4_web import CardMake
import datetime
from .HuTaoPlotEnka import Status as enkaStatus

client = EnkaNetworkAPI(lang="jp")

baseimg_page1 = 'media/img/reportA4.png'
baseimg_page2 = 'media/img/reportA4.png'
signature = 'media/img/往生堂印.png'

async def main(UID):
    async with client:
        data = await client.fetch_user(UID)

        for character in data.characters:
            if character.id != 10000046:
                break
            """
            for stat in character.stats:
                print(f"- {stat[1].id} {stat[0]}: {stat[1].to_rounded() if isinstance(stat[1], Stats) else stat[1].to_percentage_symbol()}")
            print("="*18)
            """
            Baselist = [character.stats.BASE_HP.value, character.stats.FIGHT_PROP_BASE_ATTACK.value, character.stats.FIGHT_PROP_BASE_DEFENSE.value, 0.0]
            Pluslist = [character.stats.FIGHT_PROP_HP.value, character.stats.FIGHT_PROP_HP_PERCENT.value, character.stats.FIGHT_PROP_ATTACK.value, character.stats.FIGHT_PROP_ATTACK_PERCENT.value,
                        character.stats.FIGHT_PROP_DEFENSE.value, character.stats.FIGHT_PROP_DEFENSE_PERCENT.value, character.stats.FIGHT_PROP_CRITICAL.value, character.stats.FIGHT_PROP_CRITICAL_HURT.value,
                        character.stats.FIGHT_PROP_ELEMENT_MASTERY.value, character.stats.FIGHT_PROP_CHARGE_EFFICIENCY.value, character.stats.FIGHT_PROP_FIRE_ADD_HURT.value+0.33]
            # スキルによる炎元素ダメージアップを補正
            Num_C = character.constellations_unlocked
            skillLVs = [character.skills[0].level, character.skills[1].level, character.skills[2].level]

            weapon = character.equipments[-1]
            Num_R = weapon.refinement
            # [HP, HPper, ATK, ATKper, DEF, DEFper, Cr, Cd, Em, Er, EmBuff]
            # artifactstatus = [FIGHT_PROP_HP, FIGHT_PROP_HP_PERCENT, FIGHT_PROP_ATTACK, FIGHT_PROP_ATTACK_PERCENT, FIGHT_PROP_DEFENSE, FIGHT_PROP_DEFENSE_PERCENT, FIGHT_PROP_CRITICAL, FIGHT_PROP_CRITICAL_HURT, FIGHT_PROP_ELEMENT_MASTERY, FIGHT_PROP_CHARGE_EFFICIENCY, FIGHT_PROP_FIRE_ADD_HURT]
            artifact_substatus = {'FIGHT_PROP_HP': 0.0, 'FIGHT_PROP_HP_PERCENT': 0.0, 'FIGHT_PROP_ATTACK': 0.0,
                              'FIGHT_PROP_ATTACK_PERCENT': 0.0, 'FIGHT_PROP_DEFENSE':0.0, 'FIGHT_PROP_DEFENSE_PERCENT'
                              : 0.0, 'FIGHT_PROP_CRITICAL': 0.0, 'FIGHT_PROP_CRITICAL_HURT': 0.0,
                              'FIGHT_PROP_ELEMENT_MASTERY': 0.0, 'FIGHT_PROP_CHARGE_EFFICIENCY': 0.0,
                              'FIGHT_PROP_FIRE_ADD_HURT': 0.0}
            artifact_mainstatus = {'FIGHT_PROP_HP': 0.0, 'FIGHT_PROP_HP_PERCENT': 0.0, 'FIGHT_PROP_ATTACK': 0.0,
                              'FIGHT_PROP_ATTACK_PERCENT': 0.0, 'FIGHT_PROP_DEFENSE':0.0, 'FIGHT_PROP_DEFENSE_PERCENT'
                              : 0.0, 'FIGHT_PROP_CRITICAL': 0.0, 'FIGHT_PROP_CRITICAL_HURT': 0.0,
                              'FIGHT_PROP_ELEMENT_MASTERY': 0.0, 'FIGHT_PROP_CHARGE_EFFICIENCY': 0.0,
                              'FIGHT_PROP_FIRE_ADD_HURT': 0.0}

            # セット効果に関する事項
            artifact_settypeid = ['EQUIP_BRACER', 'EQUIP_NECKLACE', 'EQUIP_SHOES', 'EQUIP_RING', 'EQUIP_DRESS']
            artifact_settypevalue = ['1', '2', '3', '4', '5']
            artifact_null = ['', '', '', '', '']
            artifact_settypedict = dict(zip(artifact_settypeid, artifact_settypevalue))
            artifact_urldict = dict(zip(artifact_settypeid, artifact_settypevalue))
            artifact_substatedict = dict(zip(artifact_settypeid, artifact_null))
            artifact_substatenamedict = dict(zip(artifact_settypeid, artifact_null))
            for artifact in filter(lambda x: x.type == EquipmentsType.ARTIFACT, character.equipments):
                key1 = artifact.detail.mainstats.prop_id
                if artifact.detail.mainstats.type == DigitType.PERCENT:
                    artifact_mainstatus[key1] += artifact.detail.mainstats.value / 100
                else:
                    artifact_mainstatus[key1] += artifact.detail.mainstats.value
                artifact_settypedict[artifact.detail.artifact_type] = artifact.detail.artifact_name_set
                artifact_urldict[artifact.detail.artifact_type] = artifact.detail.icon.url
                for substate in artifact.detail.substats:
                    key = substate.prop_id
                    if substate.type == DigitType.PERCENT:
                        artifact_substatus[key] += substate.value/100
                    else:
                        artifact_substatus[key] += substate.value
                    artifact_substatedict[artifact.detail.artifact_type] += str(substate.value) + (' %' if substate.type == DigitType.PERCENT else '') + "\n"
                    artifact_substatenamedict[artifact.detail.artifact_type] += substate.name + "\n"
            # セット効果を表示
            CW4 = False
            artifact_settypelist = artifact_settypedict.values()
            count1 = Counter(artifact_settypelist)
            for item, count in count1.items():
                if count > 3 and item == "燃え盛る炎の魔女":
                    CW4 = True
                    Pluslist[10] += 0.075  # 炎バフを補正


            artifact_setname = ""
            for item, count in count1.items():
                if count > 3:
                    artifact_setname += item + ' 4セット' + '\n'
                elif count > 1:
                    artifact_setname += item + ' 2セット' + '\n'


            substate_data = artifact_substatus.values()
            mainstate_data = artifact_mainstatus.values()
            # メインステータスを最適なものに補正する
            # 胡桃の場合HP時計と熟知時計の両方を検討
            artifact_mainstatus_ideal_HP = {'FIGHT_PROP_HP': 4780.0, 'FIGHT_PROP_HP_PERCENT': 0.466, 'FIGHT_PROP_ATTACK': 311.0,
                                   'FIGHT_PROP_ATTACK_PERCENT': 0.0, 'FIGHT_PROP_DEFENSE': 0.0,
                                   'FIGHT_PROP_DEFENSE_PERCENT'
                                   : 0.0, 'FIGHT_PROP_CRITICAL': 0.311, 'FIGHT_PROP_CRITICAL_HURT': 0.0,
                                   'FIGHT_PROP_ELEMENT_MASTERY': 0.0, 'FIGHT_PROP_CHARGE_EFFICIENCY': 0.0,
                                   'FIGHT_PROP_FIRE_ADD_HURT': 0.466}
            artifact_mainstatus_ideal_EM = {'FIGHT_PROP_HP': 4780.0, 'FIGHT_PROP_HP_PERCENT': 0.0, 'FIGHT_PROP_ATTACK': 311.0,
                                   'FIGHT_PROP_ATTACK_PERCENT': 0.0, 'FIGHT_PROP_DEFENSE': 0.0,
                                   'FIGHT_PROP_DEFENSE_PERCENT'
                                   : 0.0, 'FIGHT_PROP_CRITICAL': 0.311, 'FIGHT_PROP_CRITICAL_HURT': 0.0,
                                   'FIGHT_PROP_ELEMENT_MASTERY': 187.0, 'FIGHT_PROP_CHARGE_EFFICIENCY': 0.0,
                                   'FIGHT_PROP_FIRE_ADD_HURT': 0.466}
            mainstatus_ideal_HP_data = artifact_mainstatus_ideal_HP.values()
            mainstatus_ideal_EM_data = artifact_mainstatus_ideal_EM.values()
            x = Status(Baselist, Pluslist, skillLVs, Num_C, [weapon.id, Num_R], [CW4])
            l = np.array(Pluslist) - np.array(list(substate_data))
            l_HP = np.array(Pluslist) - np.array(list(substate_data)) - np.array(list(mainstate_data)) + np.array(list(mainstatus_ideal_HP_data))
            l_EM = np.array(Pluslist) - np.array(list(substate_data)) - np.array(list(mainstate_data)) + np.array(list(mainstatus_ideal_EM_data))
            x.idealScore(x.DamageIndicator, l)
            scoreideal_HP = x.idealScore(x.DamageIndicator, l_HP)
            scoreideal_EM = x.idealScore(x.DamageIndicator, l_EM)

            score = min([scoreideal_HP, scoreideal_EM])
            scoreHP = (np.array(list(substate_data))[6]*2 + np.array(list(substate_data))[7] + np.array(list(substate_data))[1])*100
            scoreEm = (np.array(list(substate_data))[6]*2 + np.array(list(substate_data))[7])*100 + np.array(list(substate_data))[8]/4
            scores = [score, scoreHP, scoreEm]

            card = CardMake(baseimg_page1)

            # カード作製
            i = 0
            for artifact in filter(lambda x: x.type == EquipmentsType.ARTIFACT, character.equipments):
                card.mainstate(artifact.detail.mainstats.name,[200, 100*i+450],14)
                card.mainstate(str(artifact.detail.mainstats.value) + ('%' if artifact.detail.mainstats.type == DigitType.PERCENT else ''),[200, 100*i+480],24)
                i += 1
            artifact_substatelist = artifact_substatedict.values()
            artifact_substatenamelist = artifact_substatenamedict.values()
            for index, text in enumerate(artifact_substatelist):
                card.substate(text, [369, 100*index+450])
            for index, text in enumerate(artifact_substatenamelist):
                card.substate(text, [220, 100*index+450])
            artifact_urllist = artifact_urldict.values()
            for index, url in enumerate(artifact_urllist):
                card.printurlimg(url, [14, 448+100*index], [100,100])
            card.printurlimg(character.image.card.url, [30, 125], [180, 180])

            # 武器
            card.printurlimg(weapon.detail.icon.url, [480, 179], [183, 183])
            card.text(weapon.detail.name, [480, 185+15*0])
            card.text('LV ' + str(weapon.level), [480, 185+15*1])
            card.text('R' + str(weapon.refinement), [480, 185+15*2])

            # セット効果
            card.text(artifact_setname, [585, 405], 14, 'ms')

            card.textmake(x.status, scores, data.player.nickname)

            card.text(str(character.level) + " / " + str(character.max_level), [100, 307+30*0])
            card.text(str(character.friendship_level), [100, 307+30*1])
            card.text(str(character.skills[0].level), [100, 307+30*2])
            card.text(str(character.skills[1].level), [100, 307+30*3])
            card.text(str(character.skills[2].level), [100, 307+30*4])

            card.text('Name : ' + data.player.nickname, [23, 80], 16)
            card.text('UID : ' + str(UID), [23, 100], 16)

            # グラフ作製
            graph = enkaStatus()
            img = graph.HPGraph(*x.status_forGraph, "a")
            card.printimg_pil(img, [470, 465],  [int(i) for i in [640/2.8, 480/2.8]])
            img2 = graph.EmGraph(*x.status_forGraph, x.Em, CW4, 0.82, "a")
            card.printimg_pil(img2, [470, 670],  [int(i) for i in [640/2.8, 480/2.8]])

            # 発行日記入
            dt_now = datetime.datetime.now()
            card.text('発行日 : ' + dt_now.strftime('%Y年%m月%d日'), [565, 8], 12)

            # 印字
            card.printimg(signature, [620, 66], [100, 100])

            # card.showimg()
            # card.img.save("media/img/"+str(UID)+'.png')

            # 往生夜行指標(HP+25%, 元素熟知+120, 夜蘭のダメージバフ, 耐性ダウン)
            DHHT = {'FIGHT_PROP_HP': 0.0, 'FIGHT_PROP_HP_PERCENT': 0.25, 'FIGHT_PROP_ATTACK': 0.0,
                                   'FIGHT_PROP_ATTACK_PERCENT': 0.0, 'FIGHT_PROP_DEFENSE': 0.0,
                                   'FIGHT_PROP_DEFENSE_PERCENT'
                                   : 0.0, 'FIGHT_PROP_CRITICAL': 0.0, 'FIGHT_PROP_CRITICAL_HURT': 0.0,
                                   'FIGHT_PROP_ELEMENT_MASTERY': 120.0, 'FIGHT_PROP_CHARGE_EFFICIENCY': 0.0,
                                   'FIGHT_PROP_FIRE_ADD_HURT': 0.275}
            modifiedPluslist = np.array(Pluslist) + np.array(list(DHHT.values()))
            DHHTx = Status(Baselist, modifiedPluslist, skillLVs, Num_C, [weapon.id, Num_R], [CW4])
            l_DHHT = np.array(modifiedPluslist) - np.array(list(substate_data))
            l_HP_DHHT = np.array(modifiedPluslist) - np.array(list(substate_data)) - np.array(list(mainstate_data)) + np.array(list(mainstatus_ideal_HP_data))
            l_EM_DHHT = np.array(modifiedPluslist) - np.array(list(substate_data)) - np.array(list(mainstate_data)) + np.array(list(mainstatus_ideal_EM_data))
            DHHTx.idealScore(DHHTx.DamageIndicator, l_DHHT)
            scoreideal_HP_DHHT = DHHTx.idealScore(DHHTx.DamageIndicator, l_HP_DHHT)
            scoreideal_EM_DHHT = DHHTx.idealScore(DHHTx.DamageIndicator, l_EM_DHHT)

            score_DHHT = min([scoreideal_HP_DHHT, scoreideal_EM_DHHT])
            scores_DHHT = [score_DHHT, scoreHP, scoreEm]

            # グラフの作製
            card2 = CardMake(baseimg_page2)
            img = graph.HPGraph(*DHHTx.status_forGraph, "a")
            card2.printimg_pil(img, [470, 465],  [int(i) for i in [640/2.8, 480/2.8]])
            img2 = graph.EmGraph(*DHHTx.status_forGraph, DHHTx.Em, CW4, 0.82, "a")
            card2.printimg_pil(img2, [470, 670],  [int(i) for i in [640/2.8, 480/2.8]])
            # ダメージ表示
            for indexY, dicts in enumerate(x.DMGsDict):
                for indexX, damage in enumerate(list(dicts.values())):
                    if type(damage) is np.float64:
                        damage = (round(damage, 1))
                    card2.text(str(damage), [100 + indexX*75, 107 + 30 * indexY], anchor='ra')
            # ダメージ表示(往生夜行)
            for indexY, dicts in enumerate(DHHTx.DMGsDict):
                for indexX, damage in enumerate(list(dicts.values())):
                    if type(damage) is np.float64:
                        damage = (round(damage, 1))
                    card2.text(str(damage), [100 + indexX*75, 507 + 30 * indexY], anchor='ra')
            # VV指標(元素熟知+120, 耐性ダウン, 万葉のダメージバフ)
            # card2.showimg()
    return card.img

img = asyncio.run(main(815487724))
img.show()
        # 815487724　824237286 843715177 813771318