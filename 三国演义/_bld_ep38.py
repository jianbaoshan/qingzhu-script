# -*- coding: utf-8 -*-
import json
import _bld_helpers as H

board = json.load(open(r'd:\study\GitHub\shuohao-skills\三国演义\_board_after38.json','w') or open(r'd:\study\GitHub\shuohao-skills\三国演义\_board0.json','w')) if False else None
# Load base preview: reconstruct existing board (eps 36-38 with 16 segs)
raw = open(H.P, encoding='utf-8-sig').read()
suffix='\n        }\n      ]\n    },\n    {"ep":39,"segments":[]},\n    {"ep":40,"segments":[]}\n  ]\n}\n'
board = json.loads(raw + suffix)
script = json.load(open(H.SP, encoding='utf-8-sig'))

frames_shots_38b = [
    dict(beats=[19,19],sec=4.0,size='medium',camera='Static Shot',chars=['C03'],props=[],
         frame='中景，张飞在坡上瞪圆大眼，满是不平地嚷道才打胜仗就要撤这仗岂不是白赢了，一手提着长矛，一脸不服。',
         shot='固定镜头，虬髯大汉立于坡上瞪圆眼睛，随手把长矛往地上一顿，满是不平，语调又急又冲。',
         cpos='虬髯大汉 + 平视正面',comp='中心构图',eye='下方城头',foc='锁定虬髯大汉不忿的神情',
         h3='a burly bearded general on the slope stamps his long spear on the ground, eyes wide and indignant, and with an impatient, heated voice (S1) he bursts out'),
    dict(beats=[20,20],sec=5.0,size='medium',camera='Static Shot',chars=['C01'],props=[],
         frame='中景，刘备按住张飞的臂膀，目光温和又清醒，平静道三弟胜了就给咱们挣了拔营的工夫已是赚的。',
         shot='固定镜头，面容仁厚的男子按住身旁猛汉的臂膀，语气平稳地将对方的躁意按捺下来。',
         cpos='刘备 + 平视正面',comp='三分法',eye='对旁边之人',foc='锁定刘备按下的手',
         h3='a serene-faced man lays a steady hand on the burly one\'s arm, his tone calm and leveling, and with a measured voice (S1) he reasons'),
    dict(beats=[21,21],sec=3.0,size='wide',camera='Static Shot',chars=['C01','C05'],props=[],
         frame='全景，残烧将熄的城头上，刘备与诸葛亮并肩而立，望着北方，两人脸上都凝着重量。',
         shot='固定机位，两抹身影并肩立在半焦的城垛前，一同凝视寂静的北方，神色沉凝。',
         cpos='双人背影 + 平视侧面',comp='对称',eye='北方的天际',foc='锁定并肩站立的剪影',
         h3='a wide view of the two men standing shoulder to shoulder on the scorched parapet, both gazing north in shared solemn silence'),
    dict(beats=[22,22],sec=4.5,size='close',camera='Push In',chars=['C01'],props=[],
         frame='特写，刘备望着北方，眉宇不展，轻声道两把火虽解此围可曹操岂肯善罢甘休，火烬在瞳中一明一灭。',
         shot='镜头轻推，面容仁厚的男子凝视北方天际，眉头微锁，语带一丝深远的忧虑。',
         cpos='刘备 + 平视正面',comp='三分法',eye='北方天际',foc='锁定刘备微皱的眉',stability='slight-shake',
         h3='a slow push-in frames the serene-faced man staring at the northern horizon, brows knit, and with a low, uneasy voice (S1) he confides'),
    dict(beats=[23,23],sec=6.0,size='close',camera='Static Shot',chars=['C05'],props=[],
         frame='特写，诸葛亮执扇于侧，神色端凝道故此当预作退计不可恋战皇叔收拾行装要紧，目光清亮见底。',
         shot='固定特写，鹤氅青年执扇近前，语气笃定而不容拖延，目光清亮地望向身旁这位主公。',
         cpos='诸葛亮 + 平视正面',comp='中心构图',eye='对旁边之人',foc='锁定鹤氅青年的眼',
         h3='a close static shot on the young strategist folding his fan, his tone firm and decisive, and with a clear, resolute voice (S1) he urges'),
    dict(beats=[24,24],sec=3.0,size='extreme-wide',camera='Static Shot',chars=[],props=[],
         frame='大远景，天际残阳如血，漫天霞光铺满将熄的战场，一只孤雁掠过昏黄的云边。',
         shot='固定远镜，苍茫天际一丸残阳正在沉落，血色染红半边云天，显出一场更大风暴将至的前奏。',
         cpos='天际全景 + 平视远眺',comp='三分法',eye='残阳',foc='锁定血色残阳',
         h3='an extreme wide static shot: a blood-red setting sun stains the fading battlefield, a lone wild goose gliding across the amber clouds'),
]

overall_sound_38='The scattered flames hiss and die out on the charred town wall, wind carries the faint smell of smoke, and the clamour of the routed army fades into the distance.'
music_38='Low strings with a sombre, deliberate pulse, at a slow tempo, steadied and resolute.'
ep38=[e for e in board['episodes'] if e['ep']==38][0]
ep38['segments'].append(H.seg_from_specs('E38-16',2,frames_shots_38b[0:3],38,overall_sound_38,music_38,script))
ep38['segments'].append(H.seg_from_specs('E38-17',2,frames_shots_38b[3:6],38,overall_sound_38,music_38,script))
print('ep38 segs', len(ep38['segments']))
board0=board
json.dump(board, open(r'd:\study\GitHub\shuohao-skills\三国演义\_board_after38.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print('saved after38 (E37 still scene2 incomplete? check ep38 total)')
tot=sum(round(sum(c['seconds'] for c in s['cuts']),1) for s in ep38['segments'])
print('ep38 total seconds', round(tot,1))