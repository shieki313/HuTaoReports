from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

fonturl = 'fonts/ja-jp.ttf'

class CardMake:
    def __init__(self, url):
        self.img = Image.open(url)

    def textmake(self, status=[0., 0., 0., 0., 0., 0., 0., 0., 0.], scores=[0., 0., 0.], name="ナナシ"):
        status[4] *= 100
        status[5] *= 100
        status[6] *= 100
        status[8] *= 100
        statusstr = [str(round(i, 1)) for i in status]
        statusname = ['攻撃力', 'HP', 'スキル発動時攻撃力', '換算HP', '元素熟知', '会心率', '会心ダメージ', '元素熟知', '炎ダメージバフ']
        basedata = ['LV','好感度','通常','スキル','爆発']
        scoresstr = [str(round(i, 1)) for i in scores]

        font = ImageFont.truetype(fonturl, 14)
        font_big = ImageFont.truetype(fonturl, 36)

        draw = ImageDraw.Draw(self.img)

        # ステータス表記
        baseline = 187
        spaceline = 30
        baselinex = 220
        draw.text((baselinex, baseline + spaceline * 0), statusname[0], 'black', font=font)
        draw.text((baselinex, baseline + spaceline * 1), statusname[1], 'black', font=font)
        draw.text((baselinex, baseline + spaceline * 2), statusname[2], 'black', font=font)
        draw.text((baselinex, baseline + spaceline * 3), statusname[3], 'black', font=font)
        draw.text((baselinex, baseline + spaceline * 4), statusname[5], 'black', font=font)
        draw.text((baselinex, baseline + spaceline * 5), statusname[6], 'black', font=font)
        draw.text((baselinex, baseline + spaceline * 6), statusname[7], 'black', font=font)
        draw.text((baselinex, baseline + spaceline * 7), statusname[8], 'black', font=font)

        baselinex = 369
        draw.text((baselinex, baseline + spaceline * 0), statusstr[0], 'black', font=font)
        draw.text((baselinex, baseline + spaceline * 1), statusstr[1], 'black', font=font)
        draw.text((baselinex, baseline + spaceline * 2), statusstr[2], 'black', font=font)
        draw.text((baselinex, baseline + spaceline * 3), statusstr[3], 'black', font=font)
        # draw.text((baselinex+200, baseline + spaceline * 3), statusstr[4] + " %", 'black', font=font)
        draw.text((baselinex, baseline + spaceline * 4), statusstr[5] + " %", 'black', font=font)
        draw.text((baselinex, baseline + spaceline * 5), statusstr[6] + " %", 'black', font=font)
        draw.text((baselinex, baseline + spaceline * 6), statusstr[7], 'black', font=font)
        draw.text((baselinex, baseline + spaceline * 7), statusstr[8] + " %", 'black', font=font)

        # ベースステータス
        baselinex = 18
        draw.text((baselinex, baseline + spaceline * 4), basedata[0], 'black', font=font)
        draw.text((baselinex, baseline + spaceline * 5), basedata[1], 'black', font=font)
        draw.text((baselinex, baseline + spaceline * 6), basedata[2], 'black', font=font)
        draw.text((baselinex, baseline + spaceline * 7), basedata[3], 'black', font=font)
        draw.text((baselinex, baseline + spaceline * 8), basedata[4], 'black', font=font)

        # クレジット
        fontcredit = ImageFont.truetype(fonturl, 16)
        draw.text((515, 120), "制作：使役", 'black', font=fontcredit)
        draw.text((515, 140), "@juggler_make", 'black', font=fontcredit)

        # スコア
        draw.text((60, 980), "スコア", 'red', font=font_big)
        draw.text((307, 980), "HPスコア", 'red', font=font)
        draw.text((307, 1000), "熟知スコア", 'red', font=font)
        draw.text((180, 980), scoresstr[0], 'red', font=font_big)
        draw.text((387, 980), scoresstr[1], 'red', font=font)
        draw.text((387, 1000), scoresstr[2], 'red', font=font)

    def printurlimg(self, artifacturl, loc=[0, 450], size=[0,0]):
        response = requests.get(artifacturl)
        im2 = Image.open(BytesIO(response.content))
        if size==[0,0]:
            img_resize = im2
        else:
            img_resize = im2.resize(size)
        self.img.paste(img_resize, loc, img_resize)

    def substate(self, string, loc=[0, 0]):
        font = ImageFont.truetype(fonturl, 14)
        draw = ImageDraw.Draw(self.img)
        draw.text(loc, string, 'black', font=font, spacing=11)

    def mainstate(self, string, loc=[0, 0], fontsize=14):
        font = ImageFont.truetype(fonturl, fontsize)
        draw = ImageDraw.Draw(self.img)
        draw.text(loc, string, 'black', font=font, align='right', anchor='ra')

    def text(self, string, loc=[0, 0], fontsize=14, anchor='la'):
        font = ImageFont.truetype(fonturl, fontsize)
        draw = ImageDraw.Draw(self.img)
        draw.text(loc, string, 'black', font=font, anchor=anchor)

    def printimg(self, imgpass, loc, size=[0,0]):
        img = Image.open(imgpass)
        if size==[0,0]:
            img_resize = img
        else:
            img_resize = img.resize(size)
        self.img.paste(img_resize, loc, img_resize)

    def savereport(self, url='img/pillow_imagedraw_text.png'):
        self.img.save(url)

    def showimg(self):
        self.img.show()


# 動作テスト
"""
status = [1154.069109348391, 34372.24793668871, 3924.4722930455014, 48690.72323877793, 2.1307718117896624,
          0.847100019454956, 2.5789361000061035, 98.6500015258789, 0.6159999966621399]
scores = [222, 210, 250]
x = CardMake('img/reportA4.png')
x.textmake(status, scores,"名前")

x.printimg('img/往生堂印.png',[620,84], [100,100])
x.showimg()


url3 = 'https://enka.network/ui/UI_RelicIcon_14003_1.png'
artifactsimg(url3,[222,450])

"""