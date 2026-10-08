# -*- coding: utf-8 -*-
"""Author ep39 fully with 15s-bounded segments."""
import json
import _bld_helpers as H

board = json.load(open(r'd:\study\GitHub\shuohao-skills\三国演义\_board_after38.json',encoding='utf-8'))
script = json.load(open(H.SP, encoding='utf-8-sig'))

def seglist(epno, scene_idx, groups, overall, music, start=1):
    segs=[]
    for i,sp in enumerate(groups):
        n=start+i
        total=round(sum(c['sec'] for c in sp),1)
        assert total<=15, f"E{epno}-{n:02d} {total}s>15"
        segs.append(H.seg_from_specs(f'E{epno}-{n:02d}',scene_idx,sp,epno,overall,music,script))
    return segs

osa='Rain drums on the eaves of the county office, one urgent hoofbeat stops short at the gate, parchment rustles under a trembling palm, and muffled voices carry the news of Jingzhou falling.'
mus='Low, anxious strings with a wary undercurrent, at a slow tempo, swelling as the letter is read.'

# frame/shot/h3 builder shortcuts
def C(beats,sec,size,cam,chars,frame,shot,h3,cpos=None,comp=None,eye=None,foc=None,st='stable',props=[]):
    d=dict(beats=beats,sec=sec,size=size,camera=cam,chars=chars,props=props,frame=frame,shot=shot,h3=h3)
    styl={
      'wide':('35mm 广角，中等景深','+ 平视远眺','引导线构图','远景','锁定主体'),
      'medium':('50mm 标准，中浅景深','+ 平视正面','三分法','对前方','锁定主体'),
      'close':('85mm 长焦，浅景深','+ 平视正面','中心构图','对前方','锁定面部'),
      'extreme-wide':('24mm 广角，深景深','+ 平视远眺','三分法','远景','锁定剪影'),
    }
    d['cpos']=cpos or (chars[0] if chars else '画面')+' '+styl[size][1]
    d['comp']=comp or styl[size][2]
    d['eye']=eye or styl[size][3]
    d['foc']=foc or styl[size][4]
    d['stability']=st
    return d

