# -*- coding: utf-8 -*-
"""构建 storyboard-batch-9.json：ep41-45 切分镜，程序化生成 H3 对齐指令与切点时刻。"""
import io, sys, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SRC = 'storyboard-batch-9.json'
raw = open(SRC, encoding='utf-8-sig').read()
orig = json.loads(raw.replace('\ufeff', ''))

EPISODES = orig['episodes']
# sceneIndex 从 seedScenes 里取出的顺序
scene_index = {}
for e in EPISODES:
    scene_index[e['ep']] = {}
    for i, sc in enumerate(e.get('seedScenes', []), 1):
        scene_index[e['ep']][sc['sceneId']] = i
        sc['_si'] = i
        # build beats map for dialogue extraction
        sc['_beats'] = {b['n']: b for b in sc['beats']}

def dlg(sc, n):
    b = sc['_beats'][n]
    return b['text']

# ---------- H3 派生骨架（与 novel-storyboard.mjs 保持一致） ----------
def h3CutTime(t):
    m = int(t // 60); s = int(t % 60)
    ms = int(round((t - int(t)) * 1000))
    return f"{m:02d}:{s:02d}.{ms:03d}"

def cutStarts(cuts):
    starts=[]; t=0
    for c in cuts:
        starts.append(round(t*10)/10); t+= c['sec']
    return starts

def h3AlignmentLine(cuts):
    if len(cuts) <= 1:
        return 'For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.'
    starts=cutStarts(cuts)
    parts=[f"Picture {i+1} (from Shot {i+1}) aligns with the {starts[i]:.2f}-second mark of the target video" for i in range(len(cuts))]
    return 'How the reference pictures align with the target video — ' + '; '.join(parts) + '.'

def build_segment(ep, sceneIndex, seg_no, chBlocking, enSound, enMusic, zhSound, zhMusic, cuts):
    CAM = {'Static Shot':'static shot','Tracking Shot':'tracking shot','Push In':'push in',
           'Pull Out':'pull out','Zoom In':'zoom in','Zoom Out':'zoom out','Pan Left':'pan left',
           'Pan Right':'pan right','Truck Left':'truck left','Truck Right':'truck right',
           'Tilt Up':'tilt up','Tilt Down':'tilt down','Pedestal Up':'pedestal up',
           'Pedestal Down':'pedestal down','Arc Shot':'arc shot','POV':'point of view',
           'Shake Slightly':'slight handheld shake','Shake Strongly':'violent shake',
           'Roll Clockwise':'roll','Roll Counterclockwise':'roll'}
    starts=cutStarts(cuts)
    line1 = h3AlignmentLine(cuts)
    body_lines=[]
    for i,c in enumerate(cuts):
        h3txt = c['h3']
        cp = CAM.get(c.get('cam'))
        if cp and cp not in (' '.join(h3txt.split())).lower():
            h3txt = h3txt.rstrip() + f' The camera performs a {cp}.'
        if i==0:
            body_lines.append("[Shot 1] " + h3txt)
        else:
            tm=h3CutTime(starts[i])
            body_lines.append(f"[Shot {i+1}] At {tm}, " + h3txt)
    h3 = f"{line1}\n\nintegrated_multimodal_description:\n" + "\n".join(body_lines) + \
         f"\n\noverall_soundscape: {enSound}\n\nnon_diegetic_music: {enMusic}"
    K = {'b':'beats','sec':'seconds','cam':'camera','ch':'characters','pr':'props',
         'frame':'frame','shot':'shot','lens':'lens','cp':'cameraPosition','comp':'composition',
         'eye':'eyeline','focus':'focus','stab':'stability','size':'size'}
    mapped=[]
    for c in cuts:
        m={}
        for kk,vv in c.items():
            if kk=='h3': continue
            m[K.get(kk,kk)]=vv
        if not m.get('props'): m.pop('props',None)
        mapped.append(m)
    seg = {
        "id": f"E{ep:02d}-{seg_no:02d}",
        "sceneIndex": sceneIndex,
        "cuts": mapped,
        "h3Prompt": h3,
        "blocking": chBlocking,
        "soundscape": zhSound,
        }
    if zhMusic and zhMusic != 'N/A':
        seg["music"] = zhMusic
    return seg

# =====================================================================
# EP 41
# =====================================================================
EPN = 41
s1 = [s for s in EPISODES[0]['seedScenes'] if s['sceneId']=='S07'][0]  # scene1, 32 beats
s1b = s1['beats']
s2 = [s for s in EPISODES[0]['seedScenes'] if s['_si']==2][0]          # scene2, 27 beats
s2b = s2['beats']

def E41_cuts():
    segs=[]
    # ---- scene1 ----
    # seg1 beats1-4
    segs.append(dict(sceneId='S07',
      blocking='开场当阳道上一片溃乱：白袍将军单骑逆着人潮冲入画面中偏右，面朝阵心，身后遍地辎重旗杆；第一镜只有他一人。',
      soundscape='战场上嘈杂的人声与马蹄声，风卷起沙尘，时有金铁相击声，低沉而密集',
      music='低沉急促的战鼓与弦乐，中速偏快，压在溃退的嘈杂之下',
      cuts=[
       dict(b=[1,1],sec=3,size='medium',cam='Tracking Shot',ch=['C11'],pr=[],
         frame='中景，长坂坡当阳道尘土弥漫，赵云白袍银甲单骑逆着溃退的乱军往里冲，手中长枪倒拖在地，马鬃扫开一杆挡路的长矛，昏黄的烟尘光',
         shot='镜头从侧后方平稳跟拍，一名白袍小将策马逆着人潮冲进阵中，单手倒拖着长枪，枪尾擦地划过尘土，马鬃拂开逼近的长矛，动作利落不停',
         lens='35mm 广角，中景深', cp='白袍小将 + 侧后方平视跟随', comp='中心构图', eye='阵心方向', focus='锁定白袍小将与长枪', stab='slight-shake',
         h3='The cold open follows <Picture 1>: a white-robed young cavalry general charges against the tide of a rout across a dusty battlefield, his long spear trailing low along the ground behind the horse; a tracking shot follows him from behind and slightly to the side, the horse-tongue flicking past a raised pike as he pushes deeper into the chaos.'),
       dict(b=[2,3],sec=5,size='medium',cam='Static Shot',ch=['C11'],pr=[],
         frame='中景，当阳道上一名曹军骑将横刀勒马拦在赵云马前，赵云伏身躲过刀锋，反手一枪点中对方肩甲，把人掀下马背，尘土四溅',
         shot='固定镜头，一名敌方骑将横刀迎面冲来，白袍小将借着两马错镫的惯性伏身一让，反手一枪戳中对方肩甲，将人掀落马下',
         lens='50mm 标准，中浅景深', cp='双骑 + 平视侧面', comp='三分法', eye='敌将肩甲', focus='锁定枪尖点中肩甲的一瞬', stab='stable',
         h3='Holding <Picture 2> in the two-horse clash, a charging enemy rider raises a blade; over a static shot the white-robed general leans low to dodge the edge as the horses pass, then strikes back with his spear point caught on the rider shoulder and knocks the man off the saddle.'),
       dict(b=[4,4],sec=4,size='wide',cam='Static Shot',ch=['C11'],pr=[],
         frame='全景，当阳道上赵云不停蹄地趟过被弃的辎重车和倒地的旗杆，一路往阵心杀去，远处尘烟弥漫',
         shot='固定镜头，白袍小将催马趟过横七竖八的辎重与旗杆，头也不回地朝阵心杀去，马蹄踢起一路尘土',
         lens='35mm 广角，中景深', cp='战场远景 + 平视侧面', comp='对角线构图', eye='阵心方向', focus='锁定白袍小将骑影', stab='stable',
         h3='The wide view of <Picture 3> holds as the white-robed general spurs the horse through abandoned carts and fallen banners, trampling over the debris toward the heart of the formation; static shot, hooves kicking up a long plume of dust.'),
      ]))
    # seg2 beats5-9
    segs.append(dict(sceneId='S07',
      blocking='画面以张开的战场为底：白袍将军居右，拥着妇人的乱兵挤在正中，妇人抱着襁褓在左侧被人潮冲翻。',
      soundscape='推向高处的人声与推搡声，妇人一声短促的惊呼被急促马蹄掩过，随后金铁交鸣',
      music='急促鼓点的一条低音线快节奏压场，随冲突起伏',
      cuts=[
       dict(b=[5,6],sec=5,size='wide',cam='Tracking Shot',ch=['C11'],pr=[],
         frame='全景，乱兵中一名妇人抱着襁褓被冲倒在地，赵云纵马抢到跟前探下身子，一把捞起妇人和襁褓稳稳搁上马背',
         shot='镜头平稳跟随，一名抱着襁褓的妇人被冲得踉跄跌坐，白袍将军策马赶上俯身，一只手臂猛地捞住妇人与婴儿稳稳横放上马',
         lens='35mm 广角，中景深', cp='白袍将军 + 侧面平视跟随', comp='中心构图', eye='地上的妇人与襁褓', focus='锁定捞起母子的一瞬', stab='slight-shake',
         h3='A tracking shot sweeps with <Picture 2> as the rescued mother with a baby in arms is jostled down amid the mob; the white-robed general reaches the spot, leans from the saddle and scoops the woman and the swaddled infant onto the horse in one steady movement.'),
       dict(b=[7,7],sec=3,size='close',cam='Static Shot',ch=['C11'],pr=[],
         frame='特写，赵云在马背上俯身朝妇人大声叮嘱，眼神急切真挚，白袍在风里翻卷，身后溃兵往来',
         shot='固定镜头近切，白袍小将侧过头，声音急切而有力，叮嘱马背上的妇人把怀里的孩子抱紧',
         lens='85mm 长焦，浅景深', cp='白袍小将 + 平视正面', comp='三分法', eye='马背上的妇人', focus='锁定白袍小将面部', stab='stable',
         h3='The close framing of <Picture 3> holds on the young general leaning toward the woman on horseback; static shot, and the white-robed general with a tense, urgent voice (S1) presses on: <d>[Chinese] 抱紧孩子，千万别撒手。</d>'),
       dict(b=[8,9],sec=5,size='medium',cam='Static Shot',ch=['C11'],pr=[],
         frame='中景，搜索的曹军从两翼合拢过来刀枪齐举，赵云夹紧马腹枪出如龙，挑开两柄长刀，踏着败草夺路而走',
         shot='固定镜头，两翼敌军举刀合拢，白袍小将夹紧马腹一抢挑开两柄长刀，趁着破口踏着败草冲出去夺路而走',
         lens='50mm 标准，中浅景深', cp='白袍小将 + 平视侧面', comp='三分法', eye='两翼合拢的敌兵', focus='锁定挑开双刀的风/枪影', stab='stable',
         h3='Under <Picture 4>, enemy soldiers close in from both flanks raising their arms; over a static shot the white-robed general kicks the horse and sweeps his spear, knocking aside two blades and surging through the gap across the trampled grass and away.'),
      ]))
    # seg3 beats10-13
    segs.append(dict(sceneId='S07',
      blocking='高坡上，曹操居画面左侧骑于伞盖下远眺战场，右侧远处是乱阵里的白袍小将；偏将立曹操身侧稍后。',
      soundscape='战场远处的人喊马嘶与风声，曹操面前一片相对安静，只有旌旗猎猎',
      music='低沉弦乐托底，速度偏慢，透出一丝审视的余地',
      cuts=[
       dict(b=[10,10],sec=3,size='wide',cam='Static Shot',ch=['C04'],pr=[],
         frame='全景，高坡上一名曹军统帅在伞盖下列马远望，捋须不动声色，背后旌旗猎猎，远处是乱阵战场',
         shot='固定镜头远景，一名披重甲的统帅骑在马上立在伞盖下远眺战场，手捋胡须不开口，旌旗在他头顶翻卷',
         lens='35mm 广角，中景深', cp='统帅 + 平视仰角度', comp='对角线构图', eye='远处的战场', focus='锁定伞盖下统帅侧影', stab='stable',
         h3='<Picture 1> frames the high slope: a heavy-robed warlord sits on horseback under a canopy gazing down at the distant melee; static shot, fondling his beard without a word while a banner stirs overhead.'),
       dict(b=[11,11],sec=3,size='close',cam='Push In',ch=['C04'],pr=[],
         frame='特写，曹操眯眼望着乱阵里那道越战越勇的白影，若有所思地缓缓开口，眉眼间有审视与惜才',
         shot='镜头小幅缓推，统帅眯着眼望向战场里那道不停冲杀的白影，缓缓开口，语气里有难掩的叹惜',
         lens='85mm 长焦，极浅景深', cp='统帅 + 平视正面', comp='三分法', eye='战场里的白影', focus='锁定统帅眉眼', stab='stable',
         h3='A slow push in with small amplitude closes on <Picture 2>: the warlord narrows his eyes at the white flash still fighting in the field, and with a measured, grudging voice (S2) murmurs: <d>[Chinese] 这等好身手，偏跟了刘备。</d>'),
       dict(b=[12,13],sec=5,size='close',cam='Static Shot',ch=['C04'],pr=[],
         frame='特写，曹操身边偏将已张弓搭箭，曹操抬手按住他的腕子，语气笃定地说完下半句，眼底是活擒的算计',
         shot='固定镜头，身侧一名将领已张弓要放箭，统帅抬手按住对方腕子，语气笃定地改主意，目光仍盯在战场那点白影上',
         lens='85mm 长焦，极浅景深', cp='统帅与偏将 + 平视正侧面', comp='三分法', eye='按住腕子的手，再移向战场', focus='锁定按住腕子的手', stab='stable',
         h3='Keeper of <Picture 3>: a nearby officer raises a bow to shoot, but the warlord lifts a hand to press down on his wrist; over a static shot the warlord with a cool, decisive voice (S2) decides: <d>[Chinese] 生擒活虎，强过杀只死虎。</d>'),
      ]))
    # seg4 beats14-18
    segs.append(dict(sceneId='S07',
      blocking='中近景围绕白袍将军：他在画面中央马上，襁褓搭在身前马背上，妇人与他一前一后；两侧远处是合拢的敌兵。',
      soundscape='马蹄声不断，风声卷过，远处兵刃叮当与喊杀，偶有妇人稳定的呼吸声',
      music='节奏紧促的低音鼓与弦乐平滑推进',
      cuts=[
       dict(b=[14,14],sec=2,size='extreme-close',cam='Static Shot',ch=['C11'],pr=[],
         frame='大特写，赵云身前的襁褓松脱了半截，他回首探臂回护，堪堪把襁褓扶稳，指节扣进包布',
         shot='固定镜头插入特写，马背上的襁褓滑松了半截，白袍将军回头探臂，稳稳把襁褓扶回原位',
         lens='100mm 微距，极浅景深', cp='襁褓 + 平视', comp='中心构图', eye='回护襁褓的手', focus='锁定扣住包布的指节', stab='stable',
         h3='The extreme-close insert of <Picture 1> lands: the swaddled bundle slips half open on the horse, and the white-robed general reaches back with one arm, static shot, steadying it with fingers hooked into the cloth.'),
       dict(b=[15,16],sec=5,size='wide',cam='Static Shot',ch=['C11'],pr=[],
         frame='全景，坡下曹军一队接一队涌上来，赵云护着马背上的母子且战且走，白袍渐渐被血染透，一名偏将趁侧里偷袭他又回马架住',
         shot='固定镜头，敌军一队接一队涌上，白袍将军护着马背上的母子边战边走，血渐渐洇上白袍；一名偏将侧里偷袭，他回马一枪架住并把长刀荡开',
         lens='35mm 广角，中景深', cp='战场全景 + 平视', comp='对角线构图', eye='涌上来的敌阵', focus='锁定白袍将军苦战的身影', stab='stable',
         h3='The wide framing of <Picture 2> holds as enemy ranks flood up in waves; static shot, the white-robed general shields the mother and child on horseback while fighting and retreating, blood spotting his white robe, and when a rider strikes from the side he wheels and locks the spear against the blade, flinging it aside.'),
       dict(b=[17,18],sec=5,size='medium',cam='Static Shot',ch=['C11'],pr=[],
         frame='中景，马背上妇人被颠得抱不稳，赵云探出空出的那只手腕稳托住她臂弯，同时侧目紧盯又从两翼包抄上来的曹军',
         shot='固定镜头中景，马上的妇人被颠得身形摇晃，白袍将军探出空手稳稳托住她臂弯，眼睛却仍盯着两翼包抄上来的敌军',
         lens='50mm 标准，中浅景深', cp='白袍将军与妇人 + 平视侧面', comp='三分法', eye='先看妇人再看两翼敌兵', focus='锁定托住臂弯的手', stab='stable',
         h3='<Picture 3> holds mid-frame: rocked in the saddle, the woman sways and the white-robed general reaches out his free hand to steady her arm; over a static shot, his eyes stay fixed on the enemy closing from both sides.'),
      ]))
    # seg5 beats19-23
    segs.append(dict(sceneId='S07',
      blocking='反复在战场白袍将军与大坡伞盖下统帅之间切换：白袍在右中景，统帅居左近景，两者隔着千里战场呼应。',
      soundscape='骤起的风声，马蹄声，妇人抱住襁褓的闷声，远处喊杀渐稀',
      music='一段低音弦乐随情绪起伏，中速，转散开的口子时略收',
      cuts=[
       dict(b=[19,19],sec=4,size='close',cam='Static Shot',ch=['C11'],pr=[],
         frame='特写，赵云边战边朝马背上的妇人沉声交代，眼神坚毅，血点溅在脸颊，热气在烟尘里蒸腾',
         shot='固定镜头近切，白袍小将边战边侧头，声音沉而稳，向马背上的妇人下着一句重诺',
         lens='85mm 长焦，极浅景深', cp='白袍小将 + 平视正面', comp='三分法', eye='马背上的妇人', focus='锁定白袍小将眼神', stab='stable',
         h3='The close-up of <Picture 4> holds on the young general mid-battle; static shot, and the white-robed general with a low, firm voice (S1) promises: <d>[Chinese] 抱牢这孩子，天塌不塌，都有我。</d>'),
       dict(b=[20,20],sec=3,size='close',cam='Static Shot',ch=['C04'],pr=[],
         frame='特写，高坡上曹操望着乱阵里那道越战越勇的白影，眼底浮起一丝难掩的赞许，微微眯眼',
         shot='固定镜头近切，统帅望着乱阵里越战越勇的白影，眼底滑过一丝藏不住的赞许，没有喝彩也没有动作',
         lens='85mm 长焦，极浅景深', cp='统帅 + 平视正面', comp='三分法', eye='阵中白影', focus='锁定统帅眼底', stab='stable',
         h3='A static shot close-up of <Picture 5>: watching the white figure fight harder through the chaos, the warlord lets a flash of unconcealed approval rise in his eyes and gives no order.'),
       dict(b=[21,21],sec=3,size='close',cam='Push In',ch=['C04'],pr=[],
         frame='特写，曹操低低叹道那句夸赞，眉头微动，语气里听得出真正的可惜，伞影投在半张脸上',
         shot='镜头小幅缓推，统帅半张脸落在伞影里，低声自语般叹出一句，眉眼间是真的惋惜',
         lens='85mm 长焦，极浅景深', cp='统帅 + 平视正面', comp='三分法', eye='阵中白影', focus='锁定统帅眉目', stab='stable',
         h3='A slow push in with small amplitude on <Picture 6>: half his face in the canopy shadow, the warlord sighs out the line to himself, and with a low, sincerely reluctant voice (S2) says: <d>[Chinese] 这般忠勇，偏偏跟了刘备。</d>'),
       dict(b=[22,23],sec=5,size='wide',cam='Static Shot',ch=['C11'],pr=[],
         frame='全景，赵云硬冲开一道口子，前头又有伏兵举旗拦住，马鬃上滴着血，他俯身扫起地上一杆断枪扬手掷出，把拦路的旗手放翻',
         shot='固定镜头，白袍将军硬冲开一道口子，前头伏兵举旗拦住，他俯身捞起地上一杆断枪扬手掷出，正中旗手将其放翻',
         lens='35mm 广角，中景深', cp='战场 + 平视侧面', comp='对角线构图', eye='拦路的伏兵旗手', focus='锁定掷出的断枪', stab='stable',
         h3='Holding the wide of <Picture 7>, the white-robed general forces open a gap but a flag-carrier blocks ahead; static shot, blood dripping from the horse-tongue, he scoops a broken pike off the ground and hurls it, knocking the standard-bearer down.'),
      ]))
    # seg6 beats24-29
    segs.append(dict(sceneId='S07',
      blocking='白袍将军居中正面策马，身后追兵成一线压低视角；妇人缩在他身后马背上，村林的绿影在画面深处。',
      soundscape='马蹄紧凑如雨点，风声愈急，追兵的喊杀保持一段距离，襁褓里偶有一声微弱啼哭',
      music='快节奏低音弦乐一路推进，张力拉满快到顶点',
      cuts=[
       dict(b=[24,25],sec=5,size='wide',cam='Tracking Shot',ch=['C11'],pr=[],
         frame='全景，曹军人墙裂开一隙，赵云从那道缝里一蹿而过直插村林，身后追兵不歇，他头也不回把马催得更急，蹄下尘土高高扬起',
         shot='镜头平稳跟随，敌军阵墙裂开一道缝，白袍将军策马从那道缝里一冲而过直插村林，身后追兵不停，他头也不回只管催马，蹄下尘土高扬',
         lens='35mm 广角，中景深', cp='白袍将军 + 侧面平视跟随', comp='中心构图', eye='村林方向', focus='锁定奔马与扬起尘土', stab='slight-shake',
         h3='A tracking shot follows <Picture 2> across: the enemy wall splits open and the white-robed general spurts through the gap straight into the trees, pursuers unrelenting behind; he never looks back, kicking the horse faster with dust flying high from its hooves.'),
       dict(b=[26,26],sec=3,size='medium',cam='Static Shot',ch=['C11'],pr=[],
         frame='中景，赵云单手拢住襁褓，把枪横在身前，又一次荡开扑上来的乱兵，落叶被马蹄惊起',
         shot='固定镜头中景，白袍将军单手拢住襁褓，把长枪横在身前，随手一挥荡开扑上来的乱兵',
         lens='50mm 标准，中浅景深', cp='白袍将军 + 平视侧面', comp='三分法', eye='扑上来的乱兵', focus='锁定横枪荡敌的轨迹', stab='stable',
         h3='<Picture 3> holds mid-frame: with one hand clasping the bundle and the spear held crosswise, static shot, the white-robed general sweeps the shaft and knocks away a soldier lunging in.'),
       dict(b=[27,27],sec=3,size='close',cam='Static Shot',ch=['C11'],pr=[],
         frame='特写，马背上妇人勉力回头望一眼来路，又低头紧紧搂住怀里的襁褓，长长舒了口气，眉眼疲惫',
         shot='固定镜头近切，马背上的妇人艰难回头看了一眼来路，又低头把襁褓搂得更紧，长长吐出一口气',
         lens='85mm 长焦，极浅景深', cp='妇人 + 平视正面', comp='中心构图', eye='怀中的襁褓', focus='锁定妇人眉眼', stab='stable',
         h3='A static shot close-up of <Picture 4>: the woman on horseback glances back once at the road behind, then bows and clutches the swaddled child tighter, letting out a long held breath.'),
       dict(b=[28,29],sec=4,size='medium',cam='Static Shot',ch=['C11'],pr=[],
         frame='中景，赵云怒吼一句挡路者让开，随即一杆短枪扎过他肋下，血顺着甲缝淌下，他咬紧牙关没吭声仍冲杀',
         shot='固定镜头中景，白袍将军怒喝让挡路者让开，一杆短枪却扎进他肋下，血顺着甲缝往下淌，他咬着牙关一声不吭仍往前冲',
         lens='50mm 标准，中浅景深', cp='白袍将军 + 平视正面', comp='三分法', eye='挡路的敌兵', focus='锁定肋下流血仍不退的侧颈', stab='stable',
         h3='Holding <Picture 5> mid-frame, the white-robed general roars at those blocking his path; static shot — a short spear grazes under his ribs and blood runs down the armor seam, but he clenches his jaw and keeps charging without a sound: with a fierce voice (S1) he shouts: <d>[Chinese] 挡我路的，都让开！</d>'),
      ]))
    # seg7 beats30-32
    segs.append(dict(sceneId='S07',
      blocking='白袍将军在画面中央向土坎奔去，身后坡上是伞盖下统帅的远景剪影，一条尘线横贯画面。',
      soundscape='追兵声在远处渐渐拉远，马蹄放缓，风声田野，襁褓里传来一声清亮的啼哭',
      music='低音弦乐撤走大部，只留一缕张力，随啼哭声收尾',
      cuts=[
       dict(b=[30,30],sec=3,size='wide',cam='Static Shot',ch=['C11'],pr=[],
         frame='全景，赵云兜转马头，赶在合围合拢前一隙，硬生生从人缝里撕开一条路，马蹄将尘土卷成一片',
         shot='固定镜头，白袍将军猛地兜转马头，趁四面合围尚未锤拢的那道窄缝，硬生生从人缝里撕出一条去路',
         lens='35mm 广角，中景深', cp='战场全景 + 平视', comp='对角线构图', eye='合围前的窄缝', focus='锁定撕开去路的骑影', stab='stable',
         h3='The wide of <Picture 1> holds as the white-robed general reins the horse hard around and, before the ring can close, wrenches sideways and tears a path through the press; static shot, dust swept into a sheet by the hooves.'),
       dict(b=[31,31],sec=3,size='close',cam='Static Shot',ch=['C04'],pr=[],
         frame='特写，身后曹操望着那道越去越远的背影久久没有移开目光，伞影里神情复杂，欲言又止',
         shot='固定镜头近切，统帅望着那道越去越远的背影，久久没有移开目光，半张脸隐在伞影里欲言又止',
         lens='85mm 长焦，极浅景深', cp='统帅 + 平视正面', comp='三分法', eye='那道远去背影的方向', focus='锁定统帅眼神', stab='stable',
         h3='A static shot close-up of <Picture 2>: watching the fading figure grow small, the warlord holds his gaze on it for a long moment, one side of his face in the canopy shadow, as though about to speak and stopping.'),
       dict(b=[32,32],sec=4,size='extreme-wide',cam='Static Shot',ch=['C11'],pr=[],
         frame='大远景，赵云催马跃上土坎勒住嚼环四下一望，暮色烟尘里怀里的襁褓忽然传出嘤嘤啼声，他低头护住襁褓',
         shot='固定镜头远景，白袍将军催马跃上土坎勒住马环四下一望，马背上的襁褓忽然传来嘤嘤啼声，他低头伸手护住那团布包',
         lens='35mm 广角，中景深', cp='土坎远景 + 平视略仰', comp='三分法', eye='襁褓再望向四野', focus='锁定护住襁褓的手', stab='stable',
         h3='The extreme wide of <Picture 3> closes the scene: the white-robed general spurs up a dirt rise and checks the horse, scanning the smoke-veiled plain, when a thin wail rises from the bundle; static shot, he bows his head and shields the cloth with his hand.'),
      ]))
    # ---- scene2 ----
    segs.append(dict(sceneId='S07',
      blocking='林边一株枯树下，主公居左持缰立马，右侧来路上一身血的白袍将军正驰近；两人之间隔着七八步。',
      soundscape='马蹄渐近又停，风声与村林鸟儿被惊起，主公布袍窸窣下马',
      music='缓下来的低音弦乐，中慢速，透出劫后的一点暖',
      cuts=[
       dict(b=[1,1],sec=3,size='wide',cam='Static Shot',ch=['C01'],pr=[],
         frame='全景，林边一株枯树下刘备并马立着，远远望见血淋淋的赵云驰近，眼眶陡然发热，身后是隐入林的车驾',
         shot='固定镜头，一名布袍主公并马立在枯树下，远远望见一身血迹的将军驰近，眼眶一下发红，喉头动了动',
         lens='35mm 广角，中景深', cp='主公 + 平视侧面', comp='三分法', eye='来路方向', focus='锁定主公泛红的眼眶', stab='stable',
         h3='<Picture 1> frames the clearing: a lord in plain robes sits on horseback under a bare tree and, seeing the blood-soaked rider drawing near, his eyes suddenly glisten; static shot.'),
       dict(b=[2,3],sec=5,size='medium',cam='Static Shot',ch=['C01','C11'],pr=[],
         frame='中景，赵云滚鞍下马踉跄一步单膝跪地，把襁褓举到刘备面前，刘备下马趋前接住，两人相距一步',
         shot='固定镜头中景，白袍将军滚鞍下马踉跄一步单膝跪地，把襁褓高高举到主公面前；主公下马迎上一步，伸手去接',
         lens='50mm 标准，中浅景深', cp='双人 + 平视侧面', comp='三分法', eye='主公先看襁褓再看将军', focus='锁定交接襁褓的双手', stab='stable',
         h3='Holding <Picture 2> of the two men, the white-robed general slips from the saddle, stumbles and drops to one knee, lifting the bundled child toward the lord; over a static shot the lord dismounts and steps forward to receive it, and the general with a winded, loyal voice (S1) reports: <d>[Chinese] 幼主在此，末将护主来迟。</d>'),
       dict(b=[4,4],sec=4,size='close',cam='Static Shot',ch=['C01','C11'],pr=[],
         frame='特写，刘备捧过襁褓见婴儿睡得正香，悬着的心才放下，眼里的泪光被压回，指腹摩过襁褓布料',
         shot='固定镜头近切，主公捧过襁褓，见里头婴儿睡得安稳，一颗提着的心才落下，眉眼松开，指腹轻轻摩过包布的边',
         lens='85mm 长焦，极浅景深', cp='主公 + 平视正面', comp='中心构图', eye='怀中的襁褓', focus='锁定襁褓与主公眉眼', stab='stable',
         h3='A static shot close-up of <Picture 3>: holding the bundle, the lord sees the infant asleep and the tension drains from his face, thumb brushing the cloth edge, relieved.'),
      ]))
    segs.append(dict(sceneId='S07',
      blocking='二人面对面拉着距离：主公居左自持，白袍将军居右柱枪立着；换气的近景在两脸之间来回切。',
      soundscape='林间风声、怀抱薄绢的窸窣，血珠滴落的轻响，彼此的呼吸声',
      music='低音弦乐慢速流转，情绪沉郁而温暖',
      cuts=[
       dict(b=[5,5],sec=4,size='close',cam='Push In',ch=['C01'],pr=[],
         frame='特写，刘备看着赵云一身是血，声音发哽地说，眼眶又红，眉间是说不出的心疼与自责',
         shot='镜头小幅缓推，主公看着将军一身血衣，声音发哽地开口，喉咙里压着心疼，眼眶又红了一层',
         lens='85mm 长焦，极浅景深', cp='主公 + 平视正面', comp='三分法', eye='将军身上的血', focus='锁定主公泛红的眉眼', stab='stable',
         h3='A slow push in with small amplitude closes on <Picture 2>: the lord looks over the young man drenched in blood, voice catching, and with a choked, tender voice (S2) says: <d>[Chinese] 子龙，你这一身血，为的是我儿子。</d>'),
       dict(b=[6,6],sec=3,size='close',cam='Static Shot',ch=['C11'],pr=[],
         frame='特写，赵云张了张嘴没有答话，只伸手替刘备把襁褓上渗出的血珠轻轻抹去，神情疲惫而坦荡',
         shot='固定镜头近切，白袍将军张了张嘴没答话，只抬手替主公把襁褓上渗出的血珠轻轻抹掉',
         lens='85mm 长焦，极浅景深', cp='白袍将军 + 平视正面', comp='三分法', eye='襁褓上的血珠', focus='锁定拭血的手指', stab='stable',
         h3='A static shot close-up of <Picture 3>: the young general opens his mouth and says nothing, only reaches out to wipe a stray drop of blood from the cloth with a finger, weary and unguarded.'),
       dict(b=[7,8],sec=5,size='medium',cam='Static Shot',ch=['C01','C11'],pr=[],
         frame='中景，刘备垂眼看着他肋下还在渗血的伤口，眼圈又热，声音低哑地问那一句，赵云拄枪稳住发软的双腿',
         shot='固定镜头中景，主公垂眼盯着将军肋下那道还在渗血的伤口，眼圈又是一热，低哑地追问；将军拄着长枪稳住打颤的腿',
         lens='50mm 标准，中浅景深', cp='双人 + 平视侧面', comp='三分法', eye='伤口再抬向对方', focus='锁定肋下伤口', stab='stable',
         h3='Holding <Picture 4> of both men, the lord looks down at the wound still seeping under the young man\u2019s ribs and his eyes redden again; over a static shot, with a husky voice (S2) he asks: <d>[Chinese] 你这一身伤，闯了多少道关。</d>'),
      ]))
    segs.append(dict(sceneId='S07',
      blocking='近景互换：白袍将军居右喇叭裹气，主公居左抬眼望向天边尘头；两人并肩而不再面对面。',
      soundscape='风声更紧，远处尘头隐约的马蹄，将军长出一口气的呼吸声',
      music='低音弦乐稳住一个长音，中慢速，蓄着下一步的决定',
      cuts=[
       dict(b=[9,10],sec=5,size='medium',cam='Static Shot',ch=['C11'],pr=[],
         frame='中景，赵云扯了扯嘴角把长枪往地上一拄稳住发软的双腿，喘匀一口气才答，语气里是守成的一线坚持',
         shot='固定镜头中景，白袍将军扯了扯嘴角，把长枪往地上一拄稳了身子，喘匀一口气，才慢慢答上一句',
         lens='50mm 标准，中浅景深', cp='白袍将军 + 平视正面', comp='三分法', eye='主公的面容', focus='锁定将军憋着的那口气', stab='stable',
         h3='<Picture 1> holds on the young general as he steadies himself on the planted spear and catches his breath; static shot, and with a quiet, dogged voice (S1) he answers: <d>[Chinese] 全凭一口气撑着，少主平安就好。</d>'),
       dict(b=[11,11],sec=3,size='close',cam='Static Shot',ch=['C01'],pr=[],
         frame='特写，刘备替他把额上的血汗一抹，随即抬眼望向天边压过来的尘头，神色又冷了下来',
         shot='固定镜头近切，主公抬手替将军抹掉额上的血汗，随即抬眼望向外头压过来的尘头，神色一下收紧',
         lens='85mm 长焦，极浅景深', cp='主公 + 平视正面', comp='三分法', eye='天边的尘头', focus='锁定主公转冷的眼神', stab='stable',
         h3='A static shot close-up of <Picture 2>: the lord wipes the sweat and blood from the general\u2019s brow, then lifts his eyes to the dust cloud pressing down from the distance, his bearing cooling at once.'),
       dict(b=[12,12],sec=5,size='medium',cam='Static Shot',ch=['C01'],pr=[],
         frame='中景，刘备望向压近的尘头沉声道，语气是军令也是关切，示意先裹伤，眉眼凝重',
         shot='固定镜头中景，主公沉声叮嘱，风把他的袍角掀起来，语气里一半是军令一半是关切',
         lens='50mm 标准，中浅景深', cp='主公 + 平视正面', comp='三分法', eye='天边的尘头', focus='锁定主公凝重的眉眼', stab='stable',
         h3='Holding <Picture 3> on the lord, his eyes on the approaching dust, static shot, and with a grave, concerned voice (S2) he orders: <d>[Chinese] 曹军来得比风还快。先歇歇，把伤裹了。</d>'),
      ]))
    segs.append(dict(sceneId='S07',
      blocking='主公居左抱着襁褓回头望向村林外竖起的曹旗，白袍将军居右拄枪立着，两人同一朝向望向来路。',
      soundscape='村林外的马蹄与风声，襁褓传出一点声响，两人的呼吸',
      music='低音弦乐缓慢蓄势，带一丝不安的余韵',
      cuts=[
       dict(b=[13,13],sec=3,size='wide',cam='Static Shot',ch=['C11','C01'],pr=[],
         frame='全景，赵云顺着主公的目光望去，村林外的尘雾里又竖起几杆曹旗，军旗在风里猎猎',
         shot='固定镜头，白袍将军顺着主公的目光望向村林外，尘雾里又竖起几杆敌幡，在风里猎猎摆动',
         lens='35mm 广角，中景深', cp='两人 + 平视侧面', comp='三分法', eye='村林外的曹旗', focus='锁定尘雾里的旗', stab='stable',
         h3='The wide of <Picture 1> holds as the young general follows the lord\u2019s gaze; static shot, beyond the village grove a few enemy banners rise again through the dusty haze, snapping in the wind.'),
       dict(b=[14,14],sec=4,size='close',cam='Push In',ch=['C11'],pr=[],
         frame='特写，赵云把目光从敌旗上收回来，认真地看着少主，一字一句地应下这句话，语气滚烫',
         shot='镜头小幅缓推，白袍将军把目光从敌旗收回，看着怀抱的少主一字一句应下，喉结滚了滚',
         lens='85mm 长焦，极浅景深', cp='白袍将军 + 平视正面', comp='三分法', eye='襁褓里的少主', focus='锁定将军认真的神色', stab='stable',
         h3='A slow push in with small amplitude on <Picture 2>: tearing his gaze from the banners, the young general looks at the child in swaddling and answers earnestly, and with a warm, steadfast voice (S1) commits: <d>[Chinese] 少主安好，末将就没有白走这一遭。</d>'),
       dict(b=[15,16],sec=6,size='wide',cam='Static Shot',ch=['C01'],pr=[],
         frame='全景，刘备把婴儿交到身后护卫怀中，掉头望向尘雾滚滚的来路，声有牵挂地提到二弟三弟',
         shot='固定镜头，主公把婴儿交到身后一名护卫怀里，掉头望向尘雾滚滚的来路，声音里带着牵挂',
         lens='35mm 广角，中景深', cp='主公 + 平视侧面', comp='三分法', eye='尘雾滚滚的来路', focus='锁定主公望向来路的侧脸', stab='stable',
         h3='Holding the wide of <Picture 3>, the lord hands the child to a guard behind him and turns toward the rolling dust of the road; static shot, and with a worried voice (S2) he says: <d>[Chinese] 二弟三弟，还散在乱军里。</d>'),
      ]))
    segs.append(dict(sceneId='S07',
      blocking='白袍将军拄枪在右欲抬腿上马，主公主左一把按住他肋侧；背后是隐入村林的车驾与燃起的号角。',
      soundscape='马蹄欲动的窸窣，主公按住肋侧衣料摩擦，远处一声号角沉闷响起',
      music='低音弦乐一个斩钉截铁的重音，随即稳回中慢速',
      cuts=[
       dict(b=[17,17],sec=3,size='medium',cam='Static Shot',ch=['C11'],pr=[],
         frame='中景，赵云拄着长枪，一条腿就要往马镫上抬，作势要策马再杀回去寻人',
         shot='固定镜头中景，白袍将军拄着长枪，一条腿已经抬向马镫，作势就要翻身上马杀回去',
         lens='50mm 标准，中浅景深', cp='白袍将军 + 平视侧面', comp='三分法', eye='来路方向', focus='锁定抬向马镫的腿', stab='stable',
         h3='<Picture 1> holds as the young general plants the spear and lifts one leg toward the stirrup, poised to ride back; static shot.'),
       dict(b=[18,19],sec=6,size='medium',cam='Static Shot',ch=['C01','C11'],pr=[],
         frame='中景，赵云斩钉截铁承诺要去寻回二位将军，刘备一把按住他渗血的肋侧不放人，两人一个要冲一个要拦',
         shot='固定镜头，白袍将军沉声立下死诺，就要催马；主公上前一把按住他渗血的肋侧，不肯放人',
         lens='50mm 标准，中浅景深', cp='双人 + 平视侧面', comp='三分法', eye='按住肋侧的手', focus='锁定按住伤口的手', stab='stable',
         h3='Holding <Picture 2> of both men, the young general swears he will find the missing commanders no matter the cost; over a static shot the lord presses a hand firmly over the seeping ribs to hold him back, and the general with a determined voice (S1) insists: <d>[Chinese] 末将这就去寻，拼死也把二位将军带回来。</d>'),
       dict(b=[20,21],sec=5,size='medium',cam='Static Shot',ch=['C01'],pr=[],
         frame='中景，刘备斩钉截铁只让他先裹伤不许再去，话音未落，远坡头一声号角响起，曹军旌旗从尘雾露出',
         shot='固定镜头，主公一句话堵回，正说着，远处坡头骤然响起一声号角，敌军的旌旗从尘雾一角露了出来',
         lens='35mm 广角，中景深', cp='主公 + 平视正面', comp='三分法', eye='远坡头的号角方向', focus='锁定主公与远处旗影', stab='stable',
         h3='The medium of <Picture 3> holds on the lord cutting him off; static shot — just then a horn blows on the far slope and an enemy banner edge shows through the dust; the lord with a firm, sharp voice (S2) orders: <d>[Chinese] 先裹伤，不许再去。</d>'),
      ]))
    segs.append(dict(sceneId='S07',
      blocking='两人并肩立在林梢阴影下望向那条越来越近的铁流：主公居左，将军居右双手都握在兵器上。',
      soundscape='号角余音，铁蹄声由远及近越发密集，暮风卷尘土，林梢沙沙',
      music='低音弦乐稳住，速度随铁蹄渐近期显收紧，收在暮色压上来处',
      cuts=[
       dict(b=[22,23],sec=5,size='wide',cam='Static Shot',ch=['C01','C11'],pr=[],
         frame='全景，刘备上马举目望着那条越来越近的铁流眉头拧成深沟，赵云也抬头望去狠狠攥住长枪',
         shot='固定镜头，主公上马举目望着越来越近的铁流，眉头拧成一道深沟；身边的将军也抬头望向那里，双手狠狠攥紧长枪',
         lens='35mm 广角，中景深', cp='两人 + 平视略仰', comp='三分法', eye='逼近的铁流', focus='锁定两人凝望的侧影', stab='stable',
         h3='The wide of <Picture 1> holds on the two men watching the iron column draw nearer; static shot, the lord\u2019s brow knots into a deep furrow and the general beside him tightens his grip on the spear.'),
       dict(b=[24,25],sec=5,size='medium',cam='Static Shot',ch=['C01','C11'],pr=[],
         frame='中景，刘备回身看一眼立在车前的护卫老小，又望向赵云，终究没有下令启程，两人立在林梢阴影下谁也没先开口',
         shot='固定镜头，主公回头看了看车前的护卫与家小，又看了看身边的将军，终究没有下令启程；两人立在林影里沉默，谁都没先开口',
         lens='50mm 标准，中浅景深', cp='两人 + 平视侧面', comp='对称构图', eye='互相短暂交错，再看远方', focus='锁定两人相望又沉默的一瞬', stab='stable',
         h3='Holding <Picture 2> of both men, the lord glances back at the guards and dependents by the cart, then at the general, and gives no order to set out; static shot, the two stand in the grove shadow, neither speaking first.'),
       dict(b=[26,27],sec=5,size='wide',cam='Static Shot',ch=['C01','C11'],pr=[],
         frame='全景，暮色压上长坂坡，风一阵紧似一阵把道上的尘土高高卷起，远处铁蹄声越来越响，两道剪影立在营地边',
         shot='固定镜头远景，暮色压上坡头，风把道上的尘土高高卷起，远处铁蹄声越来越近，两道人影立在林边一动未动',
         lens='35mm 广角，深景深', cp='坡地远景 + 平视', comp='三分法', eye='逼来的铁蹄方向', focus='锁定暮色里的两道剪影', stab='stable',
         h3='The extreme wide of <Picture 3> closes the episode: dusk presses down over the slope and the wind whips the dust high off the road; static shot, the approaching hoofbeats grow louder while the two silhouettes stand motionless at the wood\u2019s edge.'),
      ]))
    return segs

SEG41 = E41_cuts()

# (en_sound, en_music) 按 EP41 段序排列，供 h3 使用
ENSOUND = [
 ("Chaotic shouts and hoofbeats of a rout, wind whipping grit across the road, the ring and clash of iron dulled by the dust.","Low urgent drums and strings at a brisk middle tempo, pressing under the chaos."),
 ("A muffled commotion of shouldered bodies and raised voices, one short frightened cry swallowed by hoofbeats, then the ring of blades.","A driven low percussion and string line pressing at a fast tempo."),
 ("Distant battle cries and horses from across the field, wind over the canopy, banners snapping, while the space around the warlord stays near-silent.","Low strings holding beneath at a slow tempo, allowing a pause for judgment."),
 ("Continuous hoofbeats, wind rolling over the field, distant clatter of arms and shouting, the steady stilled breath of the woman bracing herself.","Tight low drums and strings flowing evenly, forward pressure."),
 ("Rising wind, drumming hooves, the hush of cloth around the swaddled child, shouting thinning in the distance.","A low string line rising and easing with the mood, middle tempo, easing as a gap opens."),
 ("Hoofbeats tight as rain, wind rising faster, pursuers shouting at a held distance, one thin infant cry through the cloth.","A fast-tempo low-string line driving forward, tension drawn toward its peak."),
 ("Pursuit fading behind, hooves slowing, wind over open fields, one clear infant cry through the swaddling.","Low strings largely recede, a thread of tension left, softening as the cry resolves."),
 ("Hoofbeats approaching then stopping, wind and birds startled from the grove, the rustle of cloth as the lord dismounts.","Soft low strings at a moderate-slow tempo, a hint of warmth after the ordeal."),
 ("Breeze through the grove, the rub of silk cloth, a stray drip of blood, the two men breathing.","Slow flowing low strings, somber and warm."),
 ("Wind pressing harder, faint distant hoofbeats beyond the grove, the general letting out a long held breath.","Low strings steadying on a single long tone, moderate-slow, withholding a decision."),
 ("Distant hoofbeats and wind beyond the grove, the bundle giving a small sound, the two men breathing.","Low strings building slowly, a faint undertone of unease."),
 ("The stir of a foot toward the stirrup, the clutch of cloth against ribs, a dull horn sounding far off.","A decisive low-string accent, then easing back to moderate-slow."),
 ("Horn dying away, hoofbeats rolling closer and denser, dusk wind whipping dust while grove leaves hiss.","Low strings holding, tightening as the hoofbeats near, letting down as dusk settles."),
]

E42_cuts_def="""
def E42_cuts():
    s=[]
    # ==== scene1 (36 beats) ====
    s.append(dict(sceneId='S07',
      blocking='长坂桥头，一名黑甲黑袍巨汉横矛立于画面中央桥心，身后横倒一株断树；溃退的自家兵卒在画面两侧缩成一片。',
      soundscape='桥头风声，人喊马嘶的溃退声由远及近，巨汉脚下沉重的脚步声踩实桥板',
      music='低沉战鼓与弦乐随对峙顿住，速度收在中慢',
      cuts=[
       dict(b=[1,1],sec=3,size='wide',cam='Tracking Shot',ch=['C03'],pr=[],
         frame='全景，长坂桥头一圈溃兵正夺路，张飞骤马抢上来一把横过丈八蛇矛挡在桥心，环眼圆睁，尘土扬在马后',
         shot='镜头平稳跟随，一名黑甲黑袍的巨汉骤马抢上桥头，横过长矛挡在桥心，一瞪环眼把夺路的溃兵堵住',
         lens='35mm 广角，中景深', cp='黑甲巨汉 + 侧面平视跟随', comp='中心构图', eye='桥那头的溃兵', focus='锁定横矛挡桥的身影', stab='slight-shake',
         h3='The cold open follows <Picture 1>: a huge black-armored general rides up the bridgehead and swings his yard-long spear crosswise to hold the middle of the bridge, glaring at the routed men who scramble back; a tracking shot captures his advance.' ),
       dict(b=[2,3],sec=5,size='wide',cam='Static Shot',ch=['C03'],pr=[],
         frame='全景，张飞回手倒拔桥头那株大树，连根带土横在桥面上封死来路，随即把蛇矛往地上一拄立于树后',
         shot='固定镜头，黑甲巨汉回身一把倒拔起桥头的大树，连根带土横在桥面封住来路，再把长矛往地上一拄，立在树后',
         lens='35mm 广角，中景深', cp='黑甲巨汉 + 平视侧面', comp='对角线构图', eye='横上的断树再扫向桥那头', focus='锁定倒拔大树的双手', stab='stable',
         h3='Holding <Picture 2>, the general with one motion yanks up the roadside tree, roots and earth, and lays it across the bridge to block the way; static shot, then plants the spear into the ground and stands behind the fallen trunk.'),
       dict(b=[4,4],sec=3,size='close',cam='Static Shot',ch=['C03'],pr=[],
         frame='特写，张飞立于断树后环眼圆睁扫过败兵，声如炸雷地暴喝出那句，胡须在风里根根竖起',
         shot='固定镜头近切，黑甲巨汉圆睁环眼扫过缩在一边的败兵，猛地一声炸雷般暴喝',
         lens='85mm 长焦，极浅景深', cp='黑甲巨汉 + 平视正面', comp='三分法', eye='桥头的败兵', focus='锁定张开的虎口', stab='stable',
         h3='The close-up of <Picture 3> holds on the giant glaring at the routed men; static shot, and the black-armored general with a thunderous, roaring voice (S1) bellows: <d>[Chinese] 有某家在此，谁敢撞桥！</d>'),
      ]))
    s.append(dict(sceneId='S07',
      blocking='桥心是巨汉独立的身影，桥那头尘烟一滚压到河边，一队曹军骑将勒马在近景。',
      soundscape='马蹄声由远及近压到河边，桥板被踩得吱呀，风卷旗角的猎猎声',
      music='撞钟般的低音鼓点一下一下，速度压沉',
      cuts=[
       dict(b=[5,6],sec=5,size='wide',cam='Static Shot',ch=['C03'],pr=[],
         frame='全景，几名想逃的兵卒被这一声镇住直往村林缩，糜竺、赵云护送车驾从桥那边退来，张飞抬手让他们先行过桥',
         shot='固定镜头，几名溃兵被一声震住往村林缩；桥那头一队护着车驾的兵卒退来，黑甲巨汉抬手放他们先行过桥',
         lens='35mm 广角，中景深', cp='桥头全景 + 平视', comp='三分法', eye='退来的车驾', focus='锁定抬手放行的巨汉', stab='stable',
         h3='Under <Picture 2> a few routed men shrink toward the grove; over a static shot a guarded carriage retreats across from the far end and the black-armored general lifts a hand to wave them on first.'),
       dict(b=[7,8],sec=5,size='wide',cam='Static Shot',ch=['C03'],pr=[],
         frame='全景，桥那头尘烟一滚，曹军旗幡猎猎潮水一般压到河边，张飞单人一马横矛立于桥头，身后桥面躺着断树',
         shot='固定镜头，桥那头尘烟一滚，敌军的旗幡潮水般压到河边；黑甲巨汉单人匹马横矛守在桥头，身后是那道断树',
         lens='35mm 广角，深景深', cp='桥头全景 + 平视', comp='三分法', eye='潮水般压来的曹军', focus='锁定一人一马守桥的剪影', stab='stable',
         h3='The wide of <Picture 3>: dust rolls on the far bank as enemy banners surge like a tide to the river; static shot, the single black-armored figure holds the bridgehead with spear gripped, the felled tree lying behind.'),
       dict(b=[9,9],sec=3,size='medium',cam='Static Shot',ch=['C03'],pr=[],
         frame='中景，前头的曹军勒住马脚，不敢贸然踏上木板桥，你看我我看你互相张望，桥板吱吱作响',
         shot='固定镜头，前头的敌骑勒住马脚停住，互相张望，谁也不敢贸然踩上那块木板桥',
         lens='50mm 标准，中浅景深', cp='前阵曹军 + 平视正面', comp='三分法', eye='桥头的巨汉', focus='锁定犹豫不前的战马', stab='stable',
         h3='Holding <Picture 4> on the front ranks, the enemy riders rein in and hesitate, none daring to step onto the plank bridge; static shot.'),
      ]))
    s.append(dict(sceneId='S07',
      blocking='巨汉在桥心正面近景起手，两侧桥那头的曹军勒马远远观望。',
      soundscape='满阵兵马被喝得一阵骚动，马匹打响鼻蹬蹄后退，风声更紧',
      music='一声炸雷后鼓点骤歇，留一段低音弦的余震',
      cuts=[
       dict(b=[10,11],sec=4,size='close',cam='Static Shot',ch=['C03'],pr=[],
         frame='特写，张飞圆睁环眼直入中军处那杆牙旗，一声暴喝炸开，胡须戟张，声浪仿佛震得空气发晃',
         shot='固定镜头近切，黑甲巨汉圆睁环眼，目光直贯中军那杆大旗，一声暴喝炸响在整片阵前',
         lens='85mm 长焦，极浅景深', cp='黑甲巨汉 + 平视正面', comp='三分法', eye='中军牙旗方向', focus='锁定暴喝时张开的虎口', stab='stable',
         h3='A static shot close-up of <Picture 1>: the giant stares dead at the command banner and lets a shout explode across the field, and the black-armored general with a voice like a thunderclap roars: <d>[Chinese] 我乃燕人张翼德！</d>'),
       dict(b=[12,13],sec=5,size='medium',cam='Static Shot',ch=['C03'],pr=[],
         frame='中景，满阵列兵闻声一凛，马匹惊得往后蹶，有曹兵想摸上来探路只走上两步又缩了回去',
         shot='固定镜头，满阵兵卒被一声喝得发凛，马匹惊得往后退蹶；一名探路的敌兵走上两步，又被吓缩了回去',
         lens='50mm 标准，中浅景深', cp='阵前曹军 + 平视侧面', comp='三分法', eye='怯退的兵与马', focus='锁定惊蹶的马匹', stab='stable',
         h3='Holding <Picture 2>, the ranks flinch and horses start backward at the shout; over a static shot a scout edges two steps forward then flinches back.'),
       dict(b=[14,15],sec=5,size='close',cam='Static Shot',ch=['C03'],pr=[],
         frame='特写，张飞把断树又往前挪了半尺，树根扎进桥板死死封住来路，随即沉声压阵说出那句',
         shot='固定镜头，黑甲巨汉把断树往前挪了挪，树根扎进桥板，随即沉声压下一句威喝',
         lens='85mm 长焦，极浅景深', cp='黑甲巨汉 + 平视正面', comp='三分法', eye='桥那头的曹军', focus='锁定顿矛的双手', stab='stable',
         h3='A static shot close-up of <Picture 3>: the giant shoves the fallen tree half a step forward, rooting it into the planks, and the black-armored general with a heavy, intimidating voice (S1) warns: <d>[Chinese] 我有铁矛在此，谁敢近前！</d>'),
      ]))
    s.append(dict(sceneId='S07',
      blocking='自家兵卒在桥心巨汉身后排成一列壮胆，桥那头尘头又起，一骑曹将远远策马出列。',
      soundscape='自家兵卒压低的应和，桥那头大队人马开拔的动静，尘土与风声',
      music='低音弦乐托起，添一分对峙的拉扯感',
      cuts=[
       dict(b=[16,16],sec=3,size='wide',cam='Static Shot',ch=['C03'],pr=[],
         frame='全景，张飞身后几名自家兵卒壮着胆子直起腰，站到他背后排成一排，握紧手中长枪',
         shot='固定镜头，黑甲巨汉身后几名自家兵卒壮着胆子直起腰，在他背后排成一排，攥紧手中长枪',
         lens='35mm 广角，中景深', cp='桥头侧景 + 平视', comp='对称构图', eye='前方桥那头', focus='锁定排成一排的兵卒', stab='stable',
         h3='The wide of <Picture 1> holds: a few of the routed men straighten up and line up behind the giant, gripping their spears; static shot.'),
       dict(b=[17,18],sec=5,size='medium',cam='Static Shot',ch=['C03'],pr=[],
         frame='中景，正对峙间桥那头尘头又起像有大队人马开拔，一名曹将策马出列远远拱手喊话问话',
         shot='固定镜头，对峙中桥那头尘头又起，一骑敌将策马出列，远远拱了拱手，扬声道出一句问话',
         lens='50mm 标准，中浅景深', cp='敌将 + 平视正面', comp='三分法', eye='桥头的巨汉', focus='锁定策马出列的敌将', stab='stable',
         h3='Holding <Picture 2>, a new dust column rises on the far bank as a force stirs; over a static shot one enemy rider spurs out, clasps his hands across the distance and calls a question.'),
       dict(b=[19,20],sec=5,size='close',cam='Static Shot',ch=['C03'],pr=[],
         frame='特写，张飞也不答话把蛇矛往地上一顿钉出半尺深，才冷冷开口报上名姓又问来者，气势压人',
         shot='固定镜头近切，黑甲巨汉不答话，把长矛往地上一顿钉出半尺深，才冷冷开口，声音沉得像滚雷',
         lens='85mm 长焦，极浅景深', cp='黑甲巨汉 + 平视正面', comp='三分法', eye='桥那头敌将', focus='锁定钉矛震起的一动', stab='stable',
         h3='A static shot close-up of <Picture 3>: instead of answering, the giant slams the spear into the ground half a foot deep, then speaks coldly, and the black-armored general with a low, rolling voice (S1) answers: <d>[Chinese] 正是！来者何人，报上名来。</d>'),
      ]))
    s.append(dict(sceneId='S07',
      blocking='桥心巨汉正面占主导，桥那头那将勒马缩回阵里，自家兵卒在侧。',
      soundscape='敌将回阵时马镫碰撞，桥那头一片低低的骚动，风声灌满桥间',
      music='低音弦乐一个紧箍的重音，再松一扣',
      cuts=[
       dict(b=[21,22],sec=5,size='medium',cam='Static Shot',ch=['C03'],pr=[],
         frame='中景，那曹将闻声一凛勒马回阵竟不敢再近前一步，张飞见对方退回去，环眼一眯把矛一横稳稳立在桥心',
         shot='固定镜头，那骑敌将闻声一凛，勒马缩回阵里不敢再近前；黑甲巨汉见对方退去，眯了眯环眼横矛稳稳立在桥心',
         lens='50mm 标准，中浅景深', cp='桥头侧景 + 平视', comp='三分法', eye='缩回的敌将', focus='锁定横矛立桥的巨汉', stab='stable',
         h3='Holding <Picture 1>, the enemy rider flinches and wheels back without coming near; over a static shot the black-armored general narrows his eyes and plants the spear firmly at mid-bridge.'),
       dict(b=[23,24],sec=5,size='close',cam='Static Shot',ch=['C03'],pr=[],
         frame='特写，桥那头曹军阵脚一阵松动有人悄悄拨马往后退，张飞沉声把话钉死在桥面，气势如山',
         shot='固定镜头，桥那头敌阵一阵松动，有人悄悄拨马后退；近前，黑甲巨汉沉声把这话钉在桥面',
         lens='85mm 长焦，极浅景深', cp='黑甲巨汉 + 平视正面', comp='三分法', eye='后退的曹军', focus='锁定沉声开口的巨汉', stab='stable',
         h3='A static shot close-up of <Picture 2>: behind the far bank the enemy line loosens and a few quietly turn back; the black-armored general, with a voice that pins the words to the bridge, says: <d>[Chinese] 今日桥在人在，桥断也得我来断！</d>'),
       dict(b=[25,25],sec=3,size='wide',cam='Static Shot',ch=['C03'],pr=[],
         frame='全景，张飞话落，一圈自家兵卒跟着发出一声应和，反把曹军惊得又退了两步，声浪在桥头回荡',
         shot='固定镜头，巨汉话落，身后一圈兵卒跟着齐声应和，竟把桥那头的敌兵惊得又退了两步',
         lens='35mm 广角，中景深', cp='桥头全景 + 平视', comp='三分法', eye='惊退的曹军', focus='锁定齐声道和的一片', stab='stable',
         h3='The wide of <Picture 3> holds as the men behind the giant roar in unison after his words, startling the enemy back two more steps; static shot.'),
      ]))
    s.append(dict(sceneId='S07',
      blocking='巨汉翻身坐回断树根上跷着腿等敌先动，桥那头整片曹军被压得不敢向前。',
      soundscape='长矛拄桥的一声闷响，人坐下时甲叶轻响，风吹旗角与桥那头细碎的骚动',
      music='一段颇有跋扈气味的中音弦乐，速度不紧不慢',
      cuts=[
       dict(b=[26,27],sec=5,size='medium',cam='Static Shot',ch=['C03'],pr=[],
         frame='中景，张飞翻身下马把长矛往桥面一拄就势坐在树根上跷着腿等敌先动，这一坐反把桥那头的曹军看得更不敢向前挪动半步',
         shot='固定镜头，黑甲巨汉翻身下马，把长矛往桥面一拄，就势坐在断树根上跷起腿，等桥那头的敌人先动',
         lens='50mm 标准，中浅景深', cp='黑甲巨汉 + 平视侧面', comp='三分法', eye='桥那头的曹军', focus='锁定霸气坐姿的巨汉', stab='stable',
         h3='Holding <Picture 1>, the giant dismounts, props his spear on the planks and sits back on the tree root with one leg crossed, waiting; static shot, and the more relaxed he looks the less the enemy dares move.'),
       dict(b=[28,29],sec=5,size='close',cam='Static Shot',ch=['C03'],pr=[],
         frame='特写，等了半晌桥那头还是无人应声只听得风吹旗角，张飞向前倾身把那句喝出去，声音里全是笃定',
         shot='固定镜头近切，半晌桥那头无人应声，黑甲巨汉向前欠了欠身，把这话不急不缓地喝出去',
         lens='85mm 长焦，极浅景深', cp='黑甲巨汉 + 平视正面', comp='三分法', eye='桥那头的空场', focus='锁定开口的巨汉', stab='stable',
         h3='A static shot close-up of <Picture 2>: after a long silence only the flag wind answers, and the black-armored general leans forward and, with an unhurried, sure voice (S1), says: <d>[Chinese] 没人敢来，便都给我退下去！</d>'),
       dict(b=[30,31],sec=5,size='wide',cam='Static Shot',ch=['C03'],pr=[],
         frame='全景，张飞这话一落桥头排头的几骑曹军竟真个悄悄往后退了退，一场对峙硬生生被他这一坐一喝消磨得没了声气',
         shot='固定镜头，这话一落，桥头排头的几骑敌兵竟真的悄悄退了退；一场剑拔弩张的对峙，被他这一坐一喝消磨得没了声气',
         lens='35mm 广角，深景深', cp='桥头全景 + 平视', comp='对角线构图', eye='悄悄后退的骑兵', focus='锁定消弭气焰的桥头对峙', stab='stable',
         h3='The wide of <Picture 3> closes the standoff: at his words the front riders really do edge back a little, and a tense confrontation is worn down to nothing by one man sitting and shouting; static shot.'),
      ]))
    s.append(dict(sceneId='S07',
      blocking='巨汉在桥心收势，侧耳听桥那头越退越远的蹄声，嘴角难得勾起来；前阵曹军隐隐骚动往回缩。',
      soundscape='桥那头蹄声渐渐远去，桥板吱呀，风把旗角吹得扑扑响',
      music='一声松了口气的短促弦乐滑音，收在快意里',
      cuts=[
       dict(b=[32,32],sec=3,size='close',cam='Static Shot',ch=['C03'],pr=[],
         frame='特写，张飞侧头听着桥那头越退越远的蹄声，嘴角终于勾出一点弧度，环眼里是压实阵脚的笃定',
         shot='固定镜头近切，黑甲巨汉侧耳听着桥那头越退越远的蹄声，嘴角终于微微一勾',
         lens='85mm 长焦，极浅景深', cp='黑甲巨汉 + 平视正侧面', comp='三分法', eye='远去的蹄声方向', focus='锁定勾起的嘴角', stab='stable',
         h3='A static shot close-up of <Picture 1>: listening to the retreating hoofbeats fade across the bridge, the black-armored general finally lets the corner of his mouth lift a degree.'),
       dict(b=[33,34],sec=5,size='medium',cam='Static Shot',ch=['C03'],pr=[],
         frame='中景，张飞长矛往桥面一顿喝了那句，桥头当先几员曹将听罢你望我望我竟没有一个敢催马近前',
         shot='固定镜头，黑甲巨汉把长矛往桥面一顿，扬声道出这句；桥头当先几员敌将你望我我望你，竟没有一人敢催马',
         lens='50mm 标准，中浅景深', cp='黑甲巨汉 + 平视正面', comp='三分法', eye='桥头的敌将们', focus='锁定顿矛的一瞬', stab='stable',
         h3='Holding <Picture 2>, the general pounds the spear and raises his voice; static shot, and the black-armored general with a bold, demanding voice (S1) calls: <d>[Chinese] 哪个敢来，与我决一死战！</d>'),
       dict(b=[35,36],sec=4,size='wide',cam='Static Shot',ch=['C03'],pr=[],
         frame='全景，张飞又是一声喝整条河桥都在声浪里微微发颤，前阵曹军隐隐骚动竟有往回缩的势头',
         shot='固定镜头，巨汉又是一声喝，整座河桥都在声浪里颤了颤；前阵敌兵隐隐骚动，竟起了往回缩的势头',
         lens='35mm 广角，深景深', cp='桥头全景 + 平视', comp='三分法', eye='骚动向缩的敌阵', focus='锁定震得发颤的桥面', stab='stable',
         h3='The wide of <Picture 3> ends the scene: one more roar from the giant sets the whole bridge trembling in the sound wave, and the front enemy ranks begin to stir and shrink back; static shot.'),
      ]))
    # ==== scene2 (25 beats) ====
    s.append(dict(sceneId='S07',
      blocking='后阵坡上，统帅骑在伞盖下居左远望桥头，几名亲将谋士在他身侧靠后；一骑敌将出列报话。',
      soundscape='坡上风与旌旗声，桥头喊声远远传来，马镫与甲叶的轻响',
      music='低音弦乐沉下又抬起的试探音，速度慢',
      cuts=[
       dict(b=[1,2],sec=5,size='medium',cam='Static Shot',ch=['C04'],pr=[],
         frame='中景，高坡上曹操列马远望桥头那道黑塔似的身影神色凝重，缓缓开口问身边左右此人是谁',
         shot='固定镜头，统帅骑在坡上远望桥头那道黑塔似的身影，神色凝重，缓缓开口向左右发问',
         lens='50mm 标准，中浅景深', cp='统帅 + 平视正侧面', comp='三分法', eye='桥头的身影', focus='锁定凝重的眉眼', stab='stable',
         h3='Holding <Picture 1> on the slope, the warlord sits his horse gazing at the dark tower of a figure at the bridgehead; static shot, and with a grave, curious voice (S1) he asks: <d>[Chinese] 此人是谁，竟这般勇猛？</d>'),
       dict(b=[3,4],sec=5,size='close',cam='Static Shot',ch=['C04'],pr=[],
         frame='特写，左右报上桥头立的是张飞张翼德，曹操若有所思，又低声自问一句身后的虚实',
         shot='固定镜头近切，左右报上桥头那人的名姓；统帅若有所思，低声把心里的顾虑说出来',
         lens='85mm 长焦，极浅景深', cp='统帅 + 平视正面', comp='三分法', eye='桥头那片村林', focus='锁定统帅游移的眼神', stab='stable',
         h3='A static shot close-up of <Picture 2>: the attendants give the name of the man holding the bridge, and the warlord muses aloud, with a low, weighing voice (S1) wondering: <d>[Chinese] 不知他身后有没有伏兵。</d>'),
       dict(b=[5,5],sec=5,size='wide',cam='Static Shot',ch=['C04'],pr=[],
         frame='全景，曹操抚须不语望着桥那头的村林，树影里似有旗角一闪而过，他眯了眯眼',
         shot='固定镜头，统帅抚须不语，望着桥那头那片村林，树影里似有旗角一闪，他眯起眼又看了一遍',
         lens='35mm 广角，深景深', cp='统帅与坡景 + 平视', comp='三分法', eye='村林树影', focus='锁定树影里那一闪的旗角', stab='stable',
         h3='The wide of <Picture 3> holds as the warlord strokes his beard without a word, eyeing the grove beyond the bridge where a banner edge seems to flicker; static shot, he narrows his eyes.'),
      ]))
    s.append(dict(sceneId='S07',
      blocking='统帅居左，几名亲将与谋士在他身侧靠后轮番低声相劝，桥头那株断树与林影是反复打量之处。',
      soundscape='坡上低低的议论声，旌旗猎猎，桥那头林间静得没有一声鸟叫',
      music='低音弦乐一个未落的悬音，透着要不要冒进的权衡',
      cuts=[
       dict(b=[6,7],sec=5,size='medium',cam='Static Shot',ch=['C04'],pr=[],
         frame='中景，几名亲将上前请战，曹操抬手压住没让他们轻动，又眯眼看了半晌侧耳听桥那头林间静得没有一声鸟叫',
         shot='固定镜头，几名亲将上前请战，统帅抬手压住不让他们轻动，又眯眼看了半晌，侧耳去听桥那头的动静',
         lens='50mm 标准，中浅景深', cp='统帅与亲将 + 平视侧面', comp='三分法', eye='桥头村林', focus='锁定压住人的那只手', stab='stable',
         h3='Holding <Picture 1>, a few commanders offer to advance but the warlord raises a hand to hold them still, listening toward the silent grove; static shot.'),
       dict(b=[8,9],sec=5,size='medium',cam='Static Shot',ch=['C04'],pr=[],
         frame='中景，曹操身后谋士也低声相劝，说桥头恐有伏兵不可轻进，曹操沉吟片刻才接上那句判定',
         shot='固定镜头，身后谋士低声相劝，说桥头恐有伏兵冒进不得；统帅沉吟片刻，才接上这句判定',
         lens='50mm 标准，中浅景深', cp='统帅 + 平视正侧面', comp='三分法', eye='桥头的断树与林影', focus='锁定沉吟的神色', stab='stable',
         h3='A static shot holds <Picture 2>: an adviser behind cautions against rushing in and risking an ambush, and after a moment the warlord, with a weighing voice (S1), delivers his read: <d>[Chinese] 桥短树横，寻常人守不下来。</d>'),
       dict(b=[10,11],sec=5,size='medium',cam='Static Shot',ch=['C04'],pr=[],
         frame='中景，曹操来回踱了两步，目光在断树和林影间反复移掠迟迟拿不定主意，终于低声下令撤免得中伏',
         shot='固定镜头，统帅来回踱了两步，目光在那株断树与村林间反复移掠，迟迟拿不定主意，才低声吐出那个字',
         lens='50mm 标准，中浅景深', cp='统帅 + 平视正侧面', comp='三分法', eye='断树与林影', focus='锁定定下心来的眼神', stab='stable',
         h3='Holding <Picture 3>, the warlord paces two steps, eyes moving between the felled tree and the grove and failing to settle, before he makes up his mind; static shot, and with a low, decided voice (S1) he orders: <d>[Chinese] 撤。免得中伏。</d>'),
      ]))
    s.append(dict(sceneId='S07',
      blocking='桥那头的曹军一整片往后退潮，桥心巨汉纵马逼近喝声再起，溃兵挤过断树仓皇逃。',
      soundscape='退潮的嘈杂与马蹄，一声暴喝炸开，断树绊倒奔跑溃兵的闷响',
      music='低音弦乐随撤退收宽，留一段余响',
      cuts=[
       dict(b=[12,13],sec=5,size='wide',cam='Static Shot',ch=['C04'],pr=[],
         frame='全景，曹操一声令下曹军旗号一收大队人马如退潮一般一寸一寸往后撤，桥头的张飞见敌阵松动纵马又逼近两步',
         shot='固定镜头，统帅令下，敌军的旗号一收，大队人马如退潮般一寸寸后撤；桥心的黑甲巨汉见阵势松动，纵马又逼近两步',
         lens='35mm 广角，深景深', cp='桥头全景 + 平视', comp='三分法', eye='退潮的后撤', focus='锁定收旗与逼近的一人一马', stab='stable',
         h3='The wide of <Picture 1> held: at the order the banners fold and the mass recedes like a tide; over a static shot the black-armored giant sees the line loosen and spurs up another two strides.'),
       dict(b=[14,15],sec=5,size='medium',cam='Static Shot',ch=['C03'],pr=[],
         frame='中景，张飞纵马逼近又是一声暴喝，曹军兵卒掉头就跑，桥前转瞬让出一大片空场',
         shot='固定镜头，黑甲巨汉纵马逼近一声暴喝，敌兵掉头就跑，桥前转眼让出一大片空地',
         lens='50mm 标准，中浅景深', cp='黑甲巨汉 + 平视正面', comp='三分法', eye='掉头跑的曹军', focus='锁定逼向前的战马', stab='stable',
         h3='Holding <Picture 2>, the giant spurs forward and roars again; static shot, and the black-armored general with a commanding voice (S2) shouts: <d>[Chinese] 张翼德在此，谁来送死！</d>'),
       dict(b=[16,17],sec=5,size='medium',cam='Static Shot',ch=['C03'],pr=[],
         frame='中景，张飞并不追赶只把矛往地上一拄守住这半座独桥，一名溃兵跑得太急被断树绊了一跤挣扎爬起来又跑',
         shot='固定镜头，黑甲巨汉并不追赶，只把长矛往地上一拄守住半座独桥；一名溃兵跑得急，被断树绊了一跤，又挣扎爬起再跑',
         lens='50mm 标准，中浅景深', cp='桥头侧景 + 平视', comp='三分法', eye='绊倒又爬起的溃兵', focus='锁定拄矛守桥的身影', stab='stable',
         h3='Under <Picture 3>, the giant does not pursue but plants the spear and guards the half bridge; over a static shot a fleeing soldier trips on the tree root and scrambles up to run on.'),
      ]))
    s.append(dict(sceneId='S07',
      blocking='桥头剩巨汉一人拄矛独立，低头去看断树树根，又回望车驾隐入村林，独马做最后收势。',
      soundscape='溃退远去的人声，风卷桥板，巨汉吐出一口长气的鼻息，树根被扯动时泥土簌簌',
      music='低音弦乐松下来，送这一场收束散场',
      cuts=[
       dict(b=[18,19],sec=6,size='wide',cam='Static Shot',ch=['C03'],pr=[],
         frame='全景，张飞望着那一片溃退的人影吐出一口浊气，绷紧的肩背这才松了半分，又望着黑压压溃下去的铁流慢慢吐出一口长气',
         shot='固定镜头，黑甲巨汉望着那一片溃退的人影吐出一口浊气，绷紧的肩背松了半分，再望着铁流溃下去，慢慢吐出一口长气',
         lens='35mm 广角，深景深', cp='黑甲巨汉 + 平视侧面', comp='三分法', eye='溃退的铁流', focus='锁定松下来的一线肩背', stab='stable',
         h3='Holding <Picture 1>, the giant watches the receding crowd and lets the stale tension out of his shoulders; static shot, then blows out a long breath as the iron column floods away.'),
       dict(b=[20,20],sec=3,size='extreme-close',cam='Static Shot',ch=['C03'],pr=[],
         frame='大特写，张飞低头去看那株断树，树根上还带着新鲜的泥土，桥身在他独臂之下微微发晃',
         shot='固定镜头插入特写，巨汉低头看着那株断树，树根带着新泥，桥板在力压之下微微发颤',
         lens='100mm 微距，极浅景深', cp='断树树根 + 平视', comp='中心构图', eye='带着新泥的树根', focus='锁定树根与颤动的桥板', stab='stable',
         h3='An extreme-close insert of <Picture 2>: the giant looks down at the felled tree, fresh earth clinging to its roots; static shot, the bridge planks quivering slightly under the pressure. '),
       dict(b=[21,22],sec=6,size='medium',cam='Tracking Shot',ch=['C03'],pr=[],
         frame='中景，张飞回头见自家车驾已隐入桥后村林，夹马腹拨马跃过断木，马过桥心忽然顿住侧耳去听那道空了桥面没有追兵响动',
         shot='镜头小幅跟移，黑甲巨汉回头见自家车驾已隐入村林，夹紧马腹拨马跃过断木；到桥心忽又顿住，侧耳去听那道空掉的桥面',
         lens='50mm 标准，中浅景深', cp='黑甲巨汉 + 侧面平视跟随', comp='三分法', eye='空掉的桥面', focus='锁定顿住侧耳的一瞬', stab='stable',
         h3='A tracking shot follows <Picture 3>: seeing his own carts vanish into the grove, the giant spurs the horse over the fallen trunk, checks mid-bridge and cocks an ear at the suddenly empty bridge behind — no sound of pursuit.'),
      ]))
    s.append(dict(sceneId='S07',
      blocking='巨汉回望坡后那道未散的旗影，压下不安扬鞭催马，最后没入村林深处，把空桥抛在身后。',
      soundscape='回望时风声，扬鞭的一响，马匹没入村林的蹄声由近及远',
      music='低音弦乐送别般渐低，收在暮色里',
      cuts=[
       dict(b=[23,24],sec=6,size='wide',cam='Static Shot',ch=['C03'],pr=[],
         frame='全景，张飞回望坡后那道迟迟未散的旗影，眉头不由得皱了一皱，压下心头那点不安扬鞭催马没入村林深处',
         shot='固定镜头，黑甲巨汉回望坡后那道迟迟未散的旗影，眉头皱了一皱，压下心头那点不安，扬鞭催马钻进村林',
         lens='35mm 广角，深景深', cp='桥头村口 + 平视', comp='三分法', eye='坡后那道旗影', focus='锁定回望皱眉的巨汉', stab='stable',
         h3='Holding <Picture 1>, the giant glances back at the stubborn flag shadow on the slope and a line forms between his brows; static shot, he suppresses the unease and whips the horse into the grove.'),
       dict(b=[25,25],sec=5,size='wide',cam='Tracking Shot',ch=['C03'],pr=[],
         frame='全景，张飞催马扬鞭冲入村林，把那座空桥彻底抛在身后，树影把他一点一点吞没',
         shot='镜头平稳跟随，黑甲巨汉催马扬鞭冲进村林，把那座空桥彻底甩在身后，树影一点一点将他吞没',
         lens='35mm 广角，深景深', cp='黑甲巨汉 + 背后平视跟随', comp='中心构图', eye='桥的反方向村林深处', focus='锁定没入林影的骑影', stab='stable',
         h3='A tracking shot follows <Picture 2> as the black-armored general spurs into the grove and leaves the empty bridge far behind, the tree shadows closing over him one layer at a time.'),
      ]))
    return s
"""
exec(E42_cuts_def)  # 定义 E42_cuts
SEG42 = E42_cuts()

# (en_sound, en_music) 按 EP42 段序排列（12 段）
ENSOUND_42 = [
 ("Routed shouts and scrambling feet on the bridgehead, the whoosh of a spear swung crosswise, wind and bare earth underfoot.","Low battle drums and a martial string figure, mid-slow and grounded."),
 ("Hoofbeats rolling up to the river, planks groaning under weight, banners snapping in the wind.","Heavy bell-like drumbeats, one after another, pressing low."),
 ("The ranks stirring and horses squealing back a step, wind pressing harder across the bridge.","A thunderclap, then the drums drop into a low-string rumble."),
 ("Muffled straightened voices of the redoubled men behind the giant, a mass stirring on the far bank, dust and wind.","Low strings lifting, adding a slow pull of tension."),
 ("Horses backing step by step as the enemy line loosens, the wind filling the empty span.","A tightened low-string accent, then easing back a notch."),
 ("A dull thud as the spear plants on the planks, the creak of armor as he sits on the root, wind and stray stirrings from across the river.","A roguish, strutting middle-string phrase, unhurried in pace."),
 ("Hoofbeats fading away across the bridge, planks creaking, banners batting in the wind.","A short relieved string slur, resolving into a wry calm."),
 ("Wind and banners on the high slope, the distant roar from the bridgehead, the light clink of stirrups and armor.","Low strings sinking then rising on a probing note, slow."),
 ("Low murmured counsel on the slope, banners snapping, the grove beyond the bridge deathly still.","An unresolved low-string suspension, weighing whether to press forward."),
 ("The clamor of ebbing retreat and hooves, a shout exploding over the span, the soft thud of a soldier tripping on the tree root.","Low strings broadening with the retreat, a fading echo left behind."),
 ("Voices of the rout receding far off, wind over the planks, the giant blowing out a long held breath, dirt slipping from the roots.","Low strings relaxing, sending the scene toward a close."),
 ("Wind as he glances back at the stubborn flag, one sharp whip crack, the horse fading into the grove.","Low strings receding in farewell, sinking into the dusk."),
]

def assemble(epnum, segdatums, ensound, music_default_na=False):
    out=[]
    scene_idx=0; prev_start=None
    for i,segdatum in enumerate(segdatums,1):
        start = segdatum['cuts'][0]['b'][0]
        if i==1 or start==1:
            scene_idx += 1  # 每场首段都以节拍1起；同场后续段起始>1
        enS, enM = ensound[i-1] if i-1 < len(ensound) else (ensound[-1][0], 'N/A')
        out.append(build_segment(epnum, scene_idx, i,
                                 segdatum['blocking'], enS, enM,
                                 segdatum['soundscape'], segdatum.get('music'),
                                 segdatum['cuts']))
        prev_start=start
    return out

def segSeconds(seg): return sum(seg['cuts'][j]['seconds'] for j in range(len(seg['cuts'])))

outseg=assemble(EPN, SEG41, ENSOUND)

if '--write41' in sys.argv:
    test = {"source": orig["source"], "promptLang": "en", "params": orig["params"],
            "episodes": [{"ep": 41, "segments": outseg}]}
    with open('_test41.json','w',encoding='utf-8') as f:
        json.dump(test, f, ensure_ascii=False, indent=2)
    print("wrote _test41.json")

print("EP41 segments:", len(outseg), "total(s):", round(sum(segSeconds(s) for s in outseg),1), "scene:", [s['sceneIndex'] for s in outseg])

if '--write42' in sys.argv:
    out42 = assemble(42, SEG42, ENSOUND_42)
    test42 = {"source": orig["source"], "promptLang": "en", "params": orig["params"],
              "episodes": [{"ep": 42, "segments": out42}]}
    with open('_test42.json', 'w', encoding='utf-8') as f:
        json.dump(test42, f, ensure_ascii=False, indent=2)
    print("wrote _test42.json")
    print("EP42 segments:", len(out42), "total(s):", round(sum(segSeconds(s) for s in out42),1), "scene:", [s['sceneIndex'] for s in out42])

# =====================================================================
# EP 43  (scene1 江面月夜 S09: C05 孔明, C13 鲁肃)  (scene2 厅堂 S08: C13,C05,C14 孙权)
# =====================================================================
def E43_cuts():
    s=[]
    # ---- scene1 江面 ----
    s.append(dict(sceneId='S09',
      blocking='江上大雾，一叶扁舟破浪急行：白袍谋士居前立于船头，魁梧文官在舱口偏后，一前一后错开半步。',
      soundscape='江风撕掠衣角，船底破浪的水声，远处江岸灯火里隐约的人声',
      music='低沉弦乐压在雾面上，中慢速，视野开阔',
      cuts=[
       dict(b=[1,2],sec=5,size='medium',cam='Tracking Shot',ch=['C05'],pr=[],
         frame='中景，江面大雾一叶扁舟压着浪尖急行，孔明立在船头，衣角被江风撕得猎猎作响，望向前方灯火昏黄的江东岸',
         shot='镜头平稳跟随，一名白袍谋士立在船头，衣角被风撕得猎猎，目光凝向前方灯火昏黄的岸',
         lens='35mm 广角，中景深', cp='白袍谋士 + 侧后方平视跟随', comp='中心构图', eye='前方的江东岸', focus='锁定白袍谋士与翻卷衣角', stab='slight-shake',
         h3='The cold open follows <Picture 1>: a single small boat lunges over the wave crests through thick fog, the white-robed sagely strategist standing at the bow with his robe torn and snapping in the river wind, gaze fixed on the dimly lit far shore; a tracking shot holds him from behind.'),
       dict(b=[3,3],sec=3,size='close',cam='Static Shot',ch=['C05'],pr=[],
         frame='特写，船身一颠浪花溅上船舷，孔明不避，伸手按住了晃动的篙竿，手指稳而有力',
         shot='固定镜头近切，船猛颠了一下，白袍谋士不闪不避，抬手稳稳按住了晃动的篙竿',
         lens='85mm 长焦，浅景深', cp='白袍谋士 + 平视正面', comp='三分法', eye='晃动的篙竿', focus='锁定按住篙竿的手', stab='stable',
         h3='A static shot close-up of <Picture 2>: the boat heaves and spray dashes the gunwale, yet the white-robed sagely strategist does not flinch, reaching to steady the swaying pole with a firm hand.'),
       dict(b=[4,4],sec=4,size='close',cam='Static Shot',ch=['C13'],pr=[],
         frame='特写，舱口的鲁肃上前两步与孔明并肩，略一迟疑，压低声探问一句',
         shot='固定镜头近切，舱口那名魁梧文官上前两步站到白袍谋士身边，压低声音探问',
         lens='85mm 长焦，中浅景深', cp='魁梧文官 + 平视正面', comp='三分法', eye='白袍谋士的侧脸', focus='锁定探问的神情', stab='stable',
         h3='A static shot close-up of <Picture 3>: the sturdy attendant steps up from the cabin hatch to stand beside the sagely strategist and, hesitating, with a low, cautious voice (S1) asks: <d>[Chinese] 先生入吴，心里可有成算？</d>'),
      ]))
    s.append(dict(sceneId='S09',
      blocking='白袍谋士转身侧对，魁梧文官贴他近旁；换气般的两张近景在两人间来回切。',
      soundscape='江水拍舷，衣角抚动，两人压低的声音裹在风里',
      music='低音弦乐托起，速度略有收拢',
      cuts=[
       dict(b=[5,6],sec=5,size='medium',cam='Static Shot',ch=['C05'],pr=[],
         frame='中景，孔明收回手回头看鲁肃，目光平静，口中淡然接上一句',
         shot='固定镜头中景，白袍谋士收回手回头看向同伴，目光平静，徐徐接上一句',
         lens='50mm 标准，中浅景深', cp='白袍谋士 + 平视侧面', comp='三分法', eye='魁梧文官的面容', focus='锁定白袍谋士平静的目光', stab='stable',
         h3='Holding <Picture 1>, the sagely strategist draws his hand back and turns to the companion beside him; static shot, and with a calm, quiet voice (S1) he answers: <d>[Chinese] 江东主降者多，可孙权不信命。</d>'),
       dict(b=[7,7],sec=3,size='close',cam='Static Shot',ch=['C13'],pr=[],
         frame='特写，鲁肃闻言眉头松了松，抬手替孔明整了整肩头那方白巾，动作里透着宽慰',
         shot='固定镜头近切，魁梧文官闻言眉心松了松，抬手替白袍谋士把肩头的白巾整了整',
         lens='85mm 长焦，浅景深', cp='魁梧文官 + 平视正面', comp='三分法', eye='白袍谋士肩头', focus='锁定整巾的手', stab='stable',
         h3='A static shot close-up of <Picture 2>: relieved at the words, the sturdy attendant relaxes his brow and reaches up to tidy the white cloth draping the counselor\u2019s shoulder.'),
       dict(b=[8,8],sec=4,size='close',cam='Static Shot',ch=['C13'],pr=[],
         frame='特写，鲁肃略一沉吟，又郑重地追问一句，眼底带着几分期待与不安',
         shot='固定镜头近切，魁梧文官略一沉吟，又郑重地开口追问，眼底带着几分探问',
         lens='85mm 长焦，中浅景深', cp='魁梧文官 + 平视正面', comp='三分法', eye='白袍谋士', focus='锁定追问的神情', stab='stable',
         h3='A static shot close-up of <Picture 3>: after a pause the sturdy attendant puts a graver question to him, and with a serious, somewhat anxious voice (S2) presses: <d>[Chinese] 先生可敢当着满朝，驳他们一问？</d>'),
      ]))
    s.append(dict(sceneId='S09',
      blocking='白袍谋士负手望江立在前，魁梧文官扶船沿立于侧后方，江水雾气在两人之间翻涌。',
      soundscape='江雾翻涌的闷响，木板船身的吱呀，一浪侧倾时水花溅起',
      music='低音弦乐压着一个未落的音，暗藏汹涌',
      cuts=[
       dict(b=[9,9],sec=3,size='medium',cam='Static Shot',ch=['C05'],pr=[],
         frame='中景，孔明负手望江，江面上雾气翻涌不休，侧脸映着昏黄的灯火',
         shot='固定镜头中景，白袍谋士负手望江，江雾翻涌不已，他的侧脸映着灯火的微光',
         lens='50mm 标准，中浅景深', cp='白袍谋士 + 平视侧面', comp='三分法', eye='翻涌的江雾', focus='锁定白袍谋士的侧影', stab='stable',
         h3='Holding <Picture 1>, the sagely strategist stands with his hands behind his back gazing at the river, the mist churning endlessly; static shot, his profile lit by the faint shore lights.'),
       dict(b=[10,10],sec=3,size='medium',cam='Static Shot',ch=['C13'],pr=[],
         frame='中景，一浪打来船身侧倾，鲁肃一把扶住船沿，面上却绷得紧紧的',
         shot='固定镜头，大浪涌来船身侧倾，魁梧文官一把扶住船沿稳住身形，神情绷紧',
         lens='50mm 标准，中浅景深', cp='魁梧文官 + 平视侧面', comp='三分法', eye='脚下的船沿', focus='锁定扶住船沿的手', stab='slight-shake',
         h3='Under <Picture 2>, a wave strikes and the boat lists; static shot, the sturdy attendant grips the gunwale to steady himself, his face white-knuckled with tension.'),
       dict(b=[11,11],sec=4,size='close',cam='Static Shot',ch=['C13'],pr=[],
         frame='特写，鲁肃望着那片雾，低低叹出心中的顾虑',
         shot='固定镜头近切，魁梧文官望着船头那片浓雾，低低叹出一句',
         lens='85mm 长焦，中浅景深', cp='魁梧文官 + 平视正面', comp='三分法', eye='船头的江雾', focus='锁定低叹的神情', stab='stable',
         h3='A static shot close-up of <Picture 3>: looking out at the fog ahead, the sturdy attendant lets out a low sigh, and with a worried, weighing voice (S2) muses: <d>[Chinese] 我看江东这满朝，没几个是好相与的。</d>'),
      ]))
    s.append(dict(sceneId='S09',
      blocking='白袍谋士转身面向同伴，两人一正一侧隔半步相对；魁梧文官抬手替他理衣角。',
      soundscape='衣料窸窣，江水声，雾气在灯影里流动',
      music='低音弦乐稳升，蓄着一句关键的答',
      cuts=[
       dict(b=[12,13],sec=6,size='medium',cam='Static Shot',ch=['C05'],pr=[],
         frame='中景，孔明转过身来，目光在雾里顿了片刻，才沉稳地开口点破那句要害',
         shot='固定镜头中景，白袍谋士转过身来，目光在雾里顿了顿，才沉稳地开口，一字一句都在要害',
         lens='50mm 标准，中浅景深', cp='白袍谋士 + 平视正面', comp='三分法', eye='魁梧文官的面容', focus='锁定白袍谋士开口的从容', stab='stable',
         h3='Holding <Picture 1>, the sagely strategist turns around, holding his gaze in the mist for a beat before speaking; static shot, and with a steady, pointed voice (S1) he says: <d>[Chinese] 他们越急，越说明这条船必须靠岸。</d>'),
       dict(b=[14,14],sec=4,size='close',cam='Static Shot',ch=['C13'],pr=[],
         frame='特写，鲁肃听了似懂非懂，只默默替孔明拉了拉被风吹乱的衣角',
         shot='固定镜头近切，魁梧文官听了似懂非懂，没再多问，默默替白袍谋士把吹乱的衣角拉平',
         lens='85mm 长焦，中浅景深', cp='魁梧文官 + 平视正面', comp='三分法', eye='白袍谋士的衣角', focus='锁定拉衣角的动作', stab='stable',
         h3='A static shot close-up of <Picture 2>: half understanding, the sturdy attendant does not press further, only quietly smoothing the counselor\u2019s wind-blown lapel.'),
      ]))
    s.append(dict(sceneId='S09',
      blocking='船头破雾，两人一前一后立定：白袍谋士在前，魁梧文官在后替他整理衣冠。',
      soundscape='船破开白雾的响，江岸灯火渐渐亮起，远处军士隐约的走动',
      music='弦乐略开阔，中慢速，靠岸前的收势',
      cuts=[
       dict(b=[15,15],sec=3,size='wide',cam='Static Shot',ch=['C05'],pr=[],
         frame='全景，船又破开一团白雾，江岸的灯火一茬一茬亮起来，近在眼前',
         shot='固定镜头，小船又破开一团白雾，江岸的灯火一茬茬亮起，近在眼前',
         lens='35mm 广角，深景深', cp='江岸远景 + 平视', comp='三分法', eye='渐亮的岸灯', focus='锁定雾与灯火', stab='stable',
         h3='The wide of <Picture 1> holds as the boat splits another bank of fog and the shore lamps come alight one after another, close ahead; static shot.'),
       dict(b=[16,16],sec=4,size='close',cam='Static Shot',ch=['C13'],pr=[],
         frame='特写，鲁肃望着那排火光，提醒孔明上岸前再想想措辞',
         shot='固定镜头近切，魁梧文官望着岸上那排火光，回头提醒白袍谋士',
         lens='85mm 长焦，中浅景深', cp='魁梧文官 + 平视正面', comp='三分法', eye='岸上那排火光', focus='锁定提醒的神情', stab='stable',
         h3='A static shot close-up of <Picture 2>: looking at the line of shore torches, the sturdy attendant turns to warn the strategist, and with a light, concerned voice (S2) says: <d>[Chinese] 到渡口了。上岸前，先生再想想措辞。</d>'),
       dict(b=[17,17],sec=3,size='close',cam='Static Shot',ch=['C05'],pr=[],
         frame='特写，孔明望着那排火光没有答话，只把袍角往腰里一掖，整了整衣冠',
         shot='固定镜头近切，白袍谋士望着火光没有答话，只把袍角掖进腰里，随手正了正衣冠',
         lens='85mm 长焦，浅景深', cp='白袍谋士 + 平视正面', comp='三分法', eye='岸上的火光', focus='锁定整衣冠的动作', stab='stable',
         h3='A static shot close-up of <Picture 3>: the sagely strategist says nothing to the shore lights, only tucks the hem of his robe into his sash and straightens his cap.'),
      ]))
    s.append(dict(sceneId='S09',
      blocking='船首靠岸，白袍谋士独立船头，岸上兵卒执火列队，吴字旗在船尾翻卷。',
      soundscape='船体靠岸的木响，火把噼啪，旗帜在风里猎猎，军士脚步声',
      music='低音弦乐轻扬，带一线将要登场的张力',
      cuts=[
       dict(b=[18,18],sec=3,size='wide',cam='Static Shot',ch=['C05'],pr=[],
         frame='全景，船身一靠，岸上兵卒的火把一晃，吴字旗在风口猎猎招展',
         shot='固定镜头，船身靠岸，岸上兵卒的火把一晃，一面旗在风口猎猎招展',
         lens='35mm 广角，深景深', cp='江岸 + 平视', comp='对角线构图', eye='岸上执火的兵卒', focus='锁定翻卷的吴字旗', stab='stable',
         h3='The wide of <Picture 1> holds as the boat nudges the bank, torchlight flickering among the soldiers and a banner snapping in the wind; static shot.'),
       dict(b=[19,19],sec=4,size='close',cam='Static Shot',ch=['C05'],pr=[],
         frame='特写，孔明踏着船板，不紧不慢地应了这一句，语气闲淡',
         shot='固定镜头近切，白袍谋士踏稳船板，不紧不慢地回了一句，语气云淡风轻',
         lens='85mm 长焦，浅景深', cp='白袍谋士 + 平视正面', comp='三分法', eye='岸上列队的兵卒', focus='锁定闲淡的神情', stab='stable',
         h3='A static shot close-up of <Picture 2>: settling his footing on the plank, the sagely strategist answers the unspoken weight of the moment lightly, and with an easy, offhand voice (S1) says: <d>[Chinese] 都是刀笔闲工夫，何必放在心上下不来。</d>'),
       dict(b=[20,20],sec=4,size='wide',cam='Static Shot',ch=['C05'],pr=[],
         frame='全景，船头撞开一团白雾，江东岸的旗杆与楼台轮廓渐次清晰，灯火连成一片',
         shot='固定镜头，船头撞开白雾，江岸的旗杆与楼台轮廓渐次清晰，灯火连成一片',
         lens='35mm 广角，深景深', cp='江岸全景 + 平视', comp='三分法', eye='江岸楼台轮廓', focus='锁定雾散灯稠的岸', stab='stable',
         h3='Holding the wide of <Picture 3>, the bow splits the fog and the masts and pavilions of the shore take shape, lamps linking into one sheet of light; static shot.'),
      ]))
    s.append(dict(sceneId='S09',
      blocking='两人一前一后踏上岸梯：魁梧文官在前引路，白袍谋士在后拂衣跟上，身后江水滔滔。',
      soundscape='登岸的脚步声，江水在身后涌，岸上军士短暂的低语',
      music='低音弦乐收束，为下一场厅堂对话起势',
      cuts=[
       dict(b=[21,21],sec=3,size='medium',cam='Static Shot',ch=['C13'],pr=[],
         frame='中景，鲁肃搀着孔明上岸，岸边早有江东士卒执火列队相候',
         shot='固定镜头，魁梧文官搀着白袍谋士登岸，岸上早有执火的士卒列队相候',
         lens='50mm 标准，中浅景深', cp='两人 + 平视侧面', comp='三分法', eye='列队相候的兵卒', focus='锁定两人上岸的身影', stab='stable',
         h3='Holding <Picture 1>, the sturdy attendant helps the sagely strategist ashore where units of torch-bearing soldiers wait in line; static shot.'),
       dict(b=[22,22],sec=4,size='close',cam='Static Shot',ch=['C13'],pr=[],
         frame='特写，鲁肃侧身相请，请孔明随他先见主公孙权',
         shot='固定镜头近切，魁梧文官侧身做了个请的手势，请白袍谋士随他先去见主公',
         lens='85mm 长焦，中浅景深', cp='魁梧文官 + 平视正面', comp='三分法', eye='前方的道路', focus='锁定相请的手势', stab='stable',
         h3='A static shot close-up of <Picture 2>: gesturing the way ahead, the sturdy attendant invites the strategist to follow, and with a deferential voice (S2) says: <d>[Chinese] 先生随我来，先见我家主公。</d>'),
       dict(b=[23,23],sec=4,size='wide',cam='Static Shot',ch=['C05'],pr=[],
         frame='全景，孔明拂了拂衣袍上的水珠，迈步跟上，身后江水滔滔',
         shot='固定镜头，白袍谋士抬手拂去衣袍上的水珠，迈步跟上，身后的江水滔滔',
         lens='35mm 广角，深景深', cp='白袍谋士 + 背面平视', comp='三分法', eye='前方的宫室', focus='锁定白袍谋士迈步的背影', stab='stable',
         h3='The wide of <Picture 3> closes the scene: the sagely strategist brushes the spray from his robe and steps forward to follow, the great river churning behind him; static shot.'),
      ]))
    # ---- scene2 厅堂 ----
    s.append(dict(sceneId='S08',
      blocking='日光斜斜打进的厅堂，主公居主位坐定，魁梧文官引白袍谋士上前；堂下随侍。',
      soundscape='厅堂里的静，日光落下的空气中微尘，衣料与木案轻响',
      music='疏朗的弦乐托底，中慢速，见客的张力',
      cuts=[
       dict(b=[1,2],sec=5,size='wide',cam='Static Shot',ch=['C14'],pr=[],
         frame='全景，厅堂之上日光斜斜打进来，孙权重袍坐定抬眼打量初渡江来的客人，鲁肃先行拜过引孔明上前',
         shot='固定镜头，宽厅里日光照进来，一名年轻主公重袍坐定抬眼打量进门的新客，一旁文官先行长揖引见',
         lens='35mm 广角，深景深', cp='主公 + 平视略仰', comp='三分法', eye='进门的客人', focus='锁定主公安坐打量之姿', stab='stable',
         h3='The cold open holds the full hall of <Picture 1>: slanting daylight fills the chamber, a seated young lord in heavy robes studies the newly arrived guest while a civil official performs the introduction; static shot.'),
       dict(b=[3,3],sec=5,size='medium',cam='Static Shot',ch=['C13'],pr=[],
         frame='中景，鲁肃长揖引见，向孙权禀明来客身份',
         shot='固定镜头，那名魁梧文官长揖见礼，向主公禀明来客的身份',
         lens='50mm 标准，中浅景深', cp='魁梧文官 + 平视正面', comp='三分法', eye='安坐的主公', focus='锁定长揖引见的身姿', stab='stable',
         h3='Holding <Picture 2>, the sturdy attendant bows and presents the guest to the lord, and with a formal, respectful voice (S1) reports: <d>[Chinese] 主公，这位便是刘备麾下军师诸葛孔明。</d>'),
       dict(b=[4,4],sec=4,size='close',cam='Static Shot',ch=['C14'],pr=[],
         frame='特写，孙权微微颔首，抬手请客落座，目光却在孔明脸上多停了片刻',
         shot='固定镜头近切，年轻主公微微颔首，抬手请客落座，目光却在新客脸上多停了一瞬',
         lens='85mm 长焦，中浅景深', cp='主公 + 平视正面', comp='三分法', eye='白袍谋士的面容', focus='锁定审视的目光', stab='stable',
         h3='A static shot close-up of <Picture 3>: the young lord gives a slight nod and gestures for the guest to sit, but his eyes linger on the newcomer\u2019s face a moment longer than politeness allows.'),
      ]))
    s.append(dict(sceneId='S08',
      blocking='主客对坐：主公居主位，白袍谋士居客位，隔案相对；两人一进一出地过招。',
      soundscape='茶盏与案几轻响，日光落在堂上，衣料摩擦的细声',
      music='低音弦乐一收一放，随交锋起伏',
      cuts=[
       dict(b=[5,6],sec=5,size='medium',cam='Static Shot',ch=['C14'],pr=[],
         frame='中景，孙权单刀直入问孔明此来是否讨救兵，孔明在客位不慌不忙拱了拱手',
         shot='固定镜头中景，年轻主公直问一句，客位上的白袍谋士不慌不忙拱手作答',
         lens='50mm 标准，中浅景深', cp='双人 + 平视侧面', comp='三分法', eye='客位的白袍谋士', focus='锁定主公直问的神情', stab='stable',
         h3='Holding <Picture 1>, the young lord opens without ceremony, and with a probing voice (S1) he asks: <d>[Chinese] 先生此来，是替你那位皇叔讨救兵？</d>'),
       dict(b=[7,7],sec=6,size='medium',cam='Static Shot',ch=['C05'],pr=[],
         frame='中景，孔明不慌不忙拱了拱手，字字沉稳地撇清来意',
         shot='固定镜头中景，白袍谋士拱了拱手，不慌不忙，一字一句沉稳作答',
         lens='50mm 标准，中浅景深', cp='白袍谋士 + 平视正面', comp='三分法', eye='安坐的主公', focus='锁定沉稳作答的神情', stab='stable',
         h3='Holding <Picture 2>, the sagely strategist folds his hands in a bow and answers without hurry, and with a steady, measured voice (S2) declares: <d>[Chinese] 既非讨兵，也非求援，是来与江东共谋生路。</d>'),
       dict(b=[8,8],sec=3,size='medium',cam='Static Shot',ch=['C14'],pr=[],
         frame='中景，孙权眉头一动，示意他接着说下去',
         shot='固定镜头中景，年轻主公眉头微动，抬手示意客位的谋士往下说',
         lens='50mm 标准，中浅景深', cp='主公 + 平视正面', comp='三分法', eye='客位的白袍谋士', focus='锁定示意的手势', stab='stable',
         h3='A static shot of <Picture 3> holds on the young lord, who raises a single brow and gestures for the guest to go on.'),
      ]))
    s.append(dict(sceneId='S08',
      blocking='对坐交锋继续：主公一句句进逼，白袍谋士一盏茶一把尺稳稳接住。',
      soundscape='茶盏搁下的轻响，几句问答间的短暂静默，窗外风声',
      music='弦乐节奏清晰，一问一答错落有致',
      cuts=[
       dict(b=[9,10],sec=5,size='close',cam='Static Shot',ch=['C14'],pr=[],
         frame='特写，孙权嘲弄般点破孔明故意说轻曹家兵势，孔明不接话，端茶盏饮了一口缓缓放下',
         shot='固定镜头近切，年轻主公语带激将点了一句；白袍谋士不接话，端起茶盏饮了一口才轻轻放下',
         lens='85mm 长焦，中浅景深', cp='主公 + 平视正面', comp='三分法', eye='白袍谋士', focus='锁定激将的神情', stab='stable',
         h3='The close shot of <Picture 1> holds on the young lord, and with a challenging, mocking voice (S1) he needles: <d>[Chinese] 曹贼兵盛，先生却说的像一场买卖。</d>'),
       dict(b=[11,11],sec=6,size='medium',cam='Static Shot',ch=['C05'],pr=[],
         frame='中景，孔明放下茶盏，徐徐亮出那层利害',
         shot='固定镜头中景，白袍谋士缓缓放下茶盏，不紧不慢地亮出那层利害',
         lens='50mm 标准，中浅景深', cp='白袍谋士 + 平视正面', comp='三分法', eye='安坐的主公', focus='锁定说话的从容', stab='stable',
         h3='Holding <Picture 2>, the sagely strategist sets down the cup and lays out the stakes unhurriedly, and with a clear, weighty voice (S2) explains: <d>[Chinese] 曹操持百万之众南下，江东挡，则两家俱存。</d>'),
       dict(b=[12,12],sec=4,size='medium',cam='Static Shot',ch=['C14'],pr=[],
         frame='中景，孙权不答，只把眉头锁深了些，像是被这句话砸到了心上',
         shot='固定镜头中景，年轻主公有话不说，只把眉头锁得更深，像是被这句话砸中了心事',
         lens='50mm 标准，中浅景深', cp='主公 + 平视正面', comp='三分法', eye='案前的茶盏', focus='锁定紧锁的眉头', stab='stable',
         h3='A static shot of <Picture 3> holds on the young lord, who says nothing, only furrows his brow deeper, struck by the force of the words.'),
      ]))
    s.append(dict(sceneId='S08',
      blocking='堂上一时静极，白袍谋士端坐待答，主公握卷锁眉良久才开口。',
      soundscape='满堂寂静，窗外风漏进一点，卷帛被攥紧的细响',
      music='弦乐压到极静，蓄着下一句的分量',
      cuts=[
       dict(b=[13,13],sec=3,size='wide',cam='Static Shot',ch=['C05'],pr=[],
         frame='全景，堂上一时静得出奇，只有窗外的风声偶尔漏进来，白袍谋士端坐等待',
         shot='固定镜头，厅堂里静得出奇，只有窗外风声偶尔漏进来，白袍谋士端坐等着主公接话',
         lens='35mm 广角，深景深', cp='堂景 + 平视', comp='三分法', eye='安坐的主公', focus='锁定满堂的静', stab='stable',
         h3='The wide of <Picture 1> holds on the suddenly hushed chamber, only a stray gust slipping in past the window while the sagely strategist waits in his seat; static shot.'),
       dict(b=[14,14],sec=6,size='close',cam='Static Shot',ch=['C05'],pr=[],
         frame='特写，孔明一字一顿地落下那句重话，把利害摆到桌面上',
         shot='固定镜头近切，白袍谋士抬眼看着主公，一字一顿把那句利害落定',
         lens='85mm 长焦，浅景深', cp='白袍谋士 + 平视正面', comp='三分法', eye='安坐的主公', focus='锁定落话时的眼神', stab='stable',
         h3='A static shot close-up of <Picture 2>: fixing the young lord with his gaze, the sagely strategist sets down the weight of the choice, and with a grave, final voice (S2) warns: <d>[Chinese] 主公若不肯并力，曹兵一渡江，江东便是第二个荆州。</d>'),
       dict(b=[15,15],sec=5,size='close',cam='Static Shot',ch=['C14'],pr=[],
         frame='特写，孙权握着案卷的指节泛了泛白，一时没有答话',
         shot='固定镜头近切，年轻主公握着案卷的指节微微泛白，半晌没能接上话',
         lens='85mm 长焦，中浅景深', cp='主公 + 平视正面', comp='三分法', eye='案上的卷帛', focus='锁定泛白的指节', stab='stable',
         h3='A static shot close-up of <Picture 3>: the young lord\u2019s knuckles whiten around the scroll in his hand, and for a long moment he finds no reply.'),
      ]))
    s.append(dict(sceneId='S08',
      blocking='主公一句句试探深浅，白袍谋士以手势与一句轻答稳稳化解。',
      soundscape='几声问答，茶盏轻响，主公追问的语气渐急',
      music='弦乐轻快一线，又压回沉静',
      cuts=[
       dict(b=[16,16],sec=4,size='close',cam='Static Shot',ch=['C14'],pr=[],
         frame='特写，孙权不放松地追一句，问曹兵到底多不多',
         shot='固定镜头近切，年轻主公凝神追问一句，问曹家的兵到底多不多',
         lens='85mm 长焦，中浅景深', cp='主公 + 平视正面', comp='三分法', eye='白袍谋士', focus='锁定追问的神情', stab='stable',
         h3='A static shot close-up of <Picture 1>: not letting the point go, the young lord presses on, and with a skeptical voice (S1) he asks: <d>[Chinese] 你说的轻巧，可知曹兵到底多不多？</d>'),
       dict(b=[17,17],sec=4,size='medium',cam='Static Shot',ch=['C05'],pr=[],
         frame='中景，孔明朗声一笑，抬手一比，比了个极宽的手势',
         shot='固定镜头中景，白袍谋士朗声一笑，抬手一比，比出一个极宽的手势',
         lens='50mm 标准，中浅景深', cp='白袍谋士 + 平视正面', comp='三分法', eye='比出的手势', focus='锁定朗笑与手势', stab='stable',
         h3='Holding <Picture 2>, the sagely strategist lets out an easy laugh and holds up a hand, describing a very wide span; static shot.'),
       dict(b=[18,18],sec=5,size='close',cam='Static Shot',ch=['C05'],pr=[],
         frame='特写，孔明收了笑，沉稳地接上那句，点出人多未必有用',
         shot='固定镜头近切，白袍谋士敛起笑意，沉稳地接上那句点破',
         lens='85mm 长焦，浅景深', cp='白袍谋士 + 平视正面', comp='三分法', eye='安坐的主公', focus='锁定敛笑后的淡定', stab='stable',
         h3='A static shot close-up of <Picture 3>: the sagely strategist tucks the smile away and answers steadily, and with a composed voice (S2) says: <d>[Chinese] 多，可多又有何用？抵得过归心之兵。</d>'),
      ]))
    s.append(dict(sceneId='S08',
      blocking='主公望着案上灯火出神，白袍谋士不催，魁梧文官在旁禀一句船备已下。',
      soundscape='风声，茶盏细响，主公指尖敲案沿的轻响',
      music='弦乐空落，等一个决定',
      cuts=[
       dict(b=[19,19],sec=3,size='close',cam='Static Shot',ch=['C14'],pr=[],
         frame='特写，孙权盯着孔明抬起的手指，半晌，忽然点了点头',
         shot='固定镜头近切，年轻主公盯着客座那位举着的手指，沉默片刻，忽然点了一下头',
         lens='85mm 长焦，中浅景深', cp='主公 + 平视正面', comp='三分法', eye='客座的手势', focus='锁定点头的一瞬', stab='stable',
         h3='A static shot close-up of <Picture 1>: the young lord stares at the raised hand of the visitor, and after a long moment gives a small nod.'),
       dict(b=[20,21],sec=5,size='medium',cam='Static Shot',ch=['C14','C05'],pr=[],
         frame='中景，孙权目光落在窗缝透进的江上灯火上指尖轻扣案沿，孔明不催，自顾自又饮了口茶',
         shot='固定镜头中景，年轻主公望着窗缝透进来的灯火，指尖轻扣案沿；白袍谋士不催，自顾又饮了口茶',
         lens='50mm 标准，中浅景深', cp='双人 + 平视侧面', comp='三分法', eye='窗缝的灯火', focus='锁定主公出神的神情', stab='stable',
         h3='The medium of <Picture 2> holds on the two of them: the young lord gazes at the river lights through the window slats, fingers tapping the table edge, while the sagely strategist makes no move to rush him and quietly takes another sip of tea; static shot.'),
       dict(b=[22,22],sec=4,size='close',cam='Static Shot',ch=['C13'],pr=[],
         frame='特写，鲁肃低声朝主公禀一句，船已备好就等发话',
         shot='固定镜头近切，那名魁梧文官放低声音，向主公禀上一句',
         lens='85mm 长焦，中浅景深', cp='魁梧文官 + 平视正面', comp='三分法', eye='安坐的主公', focus='锁定低声禀报的神情', stab='stable',
         h3='A static shot close-up of <Picture 3>: the sturdy attendant lowers his voice to the lord, and with a discreet tone (S3) states: <d>[Chinese] 主公，船已备下，就等您一句话。</d>'),
      ]))
    s.append(dict(sceneId='S08',
      blocking='主公指按军报又停在信上，拿起又放回；白袍谋士迎着他的目光静静等待。',
      soundscape='指节按纸的轻响，信纸拿起又放回的窸窣，厅堂静默',
      music='弦乐压着一个悬音，静等主公表态',
      cuts=[
       dict(b=[23,24],sec=5,size='medium',cam='Static Shot',ch=['C14'],pr=[],
         frame='中景，孙权伸手按向案头的军报，指尖却在一封信上顿住，缓缓拿起又放回',
         shot='固定镜头中景，年轻主公伸手按向案头军报，指尖却在叠纸上顿住，把那封信拿起又缓缓放回',
         lens='50mm 标准，中浅景深', cp='主公 + 平视正面', comp='三分法', eye='案上那封信', focus='锁定顿住的指尖', stab='stable',
         h3='Holding <Picture 1>, the young lord presses a hand toward the reports on the table, his fingertip catching on one sealed letter, picking it up and setting it down again; static shot.'),
       dict(b=[25,25],sec=3,size='close',cam='Static Shot',ch=['C05'],pr=[],
         frame='特写，孔明迎着他的目光，既不闪避也不催促，只静静等着',
         shot='固定镜头近切，白袍谋士迎着主公的目光，不闪不避也不催，只静静端坐',
         lens='85mm 长焦，浅景深', cp='白袍谋士 + 平视正面', comp='三分法', eye='主公的目光', focus='锁定安然的静候', stab='stable',
         h3='A static shot close-up of <Picture 2>: the sagely strategist meets the lord\u2019s gaze, neither looking away nor pushing, simply waiting in patience.'),
       dict(b=[26,26],sec=5,size='close',cam='Static Shot',ch=['C05'],pr=[],
         frame='特写，孔明缓缓点破那句，把真正的尺度落回主公心上',
         shot='固定镜头近切，白袍谋士缓缓开口点破，一句落定便不再多言',
         lens='85mm 长焦，浅景深', cp='白袍谋士 + 平视正面', comp='三分法', eye='主公', focus='锁定点破时的沉静', stab='stable',
         h3='A static shot close-up of <Picture 3>: softly, the sagely strategist sets the deciding measure back upon the lord himself, and with a low, pointed voice (S2) concludes: <d>[Chinese] 主公心中那把尺，原不在曹贼，在江东。</d>'),
      ]))
    s.append(dict(sceneId='S08',
      blocking='主公被动摇防线、终于松口松线，白袍谋士长揖告辞退出厅堂。',
      soundscape='指尖颤过纸面，主公开口说话，随后长揖起的衣料声',
      music='弦乐松动，一线天光落进的决定',
      cuts=[
       dict(b=[27,28],sec=5,size='close',cam='Static Shot',ch=['C14'],pr=[],
         frame='特写，孙权像是被说中心事，指尖微微一颤把信压回案下，再抬眼看孔明时，眼底那道防备的线松动了一线',
         shot='固定镜头近切，年轻主公像被说中心事，指尖微颤把信压回案下，再抬眼时，眼底的防备松了一线',
         lens='85mm 长焦，中浅景深', cp='主公 + 平视正面', comp='三分法', eye='白袍谋士', focus='锁定松动一线的眼神', stab='stable',
         h3='A static shot close-up of <Picture 1>: as if the truth of it struck home, the young lord\u2019s finger quivers, pressing the letter back beneath the table, and when he lifts his eyes to the strategist again the guarded line in them loosens a hair.'),
       dict(b=[29,29],sec=5,size='medium',cam='Static Shot',ch=['C14'],pr=[],
         frame='中景，孙权终于松口，请孔明容他一夜，明日满朝再议',
         shot='固定镜头中景，年轻主公终于开口，请白袍谋士容他一夜，明日满朝同议',
         lens='50mm 标准，中浅景深', cp='主公 + 平视正面', comp='三分法', eye='白袍谋士', focus='锁定松口的郑重', stab='stable',
         h3='Holding <Picture 2>, the young lord grants time and gives his word, and with a solemn, decision-softened voice (S2) says: <d>[Chinese] 容我一夜。明日，满朝同公卿再议。</d>'),
       dict(b=[30,31],sec=4,size='wide',cam='Static Shot',ch=['C05'],pr=[],
         frame='全景，孔明起身一揖随鲁肃退出门去，门扇掩阖的声音在堂内轻轻回荡',
         shot='固定镜头全景，白袍谋士起身深深一揖，随文官退出堂门，门扇掩阖，声音在堂内轻轻回荡',
         lens='35mm 广角，深景深', cp='堂门全景 + 平视', comp='中心构图', eye='退出的方向', focus='锁定掩阖的门扇', stab='stable',
         h3='The wide of <Picture 3> closes the scene: with a deep bow the sagely strategist follows the attendant out of the chamber, and the door falls shut, its sound echoing once through the hall; static shot.'),
      ]))
    return s

# (en_sound, en_music) 按 EP43 段序排列（15 段：scene1 7 + scene2 8）
ENSOUND_43 = [
 ("River wind tearing at a robe, water washing the hull, faint voices behind the dim shore lamps.","Low strings lying on the mist, slow to middle tempo, wide and open."),
 ("Water slapping the gunwale, cloth stirring, the two lowered voices caught in the wind.","Low strings lifting, the pace drawing in a little."),
 ("The muffled churn of fog, the creak of wooden planks, spray hissing as a wave lists the boat.","Low strings holding an unresolved note, something stirring below the surface."),
 ("Rustle of cloth, river water, mist drifting through the lamplight.","Low strings rising steadily, saving for a pivotal answer."),
 ("The swish of the bow parting fog, shore lamps growing bright, faint movement of distant soldiers.","Strings opening out, slow to middle tempo, easing toward landfall."),
 ("The thud of the hull against the bank, torches crackling, a banner snapping, soldiers\u2019 boots.","Light low strings with a thread of tension before the audience begins."),
 ("Steps on the landing, the river surging behind, a brief murmur among the waiting soldiers.","Low strings drawing in, setting up the chamber to come."),
 ("A stillness in the hall, motes turning in the sunlight, the rustle of cloth and wood.","Sparce strings beneath, slow to middle tempo, the sharp air of a first meeting."),
 ("Faint clink of cup and table, sunlight across the hall, the light silk of clothing.","Low strings contracting and releasing with the exchange."),
 ("A cup set down with a click, brief silences between the exchanges, wind past the windows.","Strings with a crisp rhythm, question and answer falling into step."),
 ("The whole chamber fallen silent, a stray gust slipping past the window, a scroll clenched.","Strings pressing to near stillness, holding the weight of the next line."),
 ("A few exchanges, cup and table-click, the lord\u2019s tone pressing sharper.","Strings turning light for a beat, then settling back into quiet."),
 ("Wind, the fine click of a cup, the lord tapping the table edge with a fingertip.","Strings hollow and waiting on a decision."),
 ("The press of a fingertip over paper, a letter lifted and set back, the silence of the hall.","Strings holding a single suspended note, waiting on the lord\u2019s word."),
 ("A fingertip trembling across paper, the lord\u2019s voice at last, the silk of rising and bowing.","Strings easing open, a crack of daylight let into the resolve."),
]
if '--write43' in sys.argv:
    out43 = assemble(43, E43_cuts(), ENSOUND_43)
    test43 = {"source": orig["source"], "promptLang": "en", "params": orig["params"],
              "episodes": [{"ep": 43, "segments": out43}]}
    with open('_test43.json', 'w', encoding='utf-8') as f:
        json.dump(test43, f, ensure_ascii=False, indent=2)
    print("wrote _test43.json")
    print("EP43 segments:", len(out43), "total(s):", round(sum(segSeconds(s) for s in out43),1), "scene:", [s['sceneIndex'] for s in out43])

# =====================================================================
# EP 44  (scene1 舌战群儒 S09: C05 孔明)  (scene2 孙权定策 S09: C14 孙权, C05 孔明)
# =====================================================================
def E44_cuts():
    s=[]
    # ---- scene1 ----
    s.append(dict(sceneId='S09',
      blocking='堂上众儒分坐两排，交头接耳；一名傲气文官率先出声，白袍谋士立在堂中不疾不徐。',
      soundscape='堂上此起彼伏的低议声，衣料摩擦，一人抢先开口时满堂微静',
      music='低音弦乐压着一个未落的音，中慢速，暗藏机锋',
      cuts=[
       dict(b=[1,2],sec=5,size='wide',cam='Static Shot',ch=['C05'],pr=[],
         frame='全景，冷开场：堂上众儒坐成两排稀稀落落有人交头接耳，孔明立在孙权和群臣之间衣袍一拂不卑不亢，一名文臣抢先摆袖出声',
         shot='固定镜头，宽阔厅堂里两排文士低议纷纷，一名白袍谋士立于堂中不卑不亢，一侧有位文臣抢先摆袖开口',
         lens='35mm 广角，深景深', cp='堂景全景 + 平视略仰', comp='对称构图', eye='抢先出声的文臣', focus='锁定白袍谋士立于堂中之姿', stab='stable',
         h3='The cold open holds the hall of <Picture 1>: assembled officials murmur in two rows while the white-robed sagely strategist stands between the young prince and his ministers, robes flicked, neither humble nor overbearing; static shot.'),
       dict(b=[3,4],sec=6,size='close',cam='Static Shot',ch=['C05'],pr=[],
         frame='特写，孔明转头看向那位出声的文臣，两手负在身后，缓缓开口，一句点中要害',
         shot='固定镜头近切，白袍谋士转头看向那人，双手负在身后，不紧不慢开口，一句便点中要害',
         lens='85mm 长焦，浅景深', cp='白袍谋士 + 平视正面', comp='三分法', eye='那位出声的文臣', focus='锁定开口时的从容', stab='stable',
         h3='A static shot close-up of <Picture 2>: the sagely strategist turns to the speaking official, hands folded behind his back, and with a slow, unshakeable voice (S1) replies: <d>[Chinese] 劝降者，是替曹贼数兵，还是替江东数后路？</d>'),
      ]))
    s.append(dict(sceneId='S09',
      blocking='那文臣被噎住，又一名文官起身相问；白袍谋士抬手作答，堂下有零落附和。',
      soundscape='几处低应，衣料与咳嗽声，一人被堵住时短暂的哑场',
      music='弦乐一收一放，节奏偏快',
      cuts=[
       dict(b=[5,5],sec=3,size='wide',cam='Static Shot',ch=['C05'],pr=[],
         frame='全景，那文臣一噎，张了张嘴没能接上话，满堂目光落到他身上又移开',
         shot='固定镜头，那名文臣被一句话噎住，张了张嘴没能接上，众目睽睽下尴尬立住',
         lens='35mm 广角，深景深', cp='堂景 + 平视', comp='三分法', eye='哑然的文臣', focus='锁定被噎住的尴尬', stab='stable',
         h3='The wide of <Picture 1> holds as that official chokes on a reply, mouth open, silenced before the whole court; static shot.'),
       dict(b=[6,7],sec=5,size='medium',cam='Static Shot',ch=['C05'],pr=[],
         frame='中景，又一人自中席起身拱手，问刘皇叔兵微将寡怎么敢跟曹操硬碰，孔明听得完抬手指引答得极稳',
         shot='固定镜头中景，又一名文官起身拱手发问；白袍谋士听完，抬手指引，回答得极稳',
         lens='50mm 标准，中浅景深', cp='白袍谋士 + 平视侧面', comp='三分法', eye='起身发问的文官', focus='锁定稳答的神态', stab='stable',
         h3='Holding <Picture 2>, another official rises from mid-hall to question the guest about a thin, ill-armed force daring to clash with a mighty army; static shot, the sagely strategist listens and gestures in reply, unfaltering.'),
       dict(b=[8,8],sec=5,size='close',cam='Static Shot',ch=['C05'],pr=[],
         frame='特写，孔明一字结一句，把兵贵精而不贵多讲得干脆利落',
         shot='固定镜头近切，白袍谋士一字一句，把兵贵精不贵多的道理讲得干脆',
         lens='85mm 长焦，浅景深', cp='白袍谋士 + 平视正面', comp='三分法', eye='安坐上方的主公', focus='锁定点题的干脆', stab='stable',
         h3='A static shot close-up of <Picture 3>: sharp and clean, the sagely strategist cuts in, and with a crisp, decisive voice (S2) says: <d>[Chinese] 兵贵精不贵多，谋贵决不贵怯。</d>'),
      ]))
    s.append(dict(sceneId='S09',
      blocking='堂下几声附和，为首文官却冷笑抛来刁难；白袍谋士以一句人心收住全堂。',
      soundscape='几声零落附和，冷笑一声，随后短暂的静',
      music='弦乐转沉，一句一句压下来',
      cuts=[
       dict(b=[9,10],sec=5,size='wide',cam='Static Shot',ch=['C05'],pr=[],
         frame='全景，堂下响起几声附和，几个年轻文官抬了抬眼皮，为首的文官却不轻信，冷笑一声又抛出一句刁难话',
         shot='固定镜头，堂下几声附和与几个年轻文官抬了抬眼皮；为首的文官冷笑着又抛出一句刁难',
         lens='35mm 广角，深景深', cp='堂景 + 平视', comp='三分法', eye='冷笑的文官', focus='锁定笑里藏锋的目光', stab='stable',
         h3='The wide of <Picture 1> holds as a few murmurs of support pass and the leading official sneers, lobbing another barbed question; static shot.'),
       dict(b=[11,11],sec=5,size='close',cam='Static Shot',ch=['C05'],pr=[],
         frame='特写，孔明不避锋芒，点破那方凭仗其实在人心',
         shot='固定镜头近切，白袍谋士不避锋芒，缓缓点出真正的凭仗在人而不在城',
         lens='85mm 长焦，浅景深', cp='白袍谋士 + 平视正面', comp='三分法', eye='冷笑的文官', focus='锁定落话的沉静', stab='stable',
         h3='A static shot close-up of <Picture 2>: meeting the sneer head-on, the sagely strategist points out that the true reliance lies not in walls, and with a calm, certain voice (S2) says: <d>[Chinese] 皇叔所凭，不在城池，在人心未散。</d>'),
       dict(b=[12,12],sec=3,size='wide',cam='Static Shot',ch=['C05'],pr=[],
         frame='全景，那文官被他一句话堵住，脸色变了变，却寻不出破绽',
         shot='固定镜头，那文官被一句话堵住，脸色变了变，却怎么也寻不出破绽',
         lens='35mm 广角，深景深', cp='堂景 + 平视', comp='三分法', eye='脸色发僵的文官', focus='锁定无话可驳的窘态', stab='stable',
         h3='The wide of <Picture 3> holds as that official is caught short, his face turning, unable to find a crack in the argument; static shot.'),
      ]))
    s.append(dict(sceneId='S09',
      blocking='一名老儒撅着胡子冷笑，白袍谋士不恼反笑回身，一句反诘把老儒噎回座中。',
      soundscape='老儒冷笑的鼻音，随即被一句话堵住的闷响',
      music='弦乐一个上扬的转音，随即落定',
      cuts=[
       dict(b=[13,14],sec=5,size='medium',cam='Static Shot',ch=['C05'],pr=[],
         frame='中景，老儒撅着胡子冷笑，说江东子弟自保尚难谈何与刘备联手，孔明眉毛一挑不恼反笑回过身来',
         shot='固定镜头中景，一名老儒撅着胡子冷笑发难；白袍谋士眉毛一挑，不恼反笑，回过身来',
         lens='50mm 标准，中浅景深', cp='白袍谋士 + 平视侧面', comp='三分法', eye='撅须冷笑的老儒', focus='锁定不恼反笑的神色', stab='stable',
         h3='Holding <Picture 1>, an elder scholar sneers through his beard that the folk of the east can barely defend themselves; static shot, the sagely strategist raises a brow, smiling rather than vexed, and turns to face him.'),
       dict(b=[15,15],sec=5,size='close',cam='Static Shot',ch=['C05'],pr=[],
         frame='特写，孔明一句反诘落地，把敢不敢举刀、能不能自保摆在桌面上',
         shot='固定镜头近切，白袍谋士一句反诘稳稳落地，把话锋逼到对方桌前',
         lens='85mm 长焦，浅景深', cp='白袍谋士 + 平视正面', comp='三分法', eye='老儒', focus='锁定反诘时的锋锐', stab='stable',
         h3='A static shot close-up of <Picture 2>: the sagely strategist lands his rebuttal squarely on the table, and with a pointed voice (S2) asks: <d>[Chinese] 若连自家的刀都不敢举，谈何自保。</d>'),
       dict(b=[16,16],sec=3,size='wide',cam='Static Shot',ch=['C05'],pr=[],
         frame='全景，那老儒被噎得老脸一红，闷头坐了回去',
         shot='固定镜头，老儒被噎得老脸一红，闷了闷头坐回座中',
         lens='35mm 广角，深景深', cp='堂景 + 平视', comp='三分法', eye='坐回的老儒', focus='锁定老脸发红的窘态', stab='stable',
         h3='The wide of <Picture 3> holds as the elder scholar, red in the face, sinks back into his seat; static shot.'),
      ]))
    s.append(dict(sceneId='S09',
      blocking='座中又有人起身发难，白袍谋士不先接话，以一句反问把那人堵住。',
      soundscape='再一声起立的窸窣，一句争辩，随即语塞的安静',
      music='弦乐轻快一线，配着口中的机锋',
      cuts=[
       dict(b=[17,18],sec=5,size='medium',cam='Static Shot',ch=['C05'],pr=[],
         frame='中景，座中又有一人起身拱手发难，说孔明徒逞口舌无益江东存亡，孔明转看向那人，不慌不忙抬了抬手先不接话',
         shot='固定镜头中景，又一名文官起身拱手，指白袍谋士徒逞口舌；白袍谋士转头看向他，抬手一拦，先不接话',
         lens='50mm 标准，中浅景深', cp='白袍谋士 + 平视侧面', comp='三分法', eye='起身发难的文官', focus='锁定抬手的从容', stab='stable',
         h3='Holding <Picture 1>, another rises to accuse the guest of mere talk that serves nothing; static shot, the sagely strategist turns to him and raises a hand, declining to rise to the bait at once.'),
       dict(b=[19,19],sec=5,size='close',cam='Static Shot',ch=['C05'],pr=[],
         frame='特写，孔明顺着那句反驳轻轻一转，反问一句便把人将住',
         shot='固定镜头近切，白袍谋士顺着话锋轻轻一转，一句反问轻轻落定',
         lens='85mm 长焦，浅景深', cp='白袍谋士 + 平视正面', comp='三分法', eye='发难的文官', focus='锁定轻轻一转的巧', stab='stable',
         h3='A static shot close-up of <Picture 2>: turning the point on its head, the sagely strategist parries lightly, and with a wry voice (S2) asks: <d>[Chinese] 口舌若真无用，诸位今日又何必这般相争。</d>'),
       dict(b=[20,20],sec=4,size='wide',cam='Static Shot',ch=['C05'],pr=[],
         frame='全景，那人一时语塞，张着嘴半晌没能合上',
         shot='固定镜头，那人一时语塞，张着嘴半晌没能合上',
         lens='35mm 广角，深景深', cp='堂景 + 平视', comp='三分法', eye='语塞的文官', focus='锁定僵在当场的神情', stab='stable',
         h3='The wide of <Picture 3> holds as that man is left speechless, mouth hanging open for a long moment; static shot.'),
      ]))
    s.append(dict(sceneId='S09',
      blocking='一名老臣挺身搬出祖业求自保，白袍谋士敛了笑意把话锋轻轻一折，全堂随之寂静。',
      soundscape='老臣低沉的一句话，堂上随即静下来，只有衣料声',
      music='弦乐一沉，随即压到极静',
      cuts=[
       dict(b=[21,22],sec=5,size='medium',cam='Static Shot',ch=['C05'],pr=[],
         frame='中景，另一派的老臣也挺身而出搬出江东祖业，只说求自保、不与外人共谋，孔明敛了笑意把话锋轻轻一折',
         shot='固定镜头中景，一名老臣挺身上前搬出祖业，只求自保不与其谋；白袍谋士敛起笑意，把话锋轻轻一折',
         lens='50mm 标准，中浅景深', cp='白袍谋士 + 平视侧面', comp='三分法', eye='搬出祖业的老臣', focus='锁定敛笑折转的神情', stab='stable',
         h3='Holding <Picture 1>, an elder statesman steps forward invoking their ancestral land and asking only for self-preservation; static shot, the sagely strategist reels the point back gently.'),
       dict(b=[23,23],sec=5,size='close',cam='Static Shot',ch=['C05'],pr=[],
         frame='特写，孔明一句把内外之分拆开，郑重落在全江东上',
         shot='固定镜头近切，白袍谋士一句拆开内外之分，把分量落在整个江东之上',
         lens='85mm 长焦，浅景深', cp='白袍谋士 + 平视正面', comp='三分法', eye='老臣', focus='锁定郑重的分量', stab='stable',
         h3='A static shot close-up of <Picture 2>: drawing aside the line between self and other, the sagely strategist lays the weight upon the whole east, and with a grave, steady voice (S2) explains: <d>[Chinese] 曹兵压境，是全江东的事，何来内外之分。</d>'),
       dict(b=[24,24],sec=4,size='wide',cam='Static Shot',ch=['C05'],pr=[],
         frame='全景，这话一出堂上又是一片寂静，几个文臣低头交头接耳',
         shot='固定镜头，这话一出堂上又是一片安静，几名文臣低头交头接耳',
         lens='35mm 广角，深景深', cp='堂景 + 平视', comp='三分法', eye='低头私语的一群', focus='锁定满堂骤静的刹那', stab='stable',
         h3='The wide of <Picture 3> holds as the chamber falls silent at the words, a few officials bending to whisper; static shot.'),
      ]))
    s.append(dict(sceneId='S09',
      blocking='白袍谋士点到即止踱回庭中，一名武将击节叫好，几名主降文臣又围拢上来。',
      soundscape='击节的一声脆响，叫好声起，随后文臣围拢的低议',
      music='弦乐一线清明，转折到新一轮纠缠',
      cuts=[
       dict(b=[25,26],sec=5,size='wide',cam='Static Shot',ch=['C05'],pr=[],
         frame='全景，孔明点到即止不再追逼，缓步踱回庭中站定，一名武将模样的年轻官员忍不住击节替孔明叫了一声好',
         shot='固定镜头，白袍谋士点到即止，缓步踱回庭中站定；一名年轻武官忍不住击节，替他说了声好',
         lens='35mm 广角，深景深', cp='堂景 + 平视', comp='三分法', eye='击节叫好的武官', focus='锁定堂中踱回的身影', stab='stable',
         h3='The wide of <Picture 1> holds as the sagely strategist pulls back no further, pacing to the middle of the hall to stand; a young military officer claps once in salute; static shot.'),
       dict(b=[27,27],sec=4,size='medium',cam='Static Shot',ch=['C05'],pr=[],
         frame='中景，堂上静了片刻，几个主降的文臣又换着法子围上来',
         shot='固定镜头中景，堂上静了片刻，几名主张归降的文臣又各自换着说辞围拢过来',
         lens='50mm 标准，中浅景深', cp='白袍谋士 + 平视正面', comp='三分法', eye='围拢上来的文臣', focus='锁定被围而气定神闲', stab='stable',
         h3='Holding <Picture 2>, after a quiet beat the ministers who favor surrender close in again with fresh angles; static shot, the sagely strategist stands unruffled.'),
      ]))
    s.append(dict(sceneId='S09',
      blocking='白袍谋士被诸儒诘问围攻，一一接下逐条驳回；降派抬旧例，他以一句成败未知收住。',
      soundscape='一句接一句的争辩，被反驳时的一两声语塞，衣料与木案轻响',
      music='弦乐一句一个重音，越驳越利',
      cuts=[
       dict(b=[28,29],sec=5,size='medium',cam='Static Shot',ch=['C05'],pr=[],
         frame='中景，孔明一一接下不疾不徐逐条驳了回去，说到紧要处伸手在那案沿轻轻一点，为首的降派仍不甘心又抬出旧例',
         shot='固定镜头中景，白袍谋士一一接下逐条驳回，说到紧要处伸手在案沿一点；为首的降派不甘心，又抬出旧日战例',
         lens='50mm 标准，中浅景深', cp='白袍谋士 + 平视正面', comp='三分法', eye='为首的降派', focus='锁定点案沿的从容', stab='stable',
         h3='Holding <Picture 1>, the sagely strategist field each attack and refutes them one by one, tapping a fingertip off the table edge at the crux; static shot, the leading defeatist still refuses to yield and reaches for old precedent.'),
       dict(b=[30,31],sec=6,size='close',cam='Static Shot',ch=['C05'],pr=[],
         frame='特写，孔明待他说完轻轻一摆手不紧不慢接过话头，一句昔年成败未必今日定局把话钉住',
         shot='固定镜头近切，白袍谋士等他说完，轻轻一摆手接过话头，一句把昔年与今日分开',
         lens='85mm 长焦，浅景深', cp='白袍谋士 + 平视正面', comp='三分法', eye='抬旧例的降派', focus='锁定摆手接话的稳', stab='stable',
         h3='A static shot close-up of <Picture 2>: let him finish, the sagely strategist raises a hand and takes the turn, and with a low, settled voice (S2) closes it: <d>[Chinese] 昔年成败，未必就是今日定局。</d>'),
      ]))
    s.append(dict(sceneId='S09',
      blocking='那人怏怏退回，又有文臣绕弯试探；白袍谋士一句胆气反问，满堂再无人接话。',
      soundscape='退步的窸窣，一句绕弯的问，随即满堂衣料摩擦的静',
      music='弦乐落定，蓄着最后一击的余威',
      cuts=[
       dict(b=[32,33],sec=5,size='medium',cam='Static Shot',ch=['C05'],pr=[],
         frame='中景，那人张了张嘴驳不出来只得怏怏退了回去，又有文臣绕弯发问绕着法子试探孔明对降曹的真正看法',
         shot='固定镜头中景，那人驳不出来怏怏退回；又一名文臣绕弯试探，绕着法子想去掂量白袍谋士的真实态度',
         lens='50mm 标准，中浅景深', cp='白袍谋士 + 平视侧面', comp='三分法', eye='绕弯试探的文臣', focus='锁定沉稳立定的身姿', stab='stable',
         h3='Holding <Picture 1>, that man withdraws without a retort and another circles in to probe the visitor\u2019s true mind on surrender; static shot, the sagely strategist stands steady.'),
       dict(b=[34,34],sec=5,size='close',cam='Static Shot',ch=['C05'],pr=[],
         frame='特写，孔明一句胆气反问落定，把话头轻轻抛回满堂',
         shot='固定镜头近切，白袍谋士一句反问落定，把话头轻轻抛回满堂诸君',
         lens='85mm 长焦，浅景深', cp='白袍谋士 + 平视正面', comp='三分法', eye='绕弯的文臣', focus='锁定反问时的安然', stab='stable',
         h3='A static shot close-up of <Picture 2>: casting the question back upon them all, the sagely strategist speaks, and with an easy, quiet voice (S2) says: <d>[Chinese] 降或不降，问诸君自己的胆气便知。</d>'),
       dict(b=[35,35],sec=4,size='wide',cam='Static Shot',ch=['C05'],pr=[],
         frame='全景，满堂一时只剩衣料摩擦之声，再无人敢贸然接话',
         shot='固定镜头，满堂一时只剩衣料摩擦之声，再无人敢贸然接话',
         lens='35mm 广角，深景深', cp='堂景 + 平视', comp='三分法', eye='垂首沉默的一众', focus='锁定满堂冰一般的静', stab='stable',
         h3='The wide of <Picture 3> holds as only the rustle of robes remains and no one dares to speak; static shot.'),
      ]))
    s.append(dict(sceneId='S09',
      blocking='白袍谋士负手立堂中静静等沉默过去，最后一句收束，诸儒欲辩无言。',
      soundscape='堂上空极，静的呼吸声，一句话落定的余音',
      music='弦乐收进一个长音，替这场较量落定',
      cuts=[
       dict(b=[36,37],sec=6,size='medium',cam='Static Shot',ch=['C05'],pr=[],
         frame='中景，孔明负手立在堂中静静等那一片沉默过去，也不急着催促，最后才补上那句收束',
         shot='固定镜头中景，白袍谋士负手立于堂中，静静等沉默流过去，不催不逼，末了才补上收束一句',
         lens='50mm 标准，中浅景深', cp='白袍谋士 + 平视正面', comp='三分法', eye='满堂沉默的诸儒', focus='锁定静立等言的神色', stab='stable',
         h3='Holding <Picture 1>, the sagely strategist stands still in the middle of the hall letting the silence wash past, unhurried, before adding the closing line; static shot, and with a low, final voice (S2) he says: <d>[Chinese] 降是一时安，坐等曹贼分而食之。</d>'),
       dict(b=[38,38],sec=4,size='wide',cam='Static Shot',ch=['C05'],pr=[],
         frame='全景，底下诸儒欲辩无言，一个个面皮涨红，再没人敢轻易开口',
         shot='固定镜头，满堂文臣欲辩无言，一个个面皮涨红，再没人敢轻易开口',
         lens='35mm 广角，深景深', cp='堂景 + 平视', comp='三分法', eye='涨红脸的一众', focus='锁定全堂哑然的收束', stab='stable',
         h3='The wide of <Picture 2> closes the debate: the assembled officials argue with nothing to say, faces flushed, none daring to speak again; static shot.'),
      ]))
    # ---- scene2 ----
    s.append(dict(sceneId='S09',
      blocking='主公从旁听中缓缓站起，把降书一推，迎着满堂目光开口；众儒齐齐噤声。',
      soundscape='主公起身时衣料与推纸的响，他开口时满堂屏息',
      music='弦乐从低处抬升，一句压过满堂',
      cuts=[
       dict(b=[1,2],sec=5,size='medium',cam='Static Shot',ch=['C14'],pr=[],
         frame='中景，孙权旁听至今缓缓直起身子，眼底压着的火气浮上来一线，把案头的降书随手往旁一推，迎着满堂的目光站起',
         shot='固定镜头中景，一名年轻主公从旁听中缓缓直起身子，眼底浮起一线的火气，随手把降书往旁一推，迎着满堂目光站起',
         lens='50mm 标准，中浅景深', cp='主公 + 平视正面', comp='中心构图', eye='满堂的诸臣', focus='锁定立起身来的主公', stab='stable',
         h3='The cold open of scene two holds the hall of <Picture 1>: the young prince, who has sat listening, slowly straightens with a first flicker of ire rising in his eyes, pushes the surrender petition aside and stands to meet the court; static shot.'),
       dict(b=[3,3],sec=5,size='close',cam='Static Shot',ch=['C14'],pr=[],
         frame='特写，孙权一字一句落下那句，语气沉而坚定',
         shot='固定镜头近切，年轻主公一字一句落下，语气沉而坚定，压得满堂不敢出声',
         lens='85mm 长焦，浅景深', cp='主公 + 平视正面', comp='三分法', eye='满堂低下去的头', focus='锁定沉定的眼神', stab='stable',
         h3='A static shot close-up of <Picture 2>: word by word the young prince lets fall the line, and with a deep, unyielding voice (S1) declares: <d>[Chinese] 江东六郡，岂能拱手让人。</d>'),
       dict(b=[4,4],sec=3,size='wide',cam='Static Shot',ch=['C14'],pr=[],
         frame='全景，堂上众儒齐齐噤声，再不敢接话',
         shot='固定镜头，满堂文臣齐齐噤声，再不敢接话',
         lens='35mm 广角，深景深', cp='堂景 + 平视', comp='三分法', eye='低头的诸臣', focus='锁定满堂骤然屏息', stab='stable',
         h3='The wide of <Picture 3> holds as the assembled officials fall silent together, daring not to speak; static shot.'),
      ]))
    s.append(dict(sceneId='S09',
      blocking='主公踱到阶前扫过满堂低下去的头，一句句压下来，堂上更无人应声。',
      soundscape='主公踱步的脚步声，衣料轻响，满堂屏住的呼吸',
      music='弦乐沉下，一字一字往外压',
      cuts=[
       dict(b=[5,6],sec=7,size='medium',cam='Static Shot',ch=['C14'],pr=[],
         frame='中景，孙权踱到阶前扫过满堂低下去的头，声音沉却带着分量，一句句落下来',
         shot='固定镜头中景，年轻主公踱到阶前，扫过满堂低下去的头，声音沉而带分量，一字一句往外压',
         lens='50mm 标准，中浅景深', cp='主公 + 平视正面', comp='三分法', eye='满堂低下去的头', focus='锁定压下来的沉声', stab='stable',
         h3='Holding <Picture 1>, the young prince walks to the head of the steps, sweeping the lowered heads before him, voice heavy with weight, and with a slow, weighted voice (S2) he says: <d>[Chinese] 六郡将士，哪一个不是父老所养，岂能送与外人糟践。</d>'),
       dict(b=[7,7],sec=4,size='wide',cam='Static Shot',ch=['C14'],pr=[],
         frame='全景，堂上再无一人敢应声，连呼吸都放轻了三分',
         shot='固定镜头，堂上再无一人敢应声，连呼吸都放轻了三分',
         lens='35mm 广角，深景深', cp='堂景 + 平视', comp='三分法', eye='屏息的诸臣', focus='锁定满堂死一般的静', stab='stable',
         h3='The wide of <Picture 2> holds as no one in the hall dares answer, even breathing held lighter; static shot.'),
      ]))
    s.append(dict(sceneId='S09',
      blocking='主公收怒回到案后，朝白袍谋士看过来，眼底火气退去换成郑重，一句允诺落下。',
      soundscape='主公落座衣料的一声，随后的郑重开口',
      music='弦乐转缓透亮，一线决定的光',
      cuts=[
       dict(b=[8,9],sec=5,size='medium',cam='Static Shot',ch=['C14'],pr=[],
         frame='中景，孙权这才略略收了怒意转身回到案后坐下，他朝孔明看过来，眼底的火气退去大半添了几分郑重',
         shot='固定镜头中景，年轻主公略收怒意转身回到案后，朝白袍谋士看过来，眼底的火气退去大半，换成郑重',
         lens='50mm 标准，中浅景深', cp='主公 + 平视正面', comp='三分法', eye='堂中的白袍谋士', focus='锁定转成郑重的眼神', stab='stable',
         h3='Holding <Picture 1>, the young prince curbs his anger, turns back behind the desk, and looks to the sagely strategist, most of the fire gone from his eyes, replaced by solemnity; static shot.'),
       dict(b=[10,10],sec=6,size='close',cam='Static Shot',ch=['C14'],pr=[],
         frame='特写，孙权郑重地许下那层意思，与武臣再议联刘',
         shot='固定镜头近切，年轻主公郑重开口，许下联刘之事再与武臣详议',
         lens='85mm 长焦，浅景深', cp='主公 + 平视正面', comp='三分法', eye='白袍谋士', focus='锁定郑重的一诺', stab='stable',
         h3='A static shot close-up of <Picture 2>: with due gravity the young prince gives his word, and with a formal, sincere voice (S3) promises: <d>[Chinese] 先生既有为江东的诚意，联刘之事，容我与武臣再议。</d>'),
      ]))
    s.append(dict(sceneId='S09',
      blocking='白袍谋士长揖到底，直起身时目光在那封半掩的降书上停了一瞬，又收了回来。',
      soundscape='长揖起的衣料声，堂上微微回暖的呼吸声',
      music='弦乐低缓，蓄着一线未尽的深意',
      cuts=[
       dict(b=[11,12],sec=5,size='medium',cam='Static Shot',ch=['C05'],pr=[],
         frame='中景，孔明长揖到底心知火候已到不再多言，直起身，目光在那封半掩的降书上停了一瞬又收了回来',
         shot='固定镜头中景，白袍谋士长揖到底，心知火候到家便不再多言，直起身时目光落在那封半掩的降书上停了一瞬',
         lens='50mm 标准，中浅景深', cp='白袍谋士 + 平视侧面', comp='三分法', eye='案上那封降书', focus='锁定掠过降书的目光', stab='stable',
         h3='Holding <Picture 1>, the sagely strategist bows full and low, knowing the moment won, and as he straightens his gaze lingers a breath on the half-hidden surrender petition before slipping away; static shot.'),
       dict(b=[13,13],sec=4,size='close',cam='Static Shot',ch=['C05'],pr=[],
         frame='特写，孔明不多说，只朝孙权又微微一揖，这才跟着侍卫往后退步',
         shot='固定镜头近切，白袍谋士别无他言，只朝年轻主公又微微一揖，便随侍卫向后退步',
         lens='85mm 长焦，浅景深', cp='白袍谋士 + 平视正面', comp='三分法', eye='主公安坐的方向', focus='锁定退步前的一揖', stab='stable',
         h3='A static shot close-up of <Picture 2>: adding nothing, the sagely strategist makes one more bow toward the young prince and steps back with the attendants.'),
      ]))
    s.append(dict(sceneId='S09',
      blocking='侍卫快步进来耳语，主公神色微变却眼底一亮，抬手请客去后堂。',
      soundscape='侍卫疾步进来的声响，低语一声，主公说话时语调略抬',
      music='弦乐轻轻一扬，一点转机露头',
      cuts=[
       dict(b=[14,15],sec=5,size='medium',cam='Static Shot',ch=['C14'],pr=[],
         frame='中景，正在他要退出堂去，廊下一名侍卫快步进来凑到孙权耳畔低语了一句，孙权神色微变，眼底却掠过一丝亮色，冲孔明抬了抬手',
         shot='固定镜头中景，正要退出时一名侍卫快步进堂凑到年轻主公耳畔低语；主公神色微变，眼底却掠过一丝亮色，向白袍谋士抬了抬手',
         lens='50mm 标准，中浅景深', cp='主公与侍卫 + 平视侧面', comp='三分法', eye='进来耳语的侍卫', focus='锁定眼底亮起的那一瞬', stab='stable',
         h3='Holding <Picture 1>, just as he is about to leave a guard hastens in to murmur at the young prince\u2019s ear; his expression flickers but a light stirs in his eyes as he beckons the strategist; static shot.'),
       dict(b=[16,16],sec=5,size='close',cam='Static Shot',ch=['C14'],pr=[],
         frame='特写，孙权语气一提，请孔明先去后堂饮茶相候',
         shot='固定镜头近切，年轻主公语气一提，请白袍谋士先去后堂饮茶等候',
         lens='85mm 长焦，浅景深', cp='主公 + 平视正面', comp='三分法', eye='白袍谋士', focus='锁定神色转松的眉眼', stab='stable',
         h3='A static shot close-up of <Picture 2>: lifting his tone, the young prince invites the visitor to wait in the rear hall, and with a brighter, welcoming voice (S2) says: <d>[Chinese] 先生先去后堂饮茶，公瑾即刻便到。</d>'),
      ]))
    s.append(dict(sceneId='S09',
      blocking='白袍谋士脚步微顿回身望了一眼，嘴角勾起一点弧度，随人转进后堂；珠帘落下遮住身影。',
      soundscape='转身的衣料声，脚步渐远，层层珠帘轻响落下',
      music='弦乐缓缓收尾，留下一线悬念的光',
      cuts=[
       dict(b=[17,17],sec=5,size='medium',cam='Static Shot',ch=['C05'],pr=[],
         frame='中景，孔明脚步微顿回身望了一眼，嘴角缓缓勾起一点弧度',
         shot='固定镜头，白袍谋士脚下一顿回身望了一眼，嘴角缓缓勾起一点弧度',
         lens='50mm 标准，中浅景深', cp='白袍谋士 + 平视侧面', comp='三分法', eye='回望的方向', focus='锁定勾起的一点弧度', stab='stable',
         h3='Holding <Picture 1>, the sagely strategist pauses mid-step, glances back once and the corner of his mouth lifts in a faint arc; static shot.'),
       dict(b=[18,18],sec=5,size='wide',cam='Static Shot',ch=['C05'],pr=[],
         frame='全景，孔明迈步随人转进后堂，堂上层层珠帘落下，遮住了那道渐次明暗的身影',
         shot='固定镜头，白袍谋士迈步随人转入后堂，层层珠帘次第落下，遮住那道渐次明暗的身影',
         lens='35mm 广角，深景深', cp='堂景 + 平视', comp='中心构图', eye='转进后堂的方向', focus='锁定隔帘落下的一瞬', stab='stable',
         h3='The wide of <Picture 2> closes the episode: the sagely strategist steps with his guide into the rear hall as layer upon layer of bead curtain falls, veiling the fading figure; static shot.'),
      ]))
    return s

# (en_sound, en_music) 按 EP44 段序排列（16 段：scene1 10 + scene2 6）
ENSOUND_44 = [
 ("Low murmur rolling through the hall, the rustle of robes, one voice striking out and the chamber going quiet.","Low strings holding an unsettled note, middle-slow tempo, a sharpened edge underneath."),
 ("A few low acknowledgements, cloth and a cough, a short stunned silence as one is caught short.","Strings contracting and releasing, the pace running a touch fast."),
 ("Scattered echoes of support, one cold sneer, then a brief hush.","Strings turning heavy, pressing sentence by sentence."),
 ("An elder\u2019s sneering breath, then a thud as he is silenced.","A rising turn in the strings, then settling on a full stop."),
 ("Another scrape of one rising to his feet, a phrase of contention, then the quiet of a caught tongue.","A light quick string line, matching the fencing tongues."),
 ("An elder\u2019s low pronouncement, the hall going still after, only the sound of cloth.","Strings sinking, then pressing into near-stillness."),
 ("A single sharp clap, a call of approval, then the low murmur of officials drawing near.","Strings turning clear for a beat, shifting into a fresh tangle."),
 ("A run of exchanged arguments, a caught tongue or two, the rustle of cloth and wood.","Strings with a heavy accent on each line, sharpening as the rebuttals land."),
 ("A scrape of reluctant retreat, one circling question, then the silence of robes having no reply.","Strings settling, holding the residue of a final thrust."),
 ("The chamber near empty of sound, withheld breaths, the fading ring of a closing line.","Strings drawn into one long note, sealing the contest."),
 ("The lord rising, cloth and pushed paper, the hall holding its breath as he speaks.","Strings lifting from low, one line overriding the whole court."),
 ("The lord\u2019s steps on the dais, the rustle of clothes, the held breath of the hall.","Strings deepening, pressing outward word by word."),
 ("The scrape of the lord settling back, a solemn word following.","Strings easing transparent and bright, a crack of daylight in the decision."),
 ("The silk of a full low bow, breaths in the hall warming a little.","Strings low and unhurried, a thread of meaning left unresolved."),
 ("A guard\u2019s hastening steps, one low whisper, the lord\u2019s tone lifting a notch.","Strings lifting lightly, a glint of a turnabout in the second half."),
 ("The turn of a robe, footsteps fading, layer after layer of bead curtain ringing down.","Strings drawing to a slow close, leaving a thread of anticipation."),
]
if '--write44' in sys.argv:
    out44 = assemble(44, E44_cuts(), ENSOUND_44)
    test44 = {"source": orig["source"], "promptLang": "en", "params": orig["params"],
              "episodes": [{"ep": 44, "segments": out44}]}
    with open('_test44.json', 'w', encoding='utf-8') as f:
        json.dump(test44, f, ensure_ascii=False, indent=2)
    print("wrote _test44.json")
    print("EP44 segments:", len(out44), "total(s):", round(sum(segSeconds(s) for s in out44),1), "scene:", [s['sceneIndex'] for s in out44])

# =====================================================================
# EP 45  《蒋干盗书》 (scene1 S09 帐中灌酒盗书: C18 蒋干, C12 周瑜)  (scene2 S09 献信斩水军: C18, C04 曹操)
# C18=the flustered envoy  C12=the composed young general  C04=the mighty northern warlord
# =====================================================================
def E45_cuts():
    s=[]
    s.append(dict(sceneId='S09',
      blocking='帐中灯烛摇曳，酒气混着江风；白面说客被人引着入帐，一步三看只顾理袖，年轻将军迎到帐口一把拉住手腕。',
      soundscape='帐中灯烛摇曳，酒气混着江风，来客入帐时衣料的窸窣与脚步声',
      music='低音弦乐压着一个未落的音，中慢速，暗藏机锋',
      cuts=[
       dict(b=[1,2],sec=5,size='medium',cam='Static Shot',ch=['C18','C12'],pr=[],
         frame='中景，冷开场：帐中灯烛摇曳，酒气混着江风扑进来，一名白面说客被人引着往帐里走，一步三看，只顾着理衣袖',
         shot='固定镜头，帐中灯烛摇曳，一名白面说客被人领着走入帐内，边走边四处打量，一边整理衣袍',
         lens='50mm 标准，中浅景深', cp='帐口 + 平视', comp='三分法', eye='帐内深处', focus='锁定随行理袖的来客', stab='stable',
         h3='The cold open holds the camp of <Picture 1>: candles wavering on wine-tainted night air, a flustered envoy being led into the tent, glancing about as he smooths his sleeves; static shot.'),
       dict(b=[3,3],sec=4,size='close',cam='Static Shot',ch=['C12'],pr=[],
         frame='特写，年轻将军迎到帐口，一把拉住来客手腕往回一攥，笑得眉梢都抬了起来，半真半假地先开口',
         shot='固定镜头近切，一名年轻将军迎到帐口，拉住来客的手腕，眉梢带着笑意抢先开口',
         lens='85mm 长焦，浅景深', cp='年轻将军 + 平视正面', comp='三分法', eye='白面说客', focus='锁定拉腕一笑的神采', stab='stable',
         h3='A static shot close-up of <Picture 2>: the composed young general welcomes the guest, seizing his wrist with a bright grin, and with a teasing, half-playful voice asks: <d>[Chinese] 子翼远来，可是替曹贼当说客？</d>'),
       dict(b=[4,4],sec=4,size='close',cam='Static Shot',ch=['C18'],pr=[],
         frame='特写，来客脸上讪了一讪，忙摆手连声否认，只说念着旧情来看故人',
         shot='固定镜头近切，来客被这一问问得尴尬，忙摆手连声否认，只说是来看故人',
         lens='85mm 长焦，浅景深', cp='白面说客 + 平视正面', comp='三分法', eye='举杯相迎的方向', focus='锁定摆手否认的窘态', stab='stable',
         h3='A static shot close-up of <Picture 3>: caught short, the nervous envoy waves his hands in hasty denial, insisting he merely missed an old friend.'),
      ]))
    s.append(dict(sceneId='S09',
      blocking='年轻将军不戳破，亲手拉客在案边坐下斟满一杯；来客一杯接一杯陪着饮，年轻将军借机朝帐侧兵丁使了个眼色。',
      soundscape='杯盏轻碰，斟酒入盏的一声，来客低低的吞咽声，渐渐含混的话音',
      music='弦乐轻提，宾主话里各藏一层',
      cuts=[
       dict(b=[5,6],sec=6,size='medium',cam='Static Shot',ch=['C12'],pr=[],
         frame='中景，年轻将军亲自把来客按在案边坐下，亲手斟上满满一杯酒，话里话外都要把军务堵在半句之前',
         shot='固定镜头中景，年轻将军亲自拉客在案边坐下，亲手斟满一杯，笑容里把话题圈在酒上',
         lens='50mm 标准，中浅景深', cp='年轻将军 + 平视侧面', comp='三分法', eye='案上酒杯', focus='锁定斟酒与封锁话头的从容', stab='stable',
         h3='Holding <Picture 1>, the young general of the camp personally seats the guest by the low table and pours a brimming cup himself; static shot, and with a blocking, offhand voice he says: <d>[Chinese] 今夜只说旧谊，不谈军务。</d>'),
       dict(b=[7,7],sec=3,size='medium',cam='Static Shot',ch=['C18'],pr=[],
         frame='中景，来客只好陪着饮，一杯接一杯，渐渐有了醉意',
         shot='固定镜头中景，来客不好推拒只好一杯接一杯陪着饮，目光渐渐有些发飘',
         lens='50mm 标准，中浅景深', cp='白面说客 + 平视侧面', comp='三分法', eye='酒杯', focus='锁定渐起醉意的神态', stab='stable',
         h3='Holding <Picture 2> in medium, the flustered visitor drinks along cup after cup, his head beginning to swim; static shot.'),
       dict(b=[8,8],sec=4,size='wide',cam='Static Shot',ch=['C12'],pr=[],
         frame='全景，趁来客低头的工夫，年轻将军朝帐侧一名兵丁使了个眼色，兵丁会意退了下去',
         shot='固定镜头，趁来客低头之际，年轻将军向帐侧一名兵丁递了个眼色，兵丁会意退出帐去',
         lens='35mm 广角，深景深', cp='帐内全景 + 平视', comp='中心构图', eye='退下帐的兵丁', focus='锁定递眼色的那一瞬', stab='stable',
         h3='The static shot pulls to a wide of <Picture 3>: as the visitor lowers his head, the young general flicks a glance at a guard by the tent side, who nods and withdraws.'),
      ]))
    s.append(dict(sceneId='S09',
      blocking='年轻将军举杯与他轻轻一碰，又慢悠悠斟一杯，指尖在杯沿一圈圈转着，目光未尽。',
      soundscape='两杯轻碰的一声，酒液入喉，指尖划过杯沿的细响',
      music='弦乐一线清明，一句一句往外递',
      cuts=[
       dict(b=[9,10],sec=6,size='medium',cam='Static Shot',ch=['C12'],pr=[],
         frame='中景，年轻将军举杯与他轻轻一碰，一面把话头圈在酒上，不给他留半分探问的空当',
         shot='固定镜头中景，年轻将军举杯与来客轻轻一碰，含笑把话头拦在军务之外',
         lens='50mm 标准，中浅景深', cp='年轻将军 + 平视侧面', comp='三分法', eye='杯中酒', focus='锁定碰杯时封锁话头的笑', stab='stable',
         h3='Holding <Picture 1> in medium, the young general clinks his cup lightly against the guest\u2019s, keeping all matters of war outside the talk; static shot, and with a gentle, measured voice he says: <d>[Chinese] 子翼，今夜你我，只把这杯酒喝尽便好。</d>'),
       dict(b=[11,12],sec=6,size='close',cam='Static Shot',ch=['C12'],pr=[],
         frame='特写，年轻将军不紧不慢又斟一杯，指尖在杯沿一圈圈转着，像是在忆旧，目光却未尽',
         shot='固定镜头近切，年轻将军慢悠悠再斟一杯，指尖绕着杯沿转圈，目光幽深，像是在追忆去岁的旧谊',
         lens='85mm 长焦，浅景深', cp='年轻将军 + 平视正面', comp='三分法', eye='杯沿指尖', focus='锁定忆旧却未尽的目光', stab='stable',
         h3='A static shot close-up of <Picture 2>: unhurriedly the young general pours again and circles a fingertip along the rim, eyes trailing into memory, and with an absent, knowing voice he says: <d>[Chinese] 我周瑜在江东这些年，谁递的酒都记得清。</d>'),
      ]))
    s.append(dict(sceneId='S09',
      blocking='来客眼皮发沉却强撑着，眼珠往案头那摞军报上瞟；帐外更声又过一更，烛火昏暗，年轻将军装作酩酊靠向案上。',
      soundscape='帐外更鼓又响过一更，烛火被风拨得噼啪，衣料摩擦声',
      music='弦乐转沉，布下一张网',
      cuts=[
       dict(b=[13,14],sec=5,size='medium',cam='Static Shot',ch=['C18'],pr=[],
         frame='中景，来客眼皮发沉却还是强撑着，眼珠偷偷往那摞军报上瞟，目光已和醉意打架',
         shot='固定镜头中景，来客眼皮发沉却强撑精神，眼珠时不时偷瞄案头那摞文书，眼底藏着谋算',
         lens='50mm 标准，中浅景深', cp='白面说客 + 平视侧面', comp='三分法', eye='案头那摞军报', focus='锁定偷瞟军报的眼神', stab='stable',
         h3='Holding <Picture 1> in medium, the visitor\u2019s eyelids grow heavy yet he forces himself alert, eyes stealing toward the stack of dispatches on the desk; static shot.'),
       dict(b=[15,16],sec=5,size='wide',cam='Static Shot',ch=['C12'],pr=[],
         frame='全景，帐外更声又响过一更，烛火被风吹得越发昏暗，年轻将军把那点目光尽收眼底，面上却装作酩酊靠向案上',
         shot='固定镜头，帐外更鼓又过一更，烛火昏暗，年轻将军把来客那眼光尽收眼底，却装出酩酊的样子往案上一靠',
         lens='35mm 广角，深景深', cp='帐内全景 + 平视', comp='三分法', eye='靠向案上的年轻将军', focus='锁定装作醉倒的从容', stab='stable',
         h3='The wide of <Picture 2> holds: a fresh watch-drum sounds beyond the tent, the candle bending in the wind, while the young general, having caught every glance, feigns drunkenness and leans closer over the desk; static shot.'),
      ]))
    s.append(dict(sceneId='S09',
      blocking='来客偷眼看看醉倒的年轻将军，又看案头军报，蹑手蹑脚凑到案前，指尖在纸间拨动，停在一封没封口的信上。',
      soundscape='放轻的脚步声，纸张翻动的簌簌，屏住的呼吸',
      music='弦乐收细，一根弦吊着',
      cuts=[
       dict(b=[17,18],sec=5,size='medium',cam='Static Shot',ch=['C18'],pr=[],
         frame='中景，来客偷眼看了看醉倒的年轻将军，又看案头那摞军报，喉结动了动，蹑手蹑脚凑到案前',
         shot='固定镜头中景，来客偷眼打量醉倒的年轻将军，又看向案头文书，喉结滚动，遂蹑手蹑脚凑近书案',
         lens='50mm 标准，中浅景深', cp='白面说客 + 平视侧面', comp='三分法', eye='案头军报', focus='锁定凑近书案的试探', stab='stable',
         h3='Holding <Picture 1> in medium, the flustered envoy peeks at the slumbering figure, then at the dispatches, swallows, and creeps up to the table; static shot.'),
       dict(b=[19,20],sec=5,size='close',cam='Static Shot',ch=['C18'],pr=[],
         frame='特写，来客先抓起几份旧军报草草扫了几眼见无甚要紧又原样放回，指尖在一封没封口的信上顿住',
         shot='固定镜头近切，来客先翻了几份旧文书，见无要紧又原样放回，指尖停在那一封没封口的信上',
         lens='85mm 长焦，浅景深', cp='白面说客 + 平视正面', comp='三分法', eye='那封没封口的信', focus='锁定指尖顿住的那一瞬', stab='stable',
         h3='A static shot close-up of <Picture 2>: first he flips through a few stale dispatches, finding nothing, and sets them back exactly as they lay, fingers lingering on an unsealed letter.'),
      ]))
    s.append(dict(sceneId='S09',
      blocking='来客屏着呼吸绕着那封没封口的信转了两圈，再三确证才敢去碰，把信往烛上凑近半寸借着亮光一字一字认。',
      soundscape='烛火明灭的微响，纸张凑近火的沙沙，压抑的吐息',
      music='一个低音稳住，恐惧压在心口',
      cuts=[
       dict(b=[21,22],sec=5,size='close',cam='Static Shot',ch=['C18'],pr=[],
         frame='特写，来客屏着呼吸，指尖绕着那封信转了两圈，再三确认没封口，才敢去碰',
         shot='固定镜头近切，来客屏息绕着那封信转了两圈，确认没有封口，这才伸手去碰',
         lens='85mm 长焦，浅景深', cp='白面说客 + 平视正面', comp='三分法', eye='那封信', focus='锁定确认后壮胆的一碰', stab='stable',
         h3='A static shot close-up of <Picture 1>: holding his breath, the nervous envoy circles the letter twice, confirming it is unsealed, before daring to touch it.'),
       dict(b=[23,24],sec=5,size='close',cam='Static Shot',ch=['C18'],pr=[],
         frame='特写，来客把信往烛上凑近半寸借着亮光一字一字认，又偷眼回看，确认睡得沉才把信纸一寸寸抽出',
         shot='固定镜头近切，来客把信凑近烛火半寸借着亮光逐字辨认，又回头看那醉倒的人，确认睡得沉才把纸一寸寸抽出',
         lens='85mm 长焦，浅景深', cp='白面说客 + 平视侧面', comp='三分法', eye='烛上的信纸', focus='锁定逐字辨认的紧张', stab='stable',
         h3='A static shot close-up of <Picture 2>: he raises the letter half an inch to the candle and reads it line by line, then glances back, finds the sleeper still deep, and draws the page free inch by inch.'),
      ]))
    s.append(dict(sceneId='S09',
      blocking='来客的手一顿屏着气听了半晌，确认帐里只有鼾声，才飞快把信纸卷紧塞进衣袖又把案面抹平，直起身见信上字样脸色蓦变。',
      soundscape='纸卷摩擦衣袖的细响，抹过案面的轻响，一声压低的倒吸气',
      music='弦乐抿紧，窃得之物贴着胸口发烫',
      cuts=[
       dict(b=[25,26],sec=5,size='close',cam='Static Shot',ch=['C18'],pr=[],
         frame='特写，来客的手一顿，屏着气听了一阵，确认帐里只有鼾声，这才飞快将信纸卷紧塞进贴身袖里，又把案面抹得看不出动过的痕迹',
         shot='固定镜头近切，来客手一顿，屏气听清帐里只有鼾声，飞快把信纸卷紧塞入贴身衣袖，又把案面抹平不留痕迹',
         lens='85mm 长焦，浅景深', cp='白面说客 + 平视正面', comp='三分法', eye='案面', focus='锁定抹平痕迹的麻利', stab='stable',
         h3='A static shot close-up of <Picture 1>: his hand freezes, he listens for a long held moment, and hearing only snores, rolls the letter tight into his inner sleeve, smoothing the desk so no trace shows.'),
       dict(b=[27,28],sec=5,size='medium',cam='Static Shot',ch=['C18'],pr=[],
         frame='中景，来客慢慢直起身，袖里的信纸贴着胸口，借着烛光见信上写着两个人联手的字样，脸色蓦地变了',
         shot='固定镜头中景，来客慢慢直起身，袖中信纸贴着胸口，烛光下瞥见信上写有两位将领联手的字样，脸色骤然一变',
         lens='50mm 标准，中浅景深', cp='白面说客 + 平视侧面', comp='三分法', eye='烛光里的信纸', focus='锁定脸色突变的瞬间', stab='stable',
         h3='Holding <Picture 2> in medium, he slowly straightens, the letter warm against his chest, and by the candlelight catches sight of a line naming two naval officers in league, his face suddenly paling; static shot.'),
      ]))
    s.append(dict(sceneId='S09',
      blocking='来客把信贴身收好，抿一口残酒压惊又整了整衣襟，借口值守披衣摸出帅帐；帐外江风一过，年轻将军缓缓睁眼眼底清明。',
      soundscape='更鼓一声，起身披衣的窸窣，帐帘掀动的风声，随即一片清明',
      music='弦乐缓缓松开，留下一个心知肚明的收尾',
      cuts=[
       dict(b=[29,30],sec=5,size='close',cam='Static Shot',ch=['C18'],pr=[],
         frame='特写，来客飞快将信塞进袖中，又回头看鼾声未断的年轻将军，长长舒了一口气',
         shot='固定镜头近切，来客将信重新塞入袖中，回看仍在安睡的年轻将军，长长舒出一口气',
         lens='85mm 长焦，浅景深', cp='白面说客 + 平视正面', comp='三分法', eye='安睡的方向', focus='锁定得手后松的那口气', stab='stable',
         h3='A static shot close-up of <Picture 1>: he thrusts the letter back into his sleeve, checks that the sleeper\u2019s snore has not broken, and lets out a long relieved breath.'),
       dict(b=[31,32],sec=5,size='medium',cam='Static Shot',ch=['C18'],pr=[],
         frame='中景，来客把信贴身收好，又端起一盏冷酒抿了一口压住心头的乱跳，特意整了整衣襟，深怕那封信露出一角',
         shot='固定镜头中景，来客将信贴身收好，抿一口残酒定神，又特意整了整衣襟，生怕露出信角惹人起疑',
         lens='50mm 标准，中浅景深', cp='白面说客 + 平视侧面', comp='三分法', eye='衣襟', focus='锁定压惊理衣的谨慎', stab='stable',
         h3='Holding <Picture 2> in medium, he tucks the letter away, sips a swallow of cold wine to steady himself, and adjusts his collar, fearful the letter\u2019s edge might show; static shot.'),
       dict(b=[33,33],sec=4,size='close',cam='Static Shot',ch=['C12'],pr=[],
         frame='特写，更鼓一响，来客借口值守披衣摸出帅帐；帐外江风一过，方才醉卧的年轻将军缓缓睁开眼，眼底一片清明',
         shot='固定镜头近切，更鼓响过，来客借口值守披衣出了帐；江风一掀帐帘，方才醉卧的年轻将军缓缓睁眼，眸底清明无一丝醉意',
         lens='85mm 长焦，浅景深', cp='年轻将军 + 平视正面', comp='三分法', eye='掀动的帐帘', focus='锁定睁眼时的一片清明', stab='stable',
         h3='A static shot close-up of <Picture 3>: as the night-drum sounds, the visitor slips out on duty as an excuse, and once the tent flap stirs in the river wind, the slumbering-looking young general opens his eyes, wide and clear.'),
      ]))
    # ---- scene2 ----
    s.append(dict(sceneId='S09',
      blocking='来客连夜过江摸进帐中，把偷来的信双手奉到案前；帐上霸主披着袍子在灯下展开信，才看几行眉头就拧起来。',
      soundscape='过江的水声，靴子踏过营地，信件落在案上，一声压低的邀功禀报',
      music='低音弦乐合拢，一网收口',
      cuts=[
       dict(b=[1,2],sec=5,size='medium',cam='Static Shot',ch=['C18'],pr=[],
         frame='中景，来客连夜过江，摸着黑钻进帐中，把那封偷来的信双手奉到案前，压低声音一脸邀功',
         shot='固定镜头中景，来客连夜赶回，摸黑钻进帐内，将那封窃来的信双手奉到案前，压低声音满脸邀功之色',
         lens='50mm 标准，中浅景深', cp='白面说客 + 平视侧面', comp='三分法', eye='案上那封信', focus='锁定奉信时的一脸邀功', stab='stable',
         h3='Holding <Picture 1> in medium, the envoy crosses the river by night and slips into the tent, laying the stolen letter on the desk with both hands, and with an eager, low voice he reports: <d>[Chinese] 丞相，末将探得一件要紧的事。</d>'),
       dict(b=[3,4],sec=5,size='close',cam='Static Shot',ch=['C04'],pr=[],
         frame='特写，帐上霸主披着袍子在灯下展开信，才看几行眉头就拧了起来，反复看了三遍，指节捏得案角咯咯作响',
         shot='固定镜头近切，一位披袍的北方雄主在灯下展开信，才看几行便拧起眉头，反复看罢三遍，指节捏得案角咯咯直响',
         lens='85mm 长焦，浅景深', cp='帐上霸主 + 平视正面', comp='三分法', eye='信纸', focus='锁定越看越沉的脸色', stab='stable',
         h3='A static shot close-up of <Picture 2>: the mighty northern warlord, robe over his shoulders, unfolds the letter by lamplight and frowns within a few lines, rereading it three times as his knuckles whiten on the table edge.'),
      ]))
    s.append(dict(sceneId='S09',
      blocking='帐上霸主反复看信面色越沉，来客点头哈腰添油加醋，见脸色不对又赶紧补一句；霸主没接话只把信往灯火上虚晃。',
      soundscape='座椅承重的吱呀，展纸的声音，屏息读信的静，一句僵硬的应答',
      music='弦乐一句一个重音，越读越冷',
      cuts=[
       dict(b=[5,5],sec=5,size='close',cam='Static Shot',ch=['C04'],pr=[],
         frame='特写，帐上霸主读信时声音冷得像冰碴子，一字一字把信上那两个人的名目念出来',
         shot='固定镜头近切，帐上霸主读信时声音冷得像冰碴子，一字一句念出信上的名字',
         lens='85mm 长焦，浅景深', cp='帐上霸主 + 平视正面', comp='三分法', eye='信纸', focus='锁定冷到骨子里的神情', stab='stable',
         h3='A static shot close-up of <Picture 1>: colder by the line, the northern warlord reads the two signatures aloud, and with a voice cold as ice he says: <d>[Chinese] 蔡瑁、张允，他二人写给东吴的。</d>'),
       dict(b=[6,7],sec=5,size='medium',cam='Static Shot',ch=['C18'],pr=[],
         frame='中景，来客在旁点头哈腰，又添油加醋说了几句对方如何待自己亲厚，见帐上霸主脸色不对，又赶紧补一句说那二位帐下颇多降卒可用',
         shot='固定镜头中景，来客在旁点头哈腰，添油加醋地补话；见座上一人脸色越发不对，又赶紧补一句说那位将军帐下颇多可用之卒',
         lens='50mm 标准，中浅景深', cp='白面说客 + 平视侧面', comp='三分法', eye='帐上霸主', focus='锁定看人眼色补话的机警', stab='stable',
         h3='Holding <Picture 2> in medium, the envoy nods and bows, pouring in extra details of his warm welcome, then, seeing the mood darken, hurries to add that much usable manpower sits under those two commanders; static shot.'),
       dict(b=[8,8],sec=5,size='close',cam='Static Shot',ch=['C04'],pr=[],
         frame='特写，帐上霸主没接话，只把那封信往灯火上虚虚一晃，像是在掂它的真假',
         shot='固定镜头近切，帐上霸主未置一词，只将那封信在灯火上虚虚一晃，似在掂量其真假',
         lens='85mm 长焦，浅景深', cp='帐上霸主 + 平视正面', comp='三分法', eye='灯火', focus='锁定掂信时眯起的眼', stab='stable',
         h3='A static shot close-up of <Picture 3>: the northern warlord answers nothing, only passing the letter over the lamp-flame as if weighing its truth.'),
      ]))
    s.append(dict(sceneId='S09',
      blocking='帐上霸主自言自语似的开口，眼底一线杀机；来客心头暗喜面上惊惶，霸主沉吟良久把信往案上一搁像是下定了决心。',
      soundscape='一声压低的倒吸气，指节扣案沿的轻响，终于把信搁下的沉闷',
      music='弦乐压到近无声，杀意潜伏在字缝里',
      cuts=[
       dict(b=[9,10],sec=6,size='close',cam='Static Shot',ch=['C04'],pr=[],
         frame='特写，帐上霸主自言自语似的开口，眼底一线杀机若隐若现',
         shot='固定镜头近切，帐上霸主宛如自言自语地低声开口，眼底一线杀意若隐若现',
         lens='85mm 长焦，浅景深', cp='帐上霸主 + 平视正面', comp='三分法', eye='案上信纸', focus='锁定杀机浮现的眼神', stab='stable',
         h3='A static shot close-up of <Picture 1>: almost to himself the northern warlord lets the words fall, and with a low, brooding voice he says: <d>[Chinese] 水军的命脉，偏偏捏在二人手里。</d>'),
       dict(b=[11,12],sec=7,size='medium',cam='Static Shot',ch=['C04'],pr=[],
         frame='中景，来客听他话里透出杀机心头暗喜面上却作惊惶；帐上霸主沉吟良久，终于把信往案上一搁，像是下定了决心',
         shot='固定镜头中景，来客听出话里透出杀机，心头暗喜面上却一派惊惶；帐上霸主沉吟良久，终于把信搁下，像是拿定了主意',
         lens='50mm 标准，中浅景深', cp='帐上霸主 + 平视正面', comp='三分法', eye='案上信纸', focus='锁定落定决心的刹那', stab='stable',
         h3='Holding <Picture 2> in medium, at the murderous edge in his words the envoy\u2019s heart leaps though his face shows alarm; the northern warlord deliberates long, then sets the letter down as if resolved; static shot, and with a settled voice he adds: <d>[Chinese] 他二人若真背我，水军便是我心腹之患。</d>'),
      ]))
    s.append(dict(sceneId='S09',
      blocking='帐上霸主把信往案上重重一拍腾地站起，二位水军将领应召而来尚未站稳，被一句自相矛盾的问话问得磕绊。',
      soundscape='一掌拍案的闷响，腾起的衣料声，兵靴应答的脚步声',
      music='一声重击，弦线绷上令下',
      cuts=[
       dict(b=[13,14],sec=6,size='close',cam='Static Shot',ch=['C04'],pr=[],
         frame='特写，帐上霸主不答，只把信往案上重重一拍，眼底杀意一闪，腾地站起',
         shot='固定镜头近切，帐上霸主不答话，只把信往案上重重一拍，眼底杀意一闪，猛地站起',
         lens='85mm 长焦，浅景深', cp='帐上霸主 + 平视正面', comp='三分法', eye='帐口', focus='锁定拍案而起的一瞬', stab='stable',
         h3='A static shot close-up of <Picture 1>: without answering, the northern warlord slams the letter back onto the desk, murder flaring in his eyes as he rises, and with a low, tight voice he orders: <d>[Chinese] 传水军二将前来问话！</d>'),
       dict(b=[15,16],sec=5,size='medium',cam='Static Shot',ch=['C04'],pr=[],
         frame='中景，二位水军将领应召而来尚未站稳，帐上霸主劈头便问一句自相矛盾的问话，二人答得磕绊，反倒坐实了他的疑心',
         shot='固定镜头中景，两位水军将领应召进帐还未站稳，帐上霸主劈头便抛出一道自相矛盾的问话，二人答得期期艾艾',
         lens='50mm 标准，中浅景深', cp='帐上霸主 + 平视侧面', comp='三分法', eye='应召而来的二将', focus='锁定问话时逼人的气势', stab='stable',
         h3='Holding <Picture 2> in medium, the two water-army commanders answer the summons, and before they are steady the northern warlord throws a self-contradicting question at them, their stammered answers only hardening his suspicion; static shot.'),
      ]))
    s.append(dict(sceneId='S09',
      blocking='帐上霸主听罢猛地一拍桌案，喝令把二人拿下拖出去斩；二将喊冤却被兵卒架住，一路拖出帐去。',
      soundscape='桌案再拍的重响，甲胄拖地的刮擦，两声喊冤被沉沉人声压没',
      music='短促的战鼓，刀已出鞘',
      cuts=[
       dict(b=[17,18],sec=6,size='close',cam='Static Shot',ch=['C04'],pr=[],
         frame='特写，帐上霸主听罢猛地一拍桌案，一字一登，不留半分情面地喝令左右拿下',
         shot='固定镜头近切，帐上霸主听罢猛地一拍桌案，一字一字落得斩钉截铁，喝令左右动手拿下',
         lens='85mm 长焦，浅景深', cp='帐上霸主 + 平视正面', comp='三分法', eye='帐外', focus='锁定斩钉截铁的怒意', stab='stable',
         h3='A static shot close-up of <Picture 1>: a final slap of the table, and the northern warlord, word by word with no mercy, declares: <d>[Chinese] 勾结东吴，背我反我，拖下去斩！</d>'),
       dict(b=[19,19],sec=4,size='wide',cam='Static Shot',ch=['C04'],pr=[],
         frame='全景，二将喊冤，却被如狼似虎的兵卒架住，一路拖出帐去，帐外传来两声急促的喊冤，旋即被沉沉人声压了下去',
         shot='固定镜头，二将喊冤却被如狼似虎的兵卒架住，一路拖出帐去；帐外传来两声急促的喊冤，旋即被沉沉的人声压没',
         lens='35mm 广角，深景深', cp='帐内全景 + 平视', comp='三分法', eye='被拖出去的方向', focus='锁定二将被拖出的混乱', stab='stable',
         h3='The static shot widens to <Picture 2>: the two captains call out in innocence but are seized by fierce guards and dragged from the tent, two muffled cries cut short by the dark outside.'),
      ]))
    s.append(dict(sceneId='S09',
      blocking='霸主站起身走到帐口望着被拖远的两道黑影久久没转身；来客想凑上来再说两句却被一个眼神止住，只得讪讪收声。',
      soundscape='走到帐口的风声，帐帘掀起，来客讪讪收声的静',
      music='低音回落，一击过后的钝寂',
      cuts=[
       dict(b=[20,21],sec=5,size='wide',cam='Static Shot',ch=['C04'],pr=[],
         frame='全景，帐上霸主站起身走到帐口，望着被拖远的两道黑影久久没有转身；夜风掀起帐帘，露出一角青黑的旷野',
         shot='固定镜头，帐上霸主走到帐口，望着被拖远的两道黑影久久不动；夜风掀起帐帘，露出帐外一角青黑的旷野',
         lens='35mm 广角，深景深', cp='帐口全景 + 平视', comp='中心构图', eye='被拖远的方向', focus='锁定长久不动的背影', stab='stable',
         h3='The wide of <Picture 1> holds: the northern warlord walks to the tent mouth and watches the two black shapes dragged far off, not turning for some moments, the night wind lifting the flap on a stretch of dark wilds; static shot.'),
       dict(b=[22,23],sec=5,size='medium',cam='Static Shot',ch=['C04'],pr=[],
         frame='中景，来客刚想凑上来再说两句，却被帐上霸主一个眼神止住，只得讪讪收声；霸主重新落座，指尖点在案角，半晌没有开口',
         shot='固定镜头中景，来客又想凑上来多言，却被帐上霸主一个眼神制止，只得讪讪收声；霸主重新落座，指尖轻点案角，良久不语',
         lens='50mm 标准，中浅景深', cp='帐上霸主 + 平视侧面', comp='三分法', eye='案角', focus='锁定落座后长久的沉默', stab='stable',
         h3='Holding <Picture 2> in medium, the envoy edges forward for one more word but is stopped by a single glance, retreating sheepishly, while the northern warlord seats himself again, fingertip on the table corner, long silent; static shot.'),
      ]))
    s.append(dict(sceneId='S09',
      blocking='夜更深了，帐中只剩灯花噼啪；帐帘一落，霸主缓缓坐回案前，低头又看那封信，眼底杀意里闪过一丝犹疑。',
      soundscape='灯花噼啪，衣袍落座的声音，夜风绕帐',
      music='弦乐收进一个长音，犹疑在杀意下翻了个水花',
      cuts=[
       dict(b=[24,25],sec=5,size='wide',cam='Static Shot',ch=['C04'],pr=[],
         frame='全景，夜更深了帐中只剩灯花不时噼啪作响，帐帘一落，帐上霸主盯着方才被拖出去的方向，缓缓坐回案前',
         shot='固定镜头，夜更深，帐中只剩灯花时而噼啪作响；帐帘落下，帐上霸主盯着方才人被拖走的方向，缓缓落回案前',
         lens='35mm 广角，深景深', cp='帐内全景 + 平视', comp='中心构图', eye='帐帘', focus='锁定缓缓落座的身影', stab='stable',
         h3='The static shot wide of <Picture 1>: the night deepens and only the crackle of the lamp-wick remains; the flap falls, and the northern warlord, eyes on the spot just drained of its prisoners, slowly sits back at the desk.'),
       dict(b=[26,26],sec=5,size='close',cam='Static Shot',ch=['C04'],pr=[],
         frame='特写，帐上霸主低头又看了一眼那封墨迹未干的信，眼底的杀意里，忽而闪过一丝说不清的犹疑',
         shot='固定镜头近切，帐上霸主低头再看一眼那封墨迹未干的信，眼底的杀意里，忽而闪过一丝说不清的犹疑',
         lens='85mm 长焦，浅景深', cp='帐上霸主 + 平视正面', comp='三分法', eye='那封信', focus='锁定杀意下的那一丝犹疑', stab='stable',
         h3='A static shot close-up of <Picture 2>: he looks once more at the still-drying letter, and through the killing glare a thread of unnameable doubt flickers.'),
      ]))
    return s

# (en_sound, en_music) 按 EP45 段序排列（15 段：scene1 8 + scene2 7）
ENSOUND_45 = [
 ("A single bedchamber of the tent: candles wavering, the wine-scented night breeze, a visitor\u2019s steps as he is led in, robes being straightened.","Low strings over a held drone, slow, a veiled game beneath the wine."),
 ("A clink of cups, a warm hand clasping a wrist, wine poured full to the brim.","Strings lifting gently, an easy host in the tone."),
 ("Cups meeting in a toast, the gulp of wine, faint voices murmuring in the lamplight.","Light middle-string phrases, unhurried, half-hidden meanings."),
 ("The watch drum sounding past another watch, the candle hissing as the wind stirs it.","Strings deepening, a quiet ploy settling into the tent."),
 ("Cautious footsteps padding near the desk, the swish of papers turned, a held breath.","Strings thinning to near silence, tension drawn tight."),
 ("A fingertip circling around a folded paper, the faint rustle of the unsealed letter.","A single low note holding, rising fear beating under it."),
 ("The dry slide of paper being rolled and tucked into a sleeve, a smoothing of the desk, quick breaths.","Strings pressing quietly, a stolen prize warming in the cloth."),
 ("A stir of the night wind at the tent flap, then a breath of released tension as two eyes open.","Strings releasing into a wry, knowing close."),
 ("Night water against a crossing, boots crossing the camp, a letter laid on the table, a low eager voice.","Low strings arriving, drawing the trap\u2019s jaws shut."),
 ("The creak of the seat as he leans over the lamp, paper unfolded, tense silence reading line by line.","Strings pressing syllable by syllable, growing colder."),
 ("A short intake of breath, words dropped low like falling ice, the scratch of a fingertip on the table edge.","Strings contracting to near stillness, murder lurking under the surface."),
 ("A heavy slam of hand on the desk, a snarl rising, soldiers\u2019 boots answering the order.","A percussive strike, strings snapping into command."),
 ("A thunderous slap of the table, armor scraping as men are dragged out, muffled cries swallowed by the night.","Drums striking short and hard, an execution drawing the air taut."),
 ("Steps to the tent mouth, canvas stirring in the night wind, the rustle of an uneasy guest pulling back.","Low strings ebbing, a heavy stillness after the blow."),
 ("The dying crackle of the lamp wick, the last rustle of a robe settling, a lone night wind.","Strings fading to a single held note, doubt glinting beneath the triumph."),
]
if '--write45' in sys.argv:
    out45 = assemble(45, E45_cuts(), ENSOUND_45)
    test45 = {"source": orig["source"], "promptLang": "en", "params": orig["params"],
              "episodes": [{"ep": 45, "segments": out45}]}
    with open('_test45.json', 'w', encoding='utf-8') as f:
        json.dump(test45, f, ensure_ascii=False, indent=2)
    print("wrote _test45.json")
    print("EP45 segments:", len(out45), "total(s):", round(sum(segSeconds(s) for s in out45),1), "scene:", [s['sceneIndex'] for s in out45])

# =====================================================================
# 全批组装写回：ep41-45，删除 seedScenes，segments 填充
# =====================================================================
ALL = [(41, SEG41, ENSOUND), (42, SEG42, ENSOUND_42), (43, E43_cuts(), ENSOUND_43),
       (44, E44_cuts(), ENSOUND_44), (45, E45_cuts(), ENSOUND_45)]
def write_all():
    new_eps = []
    for epnum, segdatums, ens in ALL:
        segs = assemble(epnum, segdatums, ens)
        new_eps.append({"ep": epnum, "segments": segs})
    RES = {"source": orig["source"], "promptLang": orig["promptLang"], "params": orig["params"],
           "episodes": new_eps}
    with open(SRC, 'w', encoding='utf-8-sig') as f:
        json.dump(RES, f, ensure_ascii=False, indent=2)
    return new_eps

if '--writeall' in sys.argv:
    new_eps = write_all()
    print("wrote storyboard-batch-9.json")
    for e in new_eps:
        tot = sum(segSeconds(s) for s in e['segments'])
        ncut = sum(len(s['cuts']) for s in e['segments'])
        print(f"EP{e['ep']}: segments={len(e['segments'])} cuts={ncut} total(s)={round(tot,1)} scene={[s['sceneIndex'] for s in e['segments']]}")