# ---------------- SCENE 1: 荆州夜雨 (24 beats) ----------------
G1=[
 # [1,2] (4+4=8)
 [C([1,1],4,'wide','Tracking Shot',['C11'],
    '全景，雨夜府衙门口，一匹报马连滚带爬冲入，蹄下泥水四溅，来人立时翻身滚落鞍辔。',
    '镜头跟随，一骑驿马踏着雨水泥泞冲进官署前庭，马背上的信使翻身滚下，抱着一封急信踉跄上前。',
    'a tracking shot follows a courier splashing through the rain-soaked yard on an exhausted mount, sliding off with an urgent muddy letter clutched tight as he staggers toward the hall door',
    cpos='信使 + 侧面平视跟随',comp='对角线构图',foc='锁定信使与怀中急信',st='slight-shake'),
  C([2,2],4,'close','Push In',['C01'],
    '特写，烛火映在刘备侧脸上，他展开信一字字看，指尖发白，身形一晃忙扶住案角。',
    '镜头缓推，面容仁厚的男子就着烛光展开信纸，一字字读下去，指节泛白，身形一晃忙扶住案沿。',
    'a slow push-in follows the serene-faced man reading the letter by candlelight, knuckles whitening as he steadies himself against the table',
    foc='锁定刘备发白的指尖',st='slight-shake'),
 ],
 [C([3,3],6,'close','Static Shot',['C01'],
   '特写，刘备声音发颤道刘表竟病故了蔡氏扶幼子刘琮竟举荆州降曹，眼里的光一寸寸暗下去。',
   '固定特写，面容仁厚的男子低哑着声音念出这道凶信，神情由惊转沉，语尾几不可闻。',
   'a close static shot on the serene-faced man, his voice faltering as he speaks the grim news, the light in his eyes dimming, and with a shaken, grief-struck voice (S1) he tells them'),
  C([4,4],5,'wide','Static Shot',['C03'],
   '全景，张飞拍案而起，怒目圆睁道什么荆州九郡就这么白白送给曹操，身子前倾逼向前。',
   '固定镜头，虬髯大汉猛地拍案站起，怒目圆睁，粗声将满腹火气一并吼了出来。',
   'a wide static shot as the burly bearded general slams to his feet, eyes blazing, and with a thunderous, furious voice (S1) he roars')],
 # [5,6] 4+5=9
 [C([5,5],4,'close','Static Shot',['C02'],
   '特写，关羽蹙眉握住刀柄，目光沉凝地望向兄长，烛影在他眉心投下一道深纹。',
   '固定特写，长髯武将眉心深锁，一手按上腰间兵刃，神色凝重地望向身旁的兄长。',
   'a close static shot on the tall brocade-garbed warrior frowning, hand resting on his blade, gaze heavy as it turns toward his brother'),
  C([6,6],5,'close','Static Shot',['C02'],
    '特写，关羽沉声道大哥刘琮一降曹新野便成了曹军踏足的跳板，声音压得极低却字字落地。',
    '固定特写，长髯武将压低声音，一字字道出眼下的危局，语气沉凝如铁。',
    'a close static shot on the tall warrior, voice lowered to a grave murmur, and with a hushed, weighty voice (S1) he warns')],
 # [7] 4
 [C([7,7],4,'medium','Static Shot',['C05'],
   '中景，诸葛亮执扇立于案侧，神色严峻道刘琮不战而降荆州大势已去皇叔此地不可久留。',
   '固定镜头，鹤氅青年执扇立于案边，神情严峻，将眼前利弊一语道破。',
   'a medium static shot on the young strategist holding his fan, expression grave, and with a taut, urgent voice (S1) he states plainly'),
  C([8,8],5,'close','Static Shot',['C01'],
    '特写，刘备沉声问道前有曹操百万兵后又无路可退我军该往何处安身，眉间尽是无措的焦灼。',
    '固定特写，面容仁厚的男子眉头紧锁，语气里带着一份走投无路的沉痛。',
    'a close static shot on the serene-faced man, brow furrowed with helpless anguish, and with a low, tormented voice (S1) he asks')],
 # [9,10] (6+6=12)
 [C([9,9],6,'close','Static Shot',['C05'],
   '特写，诸葛亮接口道曹军虽众所恃不过数州之兵公得民心这才是退的本钱，目光笃定冷静。',
   '固定特写，鹤氅青年从容接话，语气沉定，为众人厘清以退为进的道理。',
   'a close static shot on the young strategist replying with steady assurance, and with a calm, reasoned voice (S1) he explains'),
  C([10,10],6,'close','Static Shot',['C05'],
    '特写，诸葛亮以扇指向西南，道唯有一路暂避江夏投奔刘琦以图后力，语气由沉转笃。',
    '固定特写，鹤氅青年执扇指向西南方向，语气转为笃定，为众人指明一条生路。',
    'a close static shot on the young strategist, fan pointing southwest, and with a firm voice (S1) he declares the one open road')],
 # [11,12] 4+5=9
 [C([11,11],4,'medium','Static Shot',['C03'],
   '中景，张飞一脸不甘地追问那新野就这么丢了，双手攥紧拳头垂在身侧。',
   '固定镜头，虬髯大汉满脸不甘，攥紧双拳，硬着嗓门追问这一句。',
   'a medium static shot on the burly bearded general, fists clenched with reluctance, and with a gruff, aggrieved voice (S1) he demands'),
  C([12,12],5,'medium','Static Shot',['C05'],
    '中景，诸葛亮转向张飞安抚道三将军新野是荆州一县失了还有江夏可从长计议，神色从容。',
    '固定镜头，鹤氅青年转向猛汉温言安抚，语气平缓，把话头稳稳按下来。',
    'a medium static shot on the young strategist turning to reassure the burly general, and with an even, soothing voice (S1) he calms')],
 # [13] 5
 [C([13,13],5,'medium','Static Shot',['C02'],
   '中景，关羽低声道军师说得是一时之失算不得败且看日后，神色沉稳地附和。',
   '固定镜头，长髯武将低沉着应和，神色沉稳，为众人压住心头的浮气。',
   'a medium static shot on the tall warrior voicing measured agreement, and with a low, composed voice (S1) he seconds'),
  C([14,14],6,'close','Push In',['C01'],
    '特写，刘备强自镇定道势单力孤守一隅而殃千万民非我本意走，目光由沉痛转为决然。',
    '镜头缓推，面容仁厚的男子按捺下心绪，一字一字说出决断，目光愈渐坚定。',
    'a slow push-in on the serene-faced man drawing himself up and, with a quiet, resolute voice (S1) he makes the decision')],
 # [15,16] 4+4=8
 [C([15,15],4,'medium','Static Shot',['C03','C02'],
   '中景，张飞还想再争，被关羽伸手按住臂膀，硬生生咽下满腹的话。',
   '固定镜头，长髯武将抬手按住正欲开口的猛汉臂膀，两人之间的异议就此压住。',
   'a medium static shot as the tall warrior presses a hand down on the burly general s arm, smothering the protest before it can rise'),
  C([16,16],4,'close','Static Shot',['C01'],
    '特写，刘备缓缓闭目，复睁眼时目光已重新坚毅，烛火在瞳中一点亮起。',
    '固定特写，面容仁厚的男子闭眼一瞬，再睁眼时眼底已经沉淀出决意与刚毅。',
    'a close static shot on the serene-faced man closing his eyes briefly, then reopening them with fresh resolve, a single candlelight kindling in his eyes')],
 # [17,18] 5+5=10
 [C([17,17],5,'close','Static Shot',['C02'],
   '特写，关羽掷地有声道大哥往哪去云长便跟到哪刀山火海也在所不惜，目光坚定无惧。',
   '固定特写，长髯武将一字千钧，吐出的每句话都带着刀山火海也不改其志的坚定。',
   'a close static shot on the tall warrior declaring his allegiance, and with a ringing, unwavering voice (S1) he vows'),
  C([18,18],5,'medium','Static Shot',['C05'],
    '中景，诸葛亮进言道皇叔荆州虽降民心未服曹操这正是咱们的后着，目光睿智远量。',
    '固定镜头，鹤氅青年上前一步进言，点出这看似败局里藏着的后手。',
    'a medium static shot on the young strategist stepping forward to advise, and with a sagacious voice (S1) he points out the hidden hope')],
 # [19,20] 4+5=9
 [C([19,19],4,'close','Static Shot',['C01'],
   '特写，刘备沉吟道军师是说剿仲弃地而民意仍可善加经营，眉头微动若有所思。',
   '固定特写，面容仁厚的男子若有所思地接过话头，眉头微蹙，细细咀嚼着其中深意。',
   'a close static shot on the serene-faced man pondering the words, brow knitting, and with a reflective voice (S1) he repeats in query'),
  C([20,20],5,'close','Static Shot',['C05'],
    '特写，诸葛亮颔首道正是地可失而民不可弃得民者日后方有卷土重来之势，语气愈发笃定。',
    '固定特写，鹤氅青年微微颔首，言语间尽显远略，语气愈见沉着。',
    'a close static shot on the young strategist nodding in affirmation, and with a firm, far-seeing voice (S1) he drives home the principle')],
 # [21,22] 4+5=9
 [C([21,21],4,'medium','Static Shot',['C03'],
   '中景，张飞仍不服输地别过脸咕哝那咱这仗算是白白败了，满是不甘。',
   '固定镜头，虬髯大汉赌气别过脸，硬着嗓子不肯认这一时的败。',
   'a medium static shot on the burly bearded general turning his face away, and with a grumbling, mulish voice (S1) he mutters'),
  C([22,22],5,'close','Static Shot',['C02'],
    '特写，关羽温声宽慰道三弟能全身而退保住这许多军民已是上上之策，目光温和。',
    '固定特写，长髯武将温声宽慰，把对方心头的疙瘩一点点解开。',
    'a close static shot on the tall warrior offering a gentle, steady reassurance to the burly general, and with a warm voice (S1) he consoles')],
 # [23,24] 4+4=8
 [C([23,23],4,'medium','Static Shot',['C01','C02','C03','C05'],
   '中景，刘备与诸葛亮相视一眼，又看向两位兄弟，四人目光一遇，已下了连夜撤出的决心。',
   '固定镜头，四人于烛火下交递一个眼神，不必多言便有了共同的心志。',
   'a medium static shot as the four men exchange a wordless glance, resolving in a single look to break camp that very night'),
  C([24,24],4,'wide','Static Shot',[],
    '全景，雨夜的新野城头，军士悄然开拔，一支支火把在雨幕里次第亮起，蜿蜒成行。',
    '固定远镜，雨幕里的城头上火把渐次点燃，一行队伍悄然无声地开拔而出。',
    'a wide static shot: torch after torch flares along the rain-soaked town wall as the column slips away silently into the night',
    cpos='城头全景 + 平视远眺',comp='引导线构图',foc='锁定次第亮起的火把')],
]

segs1=seglist(39,1,G1,osa,mus)
board['episodes'].append({'ep':39,'segments':segs1})
t1=round(sum(sum(c['seconds'] for c in s['cuts']) for s in segs1),1)
print('ep39 scene1 segs',len(segs1),'total',t1)
json.dump(board, open(r'd:\study\GitHub\shuohao-skills\三国演义\_board_after39.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print('saved after39')