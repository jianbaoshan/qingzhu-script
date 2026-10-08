# -*- coding: utf-8 -*-
"""补齐 storyboard-batch-8.json（ep36-40）+ 合规。

来源：
- ep36(16段) / ep37(16段) / ep38(17段) 已成品切分（来自截断文件，cut 级高质量）
- ep39 scene1(12段) 来自 _bld_ep39.py
- ep39 scene2 / ep40 全两场 全部新作
- 每段补中文 blocking（必填）+ soundscape + music（中文）
- ep37 总时长 149.5 < 153：上调单切段 E37-06/11/16 秒数
- 删重复/空 ep39、删 seedScenes、UTF-8 无 BOM 写回
"""
import json, os
from collections import defaultdict

P = r'd:\study\GitHub\shuohao-skills\三国演义\storyboard-batch-8.json'
AF39 = r'd:\study\GitHub\shuohao-skills\三国演义\_board_after39.json'
SP = r'd:\study\GitHub\shuohao-skills\三国演义\script.json'

import sys
sys.path.insert(0, r'd:\study\GitHub\shuohao-skills\三国演义')
import _bld_helpers as H


def dedupe_eps(board):
    d = defaultdict(list)
    for e in board['episodes']:
        d[e['ep']].append(e)
    eps = [max(v, key=lambda x: len(x.get('segments', []))) for v in d.values()]
    eps.sort(key=lambda x: x['ep'])
    return eps


# ============================================================
# 1) 从 _board_after39 载入成品段
# ============================================================
board = json.load(open(AF39, encoding='utf-8'))
script = json.load(open(SP, encoding='utf-8-sig'))
eps = dedupe_eps(board)
src = {e['ep']: e for e in eps}
ep36 = src[36]; ep37 = src[37]; ep38 = src[38]; ep39s1 = src[39]['segments']


def segs_of(ep): return ep['segments']


# ============================================================
# 2) blocking / soundscape(中) / music(中) 映射（按段 id）
#    音景/配乐由已内嵌在 h3Prompt 的英文版译成中文（不复述台词）
# ============================================================

# ---- ep36 blocking（草庐·草堂，刘备=软袍贵族在右侧，诸葛亮=鹤氅青年在左侧，隔矮案对面） ----
B36 = {
 'E36-01': '刘备立于竹篱外画面右，面朝草庐；诸葛亮在庐内柴扉前居画面左，两人隔门槛相距约两步，互相打量的视线交汇于门槛一线。',
 'E36-02': '堂内矮案横亘居中，诸葛亮坐画面左边、刘备坐画面右边，两人隔着矮案约一臂之距，皆面朝对方，刘备前倾拱手。',
 'E36-03': '诸葛亮居画面右上执壶，刘备于画面右下微倾上身，两人隔矮案边缘，直线间距半臂，目光落在手中的茶盏。',
 'E36-04': '诸葛亮独自居画面中偏左执扇，身前矮案上摊着茶盏，面向画面右的刘备，视线沿案面一路扫向外间地势。',
 'E36-05': '诸葛亮居画面左收扇指案，刘备在画面右前倾聆听，两人隔矮案约一臂，诸葛亮指尖落在二人之间的案上地势。',
 'E36-06': '诸葛亮居画面左，刘备在画面右蹙眉发问，两人隔矮案相对，间距一臂，灯光从右窗斜入照亮两人侧脸。',
 'E36-07': '诸葛亮居中偏左执扇，面向画面右的刘备，身前景矮案空置，两人隔案约一臂之距。',
 'E36-08': '诸葛亮居画面左执扇正色，刘备在画面右双眼放光，隔矮案对视，间距一臂，茶案上蒸气轻袅。',
 'E36-09': '张飞立于门外画面右探头插话，刘备在堂内画面左回身低斥；门外关羽画面右按住张飞将其带回，草庐门槛分隔内外两区。',
 'E36-10': '诸葛亮居画面左窗前摇扇，面朝窗外；刘备在画面右正色追问，两人相隔一臂，视线错开并不对视。',
 'E36-11': '诸葛亮居画面左执扇抬手，刘备在画面右闻言动容，两人隔矮案斜对，距离一臂。',
 'E36-12': '诸葛亮居画面左执扇动容，刘备在画面右谦逊低语，两人隔矮案对视，间距一臂。',
 'E36-13': '诸葛亮居画面左执扇，面向画面右的刘备，隔矮案相谈，间距一臂。',
 'E36-14': '刘备居画面右离座整冠，向画面左的诸葛亮深拜而下，两人纵向拉开约一步，诸葛亮坐席未动。',
 'E36-15': '诸葛亮居画面左，刘备在画面右躬身相请，两人近距离对峙一臂；门外关羽张飞立于廊下画面右侧屏息旁观。',
 'E36-16': '诸葛亮居画面左正色相告，刘备在画面右凝神聆听，两人隔矮案相望，间距一臂。',
}
# ---- ep37 blocking ----
B37 = {
 'E37-01': '草庐柴扉大开，诸葛亮跨出门槛立于画面左，刘备在门外画面右整冠长揖，两人隔门槛一步相望。',
 'E37-02': '诸葛亮居高临下立于画面左，刘备在画面右仰面应声，两人相距三步，光线从庐内泻出。',
 'E37-03': '诸葛亮于草庐门前画面左回望，关羽到画面右抱拳相许，张飞在其旁咧嘴，三人呈扇形立于门前台阶下，彼此相距一臂半。',
 'E37-04': '张飞在画面右咧嘴请战，诸葛亮于画面左执扇应答；随后众人引马沿画面左侧山道下行，两名为首者并肩居前。',
 'E37-05': '诸葛亮居画面左执扇叮嘱，刘备在画面右相伴同行，两人并肩策马相距半臂；关羽一骑随后于画面右。',
 'E37-06': '大远景，新野城楼居中，旗帜在城头翻卷，入城队列自画面右沿官道行进，守军于城上右向远眺。',
 'E37-07': '大帐内，刘备居画面右双手托兵符，诸葛亮于画面左双手接过，两人隔案面对面，相距一臂。',
 'E37-08': '张飞于画面右侧立发问，诸葛亮在画面左执扇抬眼望向北方，二人相距两步；关羽在画面右后方静立。',
 'E37-09': '帐内众人围于画面中偏左，关羽于画面右拱手应答，诸葛亮与刘备在画面左侧对坐，众人面朝军师。',
 'E37-10': '诸葛亮居画面左俯身展开舆图，指尖点在图右的博望；关羽在画面右抱拳称许，两人隔案相望。',
 'E37-11': '红脸武将与虬髯大汉自画面右退向帐口，刘备与诸葛亮留于画面左灯下对坐细谈，帐帘在画面右垂落。',
 'E37-12': '曹操坐于画面右案后，将探报掷在案上；随后起身负手于画面中踱步，烛影在画面左侧朱红柱上拖动影子。',
 'E37-13': '曹操居画面中停步，负手而立，面朝画面左侧前方舆图，独身一人，烛光在身后投下长影。',
 'E37-14': '曹操俯身于画面左舆图前，指尖落在图上的新野；随后站定于画面中偏左，面朝画面右前方。',
 'E37-15': '曹操居画面中偏左，沉声传令，面朝画面右前方；随后负手转身，背对画面右，身后烛影拉长。',
 'E37-16': '特写俯角，案上宣纸居中，曹操执笔于画面右下/左下落写军令，烛灯悬于一侧。',
}
# ---- ep38 blocking（长坂坡·博望战场） ----
B38 = {
 'E38-01': '大远景，夏侯惇所部曹军自画面右沿黄土官道压来，诸葛亮立于高地处画面左，张飞在其侧，两者隔整片战场遥相呼应。',
 'E38-02': '夏侯惇居中偏右策马立定，面朝画面左逃敌方向喝令追击，身后是鱼贯涌入谷道画面的骑兵。',
 'E38-03': '关羽于画面右坡上抱拳请战，面朝画面左下方谷口；诸葛亮在画面左坡上执扇沉声，两人相距数步同望下方。',
 'E38-04': '诸葛亮在画面左上方风处将旗一展，火把于其后齐落；大远景转向画面中谷口腾空的烈焰与逃散的人马。',
 'E38-05': '夏侯惇居中偏右正面惊觉，身后火墙在画面左侧腾起；随即自画面右向画面左沿坡奔逃，征衣带火。',
 'E38-06': '张飞在画面右坡上咧嘴大笑，望向画面左下方火场；关羽于画面左坡上抱拳赞许，二人相距数步。',
 'E38-07': '刘备在画面右坡上转头望向画面左侧军师，相隔半臂，火光的暖色自画面左下方涌上。',
 'E38-08': '诸葛亮居中偏左收扇执戈，面朝画面右远处退兵的烟尘；刘备随立于画面右侧并肩远望。',
 'E38-09': '刘备在画面右凝望远处烟尘道破隐忧，诸葛亮于画面左执扇轻笑，二人隔半臂并肩。',
 'E38-10': '大远景，夏侯惇残部自画面右扑向城下，诸葛亮在城头画面左上回身传令，两者隔整片护城视野。',
 'E38-11': '刘备在画面右神色一紧追问，诸葛亮于画面左沉稳应答，二人相对一臂；随后城下街市大远景将火光推向画面。',
 'E38-12': '夏侯惇居中瞪眼惊喝，身侧前后火墙包夹；随即自画面右向画面左夺路奔逃于燃烧的街市。',
 'E38-13': '夏侯惇居中勒马咬牙低喝，面朝画面左火海；诸葛亮在画面上方高处暗影中收扇，张飞于画面右坡上大笑。',
 'E38-14': '刘备在画面右高处望着渐熄的火光，随后低声道出隐忧；诸葛亮于画面左执扇凝练应答，二人相距一臂。',
 'E38-15': '关羽居画面右握刀发问，诸葛亮于画面左俯视舆图以扇轻点，指尖落在画图上的新野。',
 'E38-16': '张飞在画面右坡上瞪眼不忿，刘备于画面中按张飞臂膀，诸葛亮在画面左并肩而立，三人位于城头残烧处。',
 'E38-17': '刘备在画面右凝望北方压低声音，诸葛亮于画面左执扇近前作答，二人相距半臂并肩；末镜大远景收束为画面中央的血色残阳。',
}
# ---- ep39 scene1 blocking（荆州夜雨·府衙，围案议事） ----
B39s1 = {
 'E39-01': '大远景，驿马自画面右冲入府衙前庭，溅起泥水；随后镜头切近，刘备自画面右伸手接过急信，就着烛光展开。',
 'E39-02': '刘备居画面右低哑念信，张飞在画面后左猛地拍案，两人隔案相对，相距一臂多。',
 'E39-03': '关羽居画面中偏右蹙眉按刀，面朝画面左侧兄长；烛影斜落在墙角，四周众人后撤留出中心。',
 'E39-04': '诸葛亮于画面左执扇立案侧，刘备在画面右蹙眉发问，众人围案而立，诸葛亮与刘备隔案一臂。',
 'E39-05': '诸葛亮居画面中偏左执扇接口，以扇指向画面左下方西南，独白主导，身前景案横陈。',
 'E39-06': '张飞在画面右攥拳发问，诸葛亮于画面左转向安抚，两人隔案相对一臂。',
 'E39-07': '关羽在画面右低声附和，刘备于画面左强自镇定决断，两人隔案相望，距离一臂。',
 'E39-08': '张飞居中还想再争，关羽于画面右伸手按住其臂膀；刘备在画面左闭目复睁，三人围案而立。',
 'E39-09': '关羽居画面右掷地有声，诸葛亮于画面左上前一步进言，两者隔案一臂，众人后撤。',
 'E39-10': '刘备在画面右沉吟追问，诸葛亮于画面左颔首应答，两人隔案相对一臂。',
 'E39-11': '张飞在画面右赌气别过脸，关羽于画面左温声宽慰，二人隔案半臂对坐。',
 'E39-12': '四人心照不宣于烛火下围案对视（刘备、诸葛亮居左，关羽、张飞居右），间距一臂；随后大远景切向雨幕城头，队伍蜿蜒而去。',
}

# ============================================================
# 3) 应用 blocking。soundscape/music 中文从 h3 内嵌英文逐段译出，
#    存在 per-seg dict，缺省回退到段内已有的英文（直接隐含）。
#    这里直接为每个成品段提供中文 soundscape+music。
# ============================================================

# 提供：中文音景 + 中文配乐（ep36）
SD36 = {
 'E36-01': '晨雾弥漫低矮山丘，竹篱柴扉嘎吱开启，一阵轻缓的脚步踏过草庐前洒扫过的石阶。',
 'E36-02': '竹席在两人落座时轻响，茶汤热气袅袅升起，羽扇拂动的簌簌声混在草堂清晨的静谧里。',
 'E36-03': '茶水滑入白瓷盏的轻响，草席微微作响，林间鸟鸣随谷中薄雾隐约传来。',
 'E36-04': '羽扇随话语摆动时簌簌作响，案上茶气渐凉，草堂一片静谧，只余说话人沉稳的语调。',
 'E36-05': '袍袖拂过草席的轻响，羽扇摆动之声，话语落定后草堂又回到低低的嗡鸣里。',
 'E36-06': '草席随人挪动轻响，羽扇缓缓拂动，两道声音之间一片清晨的静谧。',
 'E36-07': '羽扇掠过空气之声，门外偶有鸟鸣传入，草堂归于一片近乎静止的安静。',
 'E36-08': '袍服随起身舒展的窸窣声，晨茶轻冒热气，门外一缕风摇动竹叶。',
 'E36-09': '门外粗豪的一声笑随即敛去，袍服窸窣，两名武者退回门后，草堂复归安静的寂静。',
 'E36-10': '羽扇保持轻柔的节律，袍服随人倾身窸窣，话语间隙里一片清晨的安静。',
 'E36-11': '说话人的语调微顿，草席随挪动轻响，四周一片草堂晨间的安顿。',
 'E36-12': '一声啜饮与茶盏落案的轻叩，羽扇短暂停住，草堂在静谧中呼吸。',
 'E36-13': '袍服随军师坐正窸窣，羽扇在空中顿住，午后斜光静静地铺过草堂。',
 'E36-14': '袍服随人起身深深一拜而窸窣，说话人的语气恳切，草堂保持着一片肃静。',
 'E36-15': '羽扇悬空停顿，门外的两道身影屏息静立，草堂在近乎无声中等候。',
 'E36-16': '一句话说到半截悬在静谧里，羽扇停在半空微晃，草堂屏息等候。',
}
MU36 = {
 'E36-01': '低沉温润的弦乐，速度缓慢。', 'E36-02': '缓慢低沉弦乐，句间夹一声轻拨。',
 'E36-03': '疏疏温润弦乐，缓缓上扬，速度缓慢。', 'E36-04': '低沉着意弦乐，一句长弓音压在话下，速度缓慢。',
 'E36-05': '缓慢上扬的弦乐，渐生温情。', 'E36-06': '持续低沉弦乐，缓慢而均匀，全曲轻微平稳。',
 'E36-07': '稀疏低沉弦乐，渐趋几近静止的气息。', 'E36-08': '温润弦乐轻轻涌起，速度缓慢。',
 'E36-09': '低沉弦乐持续随后渐疏，速度缓慢。', 'E36-10': '缓慢而平稳悠然的低音弦乐。',
 'E36-11': '温润弦乐轻轻涌起，速度缓慢。', 'E36-12': '低音弦乐间夹一次清拨，速度缓慢。',
 'E36-13': '低音弦乐带着沉静的决意涌起，速度缓慢。', 'E36-14': '缓慢温润弦乐，拜下时一记坚定强音。',
 'E36-15': '低沉克制的弦乐，起伏一次复又放松，速度缓慢。', 'E36-16': '低音弦乐戛然归于近乎无声，一记长音悬住，缓慢而期待。',
}
# ep37
SD37 = {  # 用已内嵌的英文意译
 'E37-01': '竹篱门完全敞开时一声嘎吱，晨雾里袍服窸窣，山间传来隐约鸟鸣。',
 'E37-02': '晨雾在草庐周围流转，手中的书卷轻轻作响，山间一片安顿的静谧。',
 'E37-03': '袍袖随施礼扬起的声音，竹篱门一声轻响，山间淡淡的雾气低低地嗡鸣。',
 'E37-04': '马蹄与脚步沿山间石径一路下行，松林里雾气簌簌，开阔的空气中传来低低的话声。',
 'E37-05': '马蹄踏出匀稳的节律，鞍鞯皮革吱呀，低低的话声混在掠过的栎树声中。',
 'E37-06': '城头旌旗猎猎作响，马蹄车轮碾过石板入城，城垛上隐约传来守军的低语。',
 'E37-07': '木符与印绶交到手中时轻轻一响，袍服窸窣，帐外隐约有营帐生活的嘈杂。',
 'E37-08': '羽扇拂动，帐帘被气流掀起，紧张地静谧中涌起一片低语。',
 'E37-09': '拳头握上兵刃时刀鞘轻响，帐帘微动，摇曳灯影下沉着一片沉甸甸的静默。',
 'E37-10': '舆图纸张被展平时沙沙轻响，羽扇拂动，摇曳的灯光低低地铺满帳内。',
 'E37-11': '两人起身时腰刀轻磕一响，帐帘刷拉合拢，灯下又涌起低低的议事声。',
 'E37-12': '探报拍落案上的一声闷响，脚步声在扫净的石板上回响，铜灯火焰在气流里低低晃动。',
 'E37-13': '脚步声停住，袍服随人站定而垂落，铜灯焰在厅堂气流里微微作响。',
 'E37-14': '指尖在舆图上重重一敲，烛焰一抖，厅堂内一片冷峻的安静。',
 'E37-15': '袍服随转身窸窣，脚步踏过烛光映照的石板，灯盏低低晃动。',
 'E37-16': '笔毫在纸上蹭过一道道拖行的沙沙声，印泥在印盒里轻响，厅内静室中的铜灯火焰轻响。',
}
MU37 = {
 'E37-01': '温润低音弦乐缓缓上扬，速度缓慢。', 'E37-02': '低音弦乐带着温润的决意，速度缓慢。',
 'E37-03': '稀疏温润弦乐，速度缓慢，施礼时一声涌起的强音。', 'E37-04': '轻快的上扬弦乐，中慢速，明快而带着期许。',
 'E37-05': '温润弦乐，从容缓慢，轻快而稳定。', 'E37-06': '明亮上扬弦乐，中速，开阔而提升。',
 'E37-07': '低沉着意弦乐，速度缓慢，肃穆而稳重。', 'E37-08': '渐渐拉开的低沉弦乐，略带紧绷，速度缓慢。',
 'E37-09': '低沉肃穆弦乐，速度缓慢，渐增决意。', 'E37-10': '低沉稳健的弦乐，中慢速，透着谋划。',
 'E37-11': '低音弦乐回到思索般的缓慢曲调。', 'E37-12': '低沉阴冷弦乐，速度缓慢，透着谋划。',
 'E37-13': '低冷而有力的弦乐，缓慢。', 'E37-14': '带一道尖锐冷锋的低音弦乐，速度缓慢。',
 'E37-15': '低冷弦乐，缓慢而透出威胁。', 'E37-16': '一声持久压低的长弓弦调，缓慢而宿命感十足。',
}
# ep38
SD38 = {  # 分近平直的战场声，略译
 'E38-01': '马蹄在干硬的官道上隆隆踏地，风声掠过拨马回身的骑兵，尘土在空气里呛咽。',
 'E38-02': '狭谷里马蹄挤涌，两侧枯草沙沙作响，号角在尘土里吹出细长尖音。',
 'E38-03': '风把远处隆隆的马蹄声送上坡来，上空旗帜翻卷，草线里弓手悄无声息地掩身。',
 'E38-04': '火舌呼地舔上枯草，木料爆裂噼啪、嘶鸣的马蹄与人在烟火里冲撞成一团。',
 'E38-05': '身后烈焰轰鸣，蹄子打在燃烧的坡面上打滑四散，烧焦的征衣噼啪作响落下火星。',
 'E38-06': '谷底火势噼啪燃起又轰鸣，风扬起旗帜，两道粗豪的声音在坡上暖热的嗡鸣里回响。',
 'E38-07': '风与火从谷底传来噼啪声，袍服随人转身轻动，坡上一瞬怔然的惊叹。',
 'E38-08': '风扬旗帜，远处蹄声散进烟里，坡上坠入一片警戒的安静。',
 'E38-09': '谷底火势低声噼啪，风扯动袍角，两道身影之间悬着一股沉着的信心。',
 'E38-10': '战号在回返的队列上低低吹响，马蹄与松脱的金属在城下乱响，风扯住旗帜。',
 'E38-11': '城门轰然闭阖上闩，火油泼在石上，随后街巷轰地窜起并噼啪燃成一片。',
 'E38-12': '两侧火墙轰轰作响，马蹄踏过燃烧的断木噼啪乱响，主帅的声音被烈焰吞没。',
 'E38-13': '火势渐低的噼啪声，风搅动烟雾，主帅嘶哑的咒骂悬在渐冷的空气里。',
 'E38-14': '下方余烬轻轻噼啪，风拂过袍角，两道低低的话声权衡着这场的代价。',
 'E38-15': '腰刀在掌中微动，舆图纸在扇尖下沙沙轻响，被围城外的低语在四周沉降。',
 'E38-16': '焦黑城墙上零落的余焰嘶嘶熄灭，风送来淡淡的烟味，溃军嘈杂远去。',
 'E38-17': '焦黑城墙上零落的余焰嘶嘶熄灭，风送来淡淡的烟味，溃军嘈杂远去。',
}
MU38 = {
 'E38-01': '低沉急促的弦乐，中速积聚，越拧越紧。', 'E38-02': '低沉紧绷的弦乐，中速，随队列入谷而收紧。',
 'E38-03': '低沉长音弦乐，盘旋而隐忍，中慢速。', 'E38-04': '鼓点与低音铜管驱动，凶狠而急促。',
 'E38-05': '低音铜管与鼓急促混乱，随溃逃渐散。', 'E38-06': '明亮的低音弦乐与铜管，中速，透着胜意。',
 'E38-07': '低沉温煦弦乐，缓慢地涌起。', 'E38-08': '低沉克制的弦乐，缓慢而警觉。',
 'E38-09': '低音弦乐不经意间趋于静止，速度缓慢。', 'E38-10': '低音弦乐盘旋而冷，中慢速。',
 'E38-11': '鼓与低音铜管上扬，急促凶锐，随后热浪抬升。', 'E38-12': '低音铜管与鼓翻搅混乱，快速。',
 'E38-13': '低鼓渐稳成沉着的脉冲，中速。', 'E38-14': '低沉警觉的弦乐，向内转，速度缓慢。',
 'E38-15': '低音弦乐沉着而图谋，速度缓慢。', 'E38-16': '低音弦乐带着肃穆决然的脉冲，缓慢，沉稳而坚定。',
 'E38-17': '低音弦乐带着肃穆决然的脉冲，缓慢，沉稳而坚定。',
}
# ep39 scene1（荆益夜雨·府衙）
SD39s1 = {i: '雨点噼啪敲打府衙檐瓦，一匹驿马冲到门前骤然驻足，颤抖的手掌搓动纸张，低语传来荆州沦陷的消息。' for i in range(1, 13)}
MU39s1 = {i: '低沉而焦灼的弦乐，带一道警惕的暗涌，速度缓慢，读完信时渐涨。' for i in range(1, 13)}

# ------------------------------------------------------------
# 4) 应用 blocking + soundscape + music
# ------------------------------------------------------------
SD = {**{f'E36-{i:02d}': SD36[f'E36-{i:02d}'] for i in range(1, 17)},
      **{f'E37-{i:02d}': SD37[f'E37-{i:02d}'] for i in range(1, 17)},
      **{f'E38-{i:02d}': SD38[f'E38-{i:02d}'] for i in range(1, 18)},
      **{f'E39-{i:02d}': SD39s1[i] for i in range(1, 13)}}
MU = {**{f'E36-{i:02d}': MU36[f'E36-{i:02d}'] for i in range(1, 17)},
      **{f'E37-{i:02d}': MU37[f'E37-{i:02d}'] for i in range(1, 17)},
      **{f'E38-{i:02d}': MU38[f'E38-{i:02d}'] for i in range(1, 18)},
      **{f'E39-{i:02d}': MU39s1[i] for i in range(1, 13)}}
B = {**B36, **B37, **B38, **B39s1}


def add_seg_meta(seg):
    sid = seg['id']
    seg['blocking'] = B.get(sid)
    if sid in SD: seg['soundscape'] = SD[sid]
    if sid in MU: seg['music'] = MU[sid]
    # crowd >3 需 note
    for c in seg['cuts']:
        if len(c.get('characters', [])) > 3 and not c.get('note'):
            c['note'] = '同框人数超过三人，分镜图以提示词+参考图拆解各人位置与朝向。'
    return seg


for e in [ep36, ep37, ep38]:
    for seg in e['segments']:
        add_seg_meta(seg)
for seg in ep39s1:
    add_seg_meta(seg)

assert all(s['blocking'] for seg in [ep36, ep37, ep38] for s in seg['segments'])
assert all(s['blocking'] for s in ep39s1)
print('blocking applied:', 16 + 16 + 17 + 12)

# ------------------------------------------------------------
# 5) ep37 时长修复：单切段（无台词的 action 拍）上调秒数
#    E37-06 3→6s, E37-11 3→5s, E37-16 3→5s ⇒ +5s ⇒ 149.5→154.5
# ------------------------------------------------------------
fix = {'E37-06': 6.0, 'E37-11': 5.0, 'E37-16': 5.0}
for seg in ep37['segments']:
    if seg['id'] in fix:
        assert len(seg['cuts']) == 1
        assert seg['cuts'][0]['seconds'] == 3.0
        seg['cuts'][0]['seconds'] = fix[seg['id']]
        # 单切段 h3 用固定句，无需改；但 [Shot 1] 行仍有效
ep37_total = round(sum(c['seconds'] for s in ep37['segments'] for c in s['cuts']), 1)
print('ep37 total now', ep37_total)


def ep_total(segments):
    return round(sum(c['seconds'] for s in segments for c in s['cuts']), 1)


# ------------------------------------------------------------
# 6) 新作 ep39 scene2（襄阳晴日，18 拍）⇒ ep39 [153,207]
# ------------------------------------------------------------
print('ep39 scene1 total', ep_total(ep39s1))

# 构建器闭包
def seglist(epno, scene_idx, groups, overall, music, start=1):
    segs = []
    for i, sp in enumerate(groups):
        n = start + i
        total = round(sum(c['sec'] for c in sp), 1)
        assert total <= 15, f'E{epno}-{n:02d} {total}s>15'
        segs.append(H.seg_from_specs(f'E{epno}-{n:02d}', scene_idx, sp, epno, overall, music, script))
    return segs


def C(beats, sec, size, cam, chars, frame, shot, h3, cpos=None, comp=None, eye=None, foc=None,
      st='stable', props=[], lens=None):
    d = dict(beats=beats, sec=sec, size=size, camera=cam, chars=chars, props=props, frame=frame,
             shot=shot, h3=h3, lens=lens)
    styl = {
      'wide':('35mm 广角，中等景深','+ 平视远眺','引导线构图','远景','锁定主体'),
      'medium':('50mm 标准，中浅景深','+ 平视正面','三分法','对前方','锁定主体'),
      'close':('85mm 长焦，浅景深','+ 平视正面','中心构图','对前方','锁定面部'),
      'extreme-wide':('24mm 广角，深景深','+ 平视远眺','三分法','远景','锁定剪影'),
    }
    d['lens'] = lens or styl[size][0]
    d['cpos'] = cpos or (chars[0] if chars else '画面') + ' ' + styl[size][1]
    d['comp'] = comp or styl[size][2]
    d['eye'] = eye or styl[size][3]
    d['foc'] = foc or styl[size][4]
    d['stability'] = st
    return d


# ---- ep39 scene2 blocking ----
B39s2 = {
 1: '大远景，襄阳城门居中敞开，曹字大旗自画面右城头缓缓升起，宋降旗垂落；城外残军沿画面右侧官道朝画面左的江夏方向行进。',
 2: '刘备居画面右策马回望，张飞、诸葛亮、关羽随行其后成一线；襄阳城头曹字旗在画面左扬起，队伍与城头相距数丈。',
 3: '老卒在画面右回望襄阳，红着眼向刘备背影扬拳；刘备在画面左策马前行，二者相距一仗。',
 4: '刘备居画面右，诸葛亮于画面左并行，关羽张飞在队伍中后侧；四人一路向画面左江夏方向缓行，彼此距离一二步。',
 5: '四人于官道并肩，刘备居画面右，诸葛亮于画面左执扇，关羽张飞分列身侧；队伍沿画面右侧一路南去。',
 6: '大远景，襄阳城头曹字大旗在画面中翻卷，为收束空镜；队伍已在画面下方远去。',
}
SD39s2 = [
 '城头传来沉重的门轴转动之声，一面大旗缓缓换下又升起，官道上马蹄与脚步杂沓着向画面外行进。',
 '官道上马蹄踏出坚定的节奏，队伍里传来低低的交谈，襄阳城头的旗角在风里猎猎作响。',
 '队伍里一名老兵哽咽着攥紧拳头，四周百姓议论声低低，马蹄声不断向画面外延伸。',
 '说话之间马蹄与脚步不止，队列里的交谈声混在风中，四道身影并肩而行。',
 '官道上马蹄与脚步从容不止，队伍里传来笃定的应和之声，风声卷起衣角。',
 '大旗在风中猎猎作响，渐远的蹄声与脚步在旷野里散开，襄阳城逐渐沉入画面一侧。',
]
MU39s2 = [
 '低沉弦乐在水流般的节奏里铺开，异常明朗，中速偏缓。',
 '不疾不徐的弦乐，透着沉静与坚毅，速度缓慢地稳步行进。',
 '稍显低沉而重的情弦乐，渲染回望的凝重，速度缓慢。',
 '稳而不急的弦乐，带一丝从容的暖意，中慢速。',
 '明净而沉着的弦乐，缓缓推进，透着笃定的前行感。',
 '低音弦乐放缓收束，透出守望天边的余韵，速度缓慢。',
]
# ============================================================
# 6b) 组装 ep39 scene2（襄阳晴日，18拍）段
# ============================================================
osa39s2 = 'Exchange of war-drums and distant rumble fill the air; the flag heaves as the column passes, and the rustle of marching feet and low voices drift over the road.'
mus39s2 = 'Low, steady strings at a slow marching tempo, grave yet resolute.'

G39s2 = [
 # beats [1,3] 城门降旗 / 残军南行 / 刘备回望
 [C([1,2],5.5,'wide','Tracking Shot',[], 
    '全景，晨光里襄阳城门洞开，一面曹字大旗缓缓升起，降旗垂落，城外官道上一支残军且行且停往南而去，尘土在光里轻扬。',
    '镜头平稳跟随，城门洞开处一面大旗升起又落，官道上迤逦一支队列沿路南行，晨光铺满城墙与旗角。',
    'a tracking shot follows the wide view of the fallen banner replaced by a new one over the open gate as a weary column files south along the road in the clear morning light'),
   C([3,3],6,'medium','Static Shot',['C01'],
    '中景，刘备在队列前回身回望，目光落在襄阳城头那面崭新的曹字旗上，旗角在晨光里翻卷，眉宇间浮起一层怅然。',
    '固定镜头，软袍贵族于队列前勒马回望古城墙头，眉宇微蹙，目光追着那面翻卷的新旗，神色怅然。',
    'the nobleman in a soft robe halts and looks back toward the distant city wall, his gaze resting on the new banner snapping in the light as a quiet melancholy passes over his face')],
 # beats [4,5,6]
 [C([4,4],5,'close','Static Shot',['C02'],
   '特写，关羽在马上回望城头，低声叹道大哥荆州易主咱们终又是无根之萍了，胡须在晨风里轻动。',
   '固定特写，红脸长髯武将勒马回望城墙，低声吐露无根之叹，神色沉郁。',
   'the tall brocade-garbed warrior turns in the saddle toward the wall and, with a subdued, sorrowful voice (S1) he grieves'),
   C([5,5],4,'medium','Static Shot',[],
    '中景，队伍一侧一名老兵红着眼回望襄阳，向刘备的背影扬了扬拳，车杖与百姓在一旁缓缓前行。',
    '固定镜头，队伍边缘一名老兵驻足回望古城，缓缓朝前行者的背影扬了扬拳头，又垂头跟上队列。',
    'an old soldier at the edge of the column looks back at the town, red-eyed, raising a fist toward the figure ahead before ducking back into the slow-moving files'),
   C([6,6],5,'close','Static Shot',['C01'],
    '特写，刘备回转身形肃然道留得青山在来日方长兄弟同心终有再起之时，目光沉定望向前路。',
    '固定特写，软袍贵族转回身形沉声应答，目光坚毅地望向队伍前方，语气恳切而笃定。',
    'the soft-robed nobleman turns back to face the road and, with a firm, steadfast voice (S1) he reassures')],
 # beats [7,8,9]
 [C([7,7],5.5,'medium','Static Shot',['C05'],
   '中景，诸葛亮执扇在侧接口道皇叔此言大善兵败而志不坠正是他日成事的根基，神色笃定。',
   '固定镜头，鹤氅青年执扇于侧接口，语气郑重地称许这份不坠之志，目光清亮。',
   'the young strategist in the crane-cloak joins in, and with a grave, assured voice (S1) he affirms'),
   C([8,8],4,'medium','Static Shot',['C03'],
    '中景，张飞策马昂然接道对让曹操赢了器咱们赢的是人心，扬眉朗笑，虬髯颤动。',
    '固定镜头，虬髯大汉策马扬声应和，语气粗亮里带着一股毫无犹疑的笃定。',
    'the burly bearded general on horseback answers boldly, and with a loud, hearty voice (S1) he declares'),
   C([9,9],5,'wide','Static Shot',[],
    '全景，队伍旁百姓闻声纷纷望向这位仁厚的刘皇叔，不少人红了眼眶，晨光斜照在众人脸上。',
    '固定远镜，官道旁许多百姓停下脚步望向前方那位策马之人，眼里浮起泪光，静静目送。',
    'a wide view of the civilians along the road softening into red-eyed gratitude as they watch the mounted lord, light falling across their faces')],
 # beats [10,11,12]
 [C([10,10],5,'wide','Tracking Shot',['C01'],
   '全景，刘备回过身策马向前，身后大军缓缓往南面江夏行去，衣袍与旗帜在晨光里翻动。',
   '镜头平稳跟随，软袍贵族提缰催马向前，阵列随之缓缓朝南移动，队伍在官道上延展开来。',
   'the nobleman spurs his horse forward and the great column begins to move south, a tracking shot pacing the march'),
   C([11,11],4.5,'close','Static Shot',['C02'],
    '特写，关羽随行低声道大哥前路虽险好在军师与咱们都在一处，目光温和地看向兄长。',
    '固定特写，红脸长髯武将策马并肩低声宽慰，语气沉稳而带着几分暖意。',
    'the tall warrior rides beside his lord and, with a low, firm voice (S1) he reassures'),
   C([12,12],4.5,'close','Static Shot',['C01'],
    '特写，刘备应道军民同心便是再大的风浪也走得过去，眉间渐舒，目光透着坚定。',
    '固定特写，软袍贵族策马回应，语气沉稳笃定，眉宇之间那份愁色渐渐化开。',
    'the nobleman answers and, with a calm, steady voice (S1) he declares his resolve')],
 # beats [13,14,15]
 [C([13,13],5,'medium','Static Shot',['C03'],
   '中景，张飞昂声接道哥哥放心有我飞和二哥在谁也别想把咱拆散，拍马挺矛，咧嘴而笑。',
   '固定镜头，虬髯大汉拍马朗声许诺，语气里是毫无遮拦的豪义。',
   'the burly general rides close and, with a bluff, resolute voice (S1) he pledges'),
   C([14,14],4,'close','Static Shot',['C01'],
    '特写，刘备听了这话回身望一眼二位兄弟，心头一热，眼眶微潮，晨光在侧脸流动。',
    '固定特写，软袍贵族回头望一眼两位随行的兄弟，鼻尖一酸，目光里涌起一片暖意。',
    'a close view of the nobleman turning to glance at his two companions, emotion welling in his eyes under the morning light'),
   C([15,15],5,'close','Static Shot',['C02'],
    '特写，关羽温声接道家业虽失兄弟义在何愁天下不得一隅，长髯轻动，神色沉稳。',
    '固定特写，红脸长髯武将低声宽慰，语气里带着一股笃定的兄弟义气。',
    'the tall warrior adds quietly and, with a warm, resolute voice (S1) he consoles')],
 # beats [16,17,18]
 [C([16,16],5,'wide','Static Shot',[],
   '全景，身后襄阳城头那面崭新的曹字帅旗仍在风中猎猎作响，晨光将旗帜与城楼染上金边。',
   '固定远镜，襄阳城头那面大旗在风里翻卷，城楼与旗帜逆着晨光而立，成为队列远去后的背景。',
   'a wide moonlight view of the town walls with the new banner snapping in the morning wind, the column dwindling in the distance'),
   C([17,17],4.5,'close','Static Shot',['C01'],
    '特写，刘备低声断言曹操得荆州未必是荆州之福日后自有分晓，目光深长望向远处。',
    '固定特写，软袍贵族望着远去的城头，低声笃定地说出这句判断，眼神犀利而深远。',
    'the nobleman murmurs and, with a low, far-seeing voice (S1) he prognosticates'),
   C([18,18],5,'close','Static Shot',['C05'],
    '特写，诸葛亮在侧颔首道皇叔所言正是天理常存之处容他一时争之长久，执扇予人沉定之感。',
    '固定特写，鹤氅青年执扇颔首，语气平和而笃定，把这一段收束在从容之中。',
    'the young strategist nods beside him and, with a calm, settles the thought with a measured voice (S1)')],
]
segs39s2 = seglist(39, 2, G39s2, osa39s2, mus39s2)
for idx, seg in enumerate(segs39s2):
    seg['blocking'] = B39s2[idx + 1]
    seg['soundscape'] = SD39s2[idx]
    seg['music'] = MU39s2[idx]
for s in ep39s1:
    pass
ep39_segs_all = ep39s1 + segs39s2
print('ep39 total', ep_total(ep39_segs_all))

# ============================================================
# 7) 新作 ep40（scene1=19拍、scene2=24拍，长坂坡）
# ============================================================
BL40s1 = {
 1:'大远景，当阳道阴云低垂，百姓拖老携幼沿泥泞官道自画面右向南行，刘备骑马居画面左最前，赵云单骑在画面右上侧赶至报信，哭声与车辙绵延至画面外。',
 2:'张飞、关羽在画面右一前一后扬声进言，刘备居画面左策马沉声应命，三人与浩荡的百姓队之间隔开一片泥泞。',
 3:'刘备居中下马，向画面右侧路旁的老人俯身搀扶，老人位于身侧半步；随后百姓在画面侧被深深打动，垂首抹泪。',
 4:'赵云在画面右上侧急声进言，诸葛亮于画面左执扇沉吟，两人隔空一臂半相商，刘备的身影隐于其间。',
 5:'刘备居中重新上马整袍，随后端坐马上正色宣言，身后浩荡的百姓队伍铺展向画面外。',
 6:'关羽、张飞、赵云三骑于画面右环护居中的刘备南行，阵列在泥泞中缓慢向前。',
 7:'刘备居中下马，向画面右侧抱着孩子的农妇俯身相扶，雨丝斜落，农妇位于身侧半步。',
 8:'农妇含泪叩首后背着孩童并入画面右侧人流，诸葛亮于画面左执扇旁观，微微颔首。',
}
SD40s1 = [
 '当阳道阴云低垂，数十万百姓拖老携幼在泥泞里艰难前行，车辙吱呀、哭声阵阵，马蹄深陷又拔出。',
 '马蹄在泥泞里踏出沉重的节拍，远处传来百姓的哭声，风声在道上来回掠过。',
 '马蹄深陷泥泞之声，一名老人跌倒又被人扶起的响动，四周百姓低声议论纷纷。',
 '说话声中夹杂着马蹄与脚步，队伍里的哭声、车辙声不绝于耳。',
 '马蹄在泥泞中踩出扑扑之声，百姓队伍嘈杂交织，风声掠过衣袍。',
 '四骑马蹄依次践踏泥泞，队伍里的哭声与车辙声混成低沉的潮水。',
 '马蹄顿停于泥泞，一名农妇慌忙扶住怀中孩童，人群中一阵低低的骚动。',
 '马蹄与脚步杂沓，队伍尾部农妇抱着孩童匆匆跟上，人群中母亲的啜泣渐渐远去。',
]
MU40s1 = [
 '低沉阴郁的弦乐，缓慢地在泥泞般的节拍里推进。',
 '低音弦乐切着沉重行进的节奏，透着不易察觉的紧迫。',
 '低沉弦乐放缓一瞬，随即复归严整的行进节律。',
 '弦乐低沉而克制的推进，带上一丝忧色。',
 '低音弦乐平缓行进，渗入一股决意与沉重。',
 '沉闷的行进节拍叠加低沉弦乐，透着紧张。',
 '弦乐骤然收紧一瞬，又随着鼓点复归沉重。',
 '低音弦乐缓缓收拢，拖出一道守望的长节律。',
]
BL40s2 = {
 1:'大远景，天头骤雨里逃难车队在泥泞中混成一片，步卒与百姓聚满画面，一个小孩在画面右哭闹扑倒，怀抱着襁褓的妇人四顾无助。',
 2:'刘备居画面左紧勒缰绳脸色一变回望，赵云在画面右前方勒马报信，两人隔着一片乱军与百姓烟尘相望。',
 3:'刘备居画面左神色焦灼，赵云于画面右策马扬声许下必救少主，两人相距一臂半相望。',
 4:'赵云单骑居画面中偏右，转身折返，一头扎进画面左侧翻涌的烟尘乱民之中，身影随即隐没。',
 5:'关羽在画面右上侧低声进言，诸葛亮于画面左执扇轻摇应声，两人相距一臂；刘备的身影隐于画面中。',
 6:'关羽、张飞左右护住居中的刘备，军民在雨中艰难南行，队伍自画面右向画面左延伸。',
 7:'大远景，坂上烟尘中一骑白袍银枪在乱军里左冲右突，正是赵云，位于画面中；刘备等在远处江岸画面左侧凝望。',
 8:'大远景，江岸已在画面左前方，渡口隔着重重人海；刘备在画面右勒马，赵云于画面中左侧隔江应声。',
 9:'刘备居画面左凝望远处白影，迟迟不肯催马先行；随后画面右侧一辆负重的牛车翻倾，孩童惊哭，人群惊乱。',
 10:'关羽在画面中急切催请，张飞于画面右扬声呼喊，两人面向画面左的刘备同声敦促。',
 11:'刘备居画面中攥紧缰绳、眼眶通红，终于催马转头，一面扬声叮嘱仍留在乱军的赵云。',
 12:'大远景，赵云白袍白影在画面左远处一枪挑开一名曹将回首相望，随后刘备居中催马渡水，身后十万军民紧随，江水粼粼、浊浪翻卷。',
}
SD40s2 = [
 '细雨簌簌落在车队上，泥泞的脚步扑扑作响，小儿哭闹与妇人的惊呼混在嘈杂人群里。',
 '马蹄猛地勒停于泥泞中的一声，远处人海喧哗，雨声混着脚步与哭喊。',
 '马蹄拨泥之声，雨势未歇，两道急促的话声在队伍前端你来我往。',
 '马蹄折返蹬起泥水，烟尘里人马呼喝，一道白色身影一头扎进乱民。',
 '雨声中关羽与诸葛亮的话声一低一稳，马蹄在队伍前端来回挪动。',
 '马蹄与脚步在雨中杂乱，关羽、张飞左右护行，百姓哭喊一路向后延展。',
 '马蹄踢踏、兵器交击之声，烟尘里一杆银枪左右挑刺，远处人声鼎沸。',
 '风声与水声隐隐，渡口人头攒动，一道青年将军的请命之声在江岸前响起。',
 '马蹄迟疑地剁泥，四下孩童惊哭、人群惊乱，牛车翻倾之声轰然传来。',
 '雨声里两道催促之声一处比一处急，马蹄杂沓，远处杀伐渐近。',
 '马蹄在泥泞里乱踏，哭声愈急，刘备勒缰的声响混杂着远去的话音。',
 '马蹄渡水的哗啦声，身后十万军民涉水的浊浪翻卷，江面一片喧嚣。',
]
MU40s2 = [
 '低音弦乐压着雨点般细密的鼓，紧迫而阴沉。',
 '弦乐骤然收紧，一声闷雷般的低音伴随勒马的瞬间。',
 '持续低音弦乐切着细碎鼓点，焦灼而绷紧。',
 '鼓点急躁，弦乐急促上扬，透着乱军冲散的紧急。',
 '低沉弦乐在雨里平稳推进，含着一线不安。',
 '低音弦乐切着纷乱的脚步节拍，沉郁而紧张。',
 '鼓点驱动的弦乐锋利而急促，渲染白袍冲杀的弧光。',
 '弦乐在开阔处放大，透着隔江凝望的凝重与决绝。',
 '弦乐忽慢忽紧，拖着迟疑与焦灼，孩童惊哭时骤紧。',
 '急促的弦乐挟着杂沓的鼓点，紧张再度抬升。',
 '低音弦乐跟着勒马与转身几近停滞，复又沉重地起步。',
 '宽广低沉弦乐压阵，随浊浪推进而缓缓收束。',
]
assert len(BL40s1) == 8 and len(SD40s1) == 8 and len(MU40s1) == 8
assert len(BL40s2) == 12 and len(SD40s2) == 12 and len(MU40s2) == 12

# ---- ep40 scene1（19拍）----
osa40s1 = 'Low heavy skies press the mud-filled road; countless refugees trudge south with carts and wagons, horses slogging through mud, wailing and crying rising in the damp air.'
mus40s1 = 'Low, sombre strings at a slow, treading pace, weighed and tense.'

G40s1 = [
 # [1,2,3] 天阴 百姓南行 / 刘备骑马 / 赵云报信
 [C([1,2],6,'extreme-wide','Static Shot',[],
   '大远景，当阳道上阴云低垂，数十万百姓拖老携幼在泥泞里艰难南行，哭声与车辙一路绵延到天边。',
   '固定远镜，灰蒙蒙天幕下一条泥泞官道铺开，迤逦的人流与车仗一路向画面前方延伸，哭声与车辙隐约。',
   'an extreme wide static shot of the long refugee column crawling south under heavy dark clouds, wailing faint and the wheel-rut road stretching to the horizon'),
   C([3,3],3.8,'close','Static Shot',['C11'],
    '特写，赵云单骑赶到画面侧，扬声急报主公曹军铁骑离我军已不过三十里，衣甲沾满泥点，神情焦灼。',
    '固定特写，白马银枪的青年将军策骑赶到，扬高声调急报军情，面上满是焦灼。',
    'a close static shot as the white-robed spearman on his horse reports urgently, and with a tense, urgent voice (S1) he warns')],
 # [4,5,6] 张飞快走 / 关羽劝阻 / 刘备拒绝
 [C([4,4],5,'medium','Static Shot',['C03'],
   '中景，张飞按捺不住扬声道哥哥让百姓自去吧咱们快走保住主力要紧，一手攥着缰绳满脸着急。',
   '固定镜头，虬髯大汉扯着缰绳扬声进言，语气直白而不耐，急着催促撤退。',
   'a medium static shot as the burly bearded general urges haste, and with an impatient, heated voice (S1) he presses'),
   C([5,5],5,'close','Static Shot',['C02'],
    '特写，关羽在侧低声道大哥军民裹挟同行行军太慢恐被追兵赶上，长髯微垂，神色凝重。',
    '固定特写，红脸长髯武将压低声音，一字一句道出行军迟缓之虞，神色沉凝。',
    'a close static shot on the tall warrior voicing the risk of slow marching, and with a low, grave voice (S1) he cautions'),
   C([6,6],5,'close','Static Shot',['C01'],
    '特写，刘备沉声回道百姓愿随我而来患难之中我岂能弃之于先，目光坚定，眉宇里带着不容反驳的仁厚。',
    '固定特写，软袍贵族回身正色作答，目光坚毅，语气里是一股不容商量的仁厚之情。',
    'a close static shot on the nobleman, and with a firm, deep voice (S1) he refuses to abandon the people')],
 # [7,8,9] 下马扶老人 / 安慰 / 老人叩谢
 [C([7,7],4,'medium','Static Shot',['C01'],
   '中景，刘备下马踩着泥走到路旁，将一名跌倒的老人亲手扶起，衣袍下摆沾满泥浆。',
   '固定镜头，软袍贵族翻身下马，蹚过泥地俯身扶起一名倒地的老人，动作温和。',
   'a medium static shot as the nobleman dismounts and wades through the mud to help an old man to his feet'),
   C([8,8],4,'close','Static Shot',['C01'],
    '特写，刘备温声对老人道老人家莫慌刘备带你们一起走，目光微泛泪光，语气恳切。',
    '固定特写，软袍贵族俯身温声宽慰老人，目光柔和而诚恳，语气平稳。',
    'a close static shot on the nobleman speaking kindly to the old man, and with a gentle, reassuring voice (S1) he comforts'),
   C([9,9],3,'wide','Static Shot',[],
    '全景，老人含泪叩谢，周遭百姓见皇叔如此都被深深打动，许多人垂下头抹泪。',
    '固定远镜，老人含泪拜谢，围观百姓纷纷动容垂首，泥泞道上一片低低的啜泣。',
    'a wide static shot as the old man bows tearfully in thanks and the surrounding refugees are moved to tears')],
 # [10,11] 赵云再劝 / 孔明两难
 [C([10,10],5,'close','Static Shot',['C11'],
   '特写，赵云在侧急道主公仁心可再不走曹军追到便是全军覆没，眉间拧紧，声音发急。',
   '固定特写，白马青年将军再进一言，语气急切，毫不掩饰对追兵已近的担忧。',
   'a close static shot as the white-robed spearman pushes forward once more, and with an urgent voice (S1) he insists'),
   C([11,11],5,'close','Static Shot',['C05'],
    '特写，诸葛亮执扇于侧沉吟道皇叔兵贵神速然民心亦不可弃此事两难，羽扇轻摇神色凝练。',
    '固定特写，鹤氅青年执扇沉吟，道出这进退两难的权衡，神色审慎。',
    'a close static shot on the young strategist weighing both sides, and with a measured, pensive voice (S1) he muses')],
 # [12,13] 刘备上马回望 / 宣言
 [C([12,12],4,'medium','Static Shot',['C01'],
   '中景，刘备起身重新上马，目光扫过浩荡疲惫的百姓队伍，衣袍整了整坐直腰身。',
   '固定镜头，软袍贵族重新上马，勒缰挺直腰身，目光缓缓扫过眼前浩荡的难民。',
   'a medium static shot as the nobleman remounts and sweeps his gaze across the weary crowd'),
   C([13,13],6,'close','Static Shot',['C01'],
    '特写，刘备在马上正色道百姓所望便是刘备一生所行之路敌进我亦进退同步，目光坚毅如炬。',
    '固定特写，软袍贵族坐于马上神色坚定，一字一句宣称与民同进之理，目光如炬。',
    'a close static shot on the nobleman, and with a resolute, solemn voice (S1) he declares his way')],
 # [14,15] 云张赵护行 / 关羽表态
 [C([14,14],3,'wide','Static Shot',['C02','C03','C11'],
   '全景，关羽张飞赵云见劝不动，只得左右护住刘备，一同南行，三骑环卫着居中的刘备在泥泞里前行。',
   '固定远镜，三名武将策马分列两侧，将居中的软袍贵族护在阵心，阵列在泥泞中缓慢向前。',
   'a wide static shot as the three generals flank the nobleman and the column together pushes on through the mud'),
   C([15,15],5,'close','Static Shot',['C02'],
    '特写，关羽策马在侧道既已同生共死云长便陪大哥一道走到哪算哪，长髯轻扬，语气沉稳。',
    '固定特写，红脸长髯武将策马相伴，语气沉稳地表明生死相随之心。',
    'a close static shot on the tall warrior riding beside his lord, and with a steady, loyal voice (S1) he vows')],
 # [16,17] 雨急 扶农妇 / 温声安慰
 [C([16,16],4,'medium','Static Shot',['C01'],
   '中景，雨势渐急，一名农妇抱着孩子在泥里踉跄，刘备下马相扶，脚下一滑稳住身形。',
   '固定镜头，软袍贵族于雨中下马，伸手扶住一名抱着孩童踉跄的农妇，动作利落。',
   'a medium static shot as the nobleman dismounts once more in the rain to steady a woman clutching a child'),
   C([17,17],4,'close','Static Shot',['C01'],
    '特写，刘备温声对农妇道莫怕跟着队伍走刘备不会丢下你们，雨水顺着面颊滑落，目光温柔。',
    '固定特写，软袍贵族淋着雨温声安抚，眉目温和，语气让人安下心来。',
    'a close static shot on the nobleman, and with a gentle voice (S1) he reassures her')],
 # [18,19] 农妇叩首入潮 / 孔明赞许
 [C([18,18],3,'wide','Static Shot',[],
   '全景，那农妇含泪叩首，背着孩童重新跟上大潮，消失在人群里，泥泞中一串身影缓缓前行。',
   '固定远镜，农妇含泪拜谢后背着孩子转身奔入人流，身影渐渐被队伍淹没。',
   'a wide static shot as the woman bows tearfully and disappears back into the surging crowd'),
   C([19,19],5,'close','Static Shot',['C05'],
    '特写，诸葛亮在侧望着此景颔首道皇叔仁心百姓愈发死心塌地这是旁人都抢不走的，目光清亮。',
    '固定特写，鹤氅青年在侧望着这幕微微颔首，语气里带着由衷的认可。',
    'a close static shot on the young strategist approving, and with a quiet voice (S1) he observes')],
]
segs40s1 = seglist(40, 1, G40s1, osa40s1, mus40s1)
for idx, seg in enumerate(segs40s1):
    seg['blocking'] = BL40s1[idx + 1]
    seg['soundscape'] = SD40s1[idx]
    seg['music'] = MU40s1[idx]
print('ep40 scene1 segs', len(segs40s1), 'total', ep_total(segs40s1))

# ---- ep40 scene2（24拍，长坂坡·渡江）----
osa40s2 = 'A light drizzle falls on the choked carts, hooves squelch in mud, wails and shouts mingle with the distant clash of arms, then the roar of crossing water.'
mus40s2 = 'Low strings driven by fine urgent drums, tense and grave, then broadening to a resolute crossing.'

G40s2 = [
 # [1,2] 骤雨 车队泥泞 / 小儿扑倒 妇人四顾
 [C([1,1],6,'extreme-wide','Static Shot',[],
   '大远景，天头骤然飘下细雨，逃难的车队陷在泥泞里，步卒与百姓混成一团，车辙与哭声在灰蒙蒙的天幕下铺满画面。',
   '固定远镜，灰暗天幕下泥泞官道上车队与人流混作一团，细雨斜落，队尾拖出一路哭喊与车辙。',
   'an extreme wide static shot of the refugee traffic churning through mud under a drizzling sky, carts and foot-soldiers and civilians crammed together as the column drags on'),
   C([2,2],5,'close','Static Shot',[],
    '特写，人群中一名小孩哭闹着扑倒在泥里，怀抱着襁褓的妇人惊惶四顾，竟寻不到半点依靠，雨珠挂在她的睫毛上。',
    '固定特写，一名孩童在泥泞里扑倒哭闹，一旁抱着襁褓的妇人慌乱四顾，雨珠顺着面颊滚落，孤立无援。',
    'a close static shot as a small child falls crying in the mud while a woman clutching a wrapped infant looks about in panic, rain beading on her face')],
 # [3,4] 赵云报信 / 刘备勒马变色
 [C([3,3],4.5,'close','Static Shot',['C11'],
   '特写，赵云策马赶到，扬声急报主公甘夫人与少主方才在乱军中走散了，白袍沾满泥点，神色焦灼。',
   '固定特写，白袍银枪的青年将军策骑赶到，扬声急报，语气焦灼而着急。',
   'a close static shot on the white-robed young spearman reporting urgently that Lady Gan and the young lord have been lost in the chaos, and with a tense, urgent voice (S1) he warns'),
   C([4,4],5,'medium','Static Shot',['C01'],
    '中景，刘备闻言脸色一变，猛地勒住缰绳，回头朝乱军窜动的方向望去，神色骤然收紧。',
    '固定镜头，软袍贵族勒住缰绳脸色骤变，回头望向乱军纷乱处，眉宇间绷紧。',
    'a medium static shot of the nobleman in soft robes reining in hard at the news, turning abruptly to look back toward the churning crowd')],
 # [5,6] 刘备忧子 / 赵云许下必救
 [C([5,5],4.5,'close','Static Shot',['C01'],
   '特写，刘备急声道阿斗尚在襁褓，如何经得起乱军冲散，声音里的担忧几乎要溢出，目光紧锁着烟尘。',
   '固定特写，软袍贵族压着声音道出对襁褓中幼主的担忧，眉头紧蹙，神色焦急。',
   'a close static shot on the nobleman, and with a strained, worried voice (S1) he frets that his infant son cannot survive the chaos'),
   C([6,6],4.5,'close','Static Shot',['C11'],
    '特写，赵云朗声应道主公放心，常山赵子龙在此，必救少主回来，白袍一振，目光如炬。',
    '固定特写，白袍银枪的青年将军扬声许诺，目光坚定，语气里满是魄力。',
    'a close static shot as the white-robed young spearman swears to recover the young lord, and with a resolute, ringing voice (S1) he pledges')],
 # [7] 赵云单骑折返 扎入乱军
 [C([7,7],6,'wide','Tracking Shot',['C11'],
   '中景，赵云单骑折返，一回身便纵马一头扎进翻涌的烟尘乱民之中，白袍几个起落，身影转眼隐没。',
   '镜头平稳跟随，白袍银枪的青年将军拨马折返，纵骑冲入乱军烟尘，白袍明灭间身影隐没。',
   'a tracking shot following the white-robed young spearman wheeling his horse and charging alone back into the swirling dust and stampede until his figure is swallowed up')],
 # [8,9] 关羽 / 诸葛亮 相劝
 [C([8,8],5.3,'close','Static Shot',['C02'],
   '特写，关羽压低声音道大哥，曹军将至，此地不能久留，先护大军过江要紧，长髯微动，神色凝重。',
   '固定特写，红脸长髯武将压低声音进言，语气沉凝，神色郑重。',
   'a close static shot on the tall red-faced warrior urging that they must first get the main force across the river, and with a low, grave voice (S1) he cautions'),
   C([9,9],4.9,'close','Static Shot',['C05'],
    '特写，诸葛亮执扇接口道皇叔，事有轻重。子龙勇冠三军，自能全身而还，羽扇轻顿，神色笃定。',
    '固定特写，鹤氅青年执扇应声，语气沉稳，替大家宽下心。',
    'a close static shot on the young strategist in the crane-cloak reassuring that the spearman can return safe, and with a steady, calm voice (S1) he settles')],
 # [10,11] 关羽张飞护行 南行 / 张飞信子龙
 [C([10,10],4,'wide','Static Shot',['C01','C02','C03'],
   '全景，关羽张飞闻言只得左右护住刘备，军民在雨中艰难南行，队伍自画面右边一路向左边延伸开去。',
   '固定远镜，红脸长髯武将一身虬髯的大汉分别护在软袍贵族两侧，军民在雨中缓缓向南。',
   'a wide static shot as the two guards flank the nobleman and the crowd presses on southward through the rain'),
   C([11,11],5,'close','Static Shot',['C03'],
    '特写，张飞扬声接道哥哥，你信子龙，我信哥哥。走吧，渡过江再等，虬髯微颤，语气率直。',
    '固定特写，虬髯大汉扬声宽解，语气豪迈笃定，催着继续前行。',
    'a close static shot on the burly bearded general, and with a bold, hearty voice (S1) he declares the plan to cross the river first')],
 # [12,13] 赵云乱军左冲右突 / 刘备万军救骨肉
 [C([12,12],6,'extreme-wide','Arc Shot',['C11'],
   '大远景，坂上烟尘里一骑白袍银枪在乱军里左冲右突，枪影翻飞，正是赵云一路寻救，战圈绕着他在烟尘中起伏。',
   '镜头缓缓环绕，坂上烟尘中一名白袍银枪的年轻将军在乱军里左冲右突，枪影起伏，划开人流。',
   'an extreme wide arc shot circling a lone white-robed spearman darting left and right through the muddle of the enemy host, his silver spear carving through the crowd'),
   C([13,13],6,'close','Static Shot',['C01'],
    '特写，刘备在远处动容道子龙啊子龙，你万军之中救我骨肉，此恩刘备永世不得忘，眼眶微红，声音发颤。',
    '固定特写，软袍贵族望着远处那道身影，声音微颤，一字一句道出至深的感激。',
    'a close static shot on the nobleman watching from afar, and with a choked, moved voice (S1) he vows to remember this debt forever')],
 # [14,15] 江岸现 渡口隔人海 / 赵云请命断后
 [C([14,14],5,'wide','Static Shot',[],
   '大远景，前方江岸已在望，可乱军缠裹，渡口却还隔着重重人海，浊浪与烟尘在画面中分隔开一条对峙的线。',
   '固定远镜，宽阔江面横在画面前方，渡口方向被重重人海与烟尘挡住了去路。',
   'a wide static shot of the far riverbank in sight but the ford still walled off by a sea of people and dust'),
   C([15,15],5.5,'close','Static Shot',['C11'],
    '特写，赵云越众请命道皇叔，先军民过江，末将留断后，定护主公全身而渡，抱拳一礼，目光恳定。',
    '固定特写，白袍银枪的青年将军上前请命断后，语气沉稳，目光坚毅。',
    'a close static shot on the white-robed young general volunteering to hold the rear, and with a firm, loyal voice (S1) he vows to see his lord across')],
 # [16,17] 刘备回望白影 / 牛车翻倾
 [C([16,16],4,'medium','Static Shot',['C01'],
   '中景，刘备回望那团烟尘里的白色身影，久久不肯催马先行，缰绳在掌中攥紧又松开。',
   '固定镜头，软袍贵族勒马凝望远处烟尘里那道白影，迟迟不肯催马前行，神色挣扎。',
   'a medium static shot of the nobleman looking back at the distant white figure, reluctant to spur on, his fist tightening on the reins'),
   C([17,17],4,'wide','Static Shot',[],
    '全景，乱军中一辆负重的牛车轰然翻倾，孩童惊哭，众人顿时乱作一团，泥水四溅。',
    '固定远镜，乱军里一辆牛车骤然翻倒，孩童惊哭、人群四散，泥水溅起一片。',
    'a wide static shot as an overloaded ox-cart topples over in the chaos, a child wails, and the crowd scatters in alarm')],
 # [18,19] 关羽 / 张飞 急促催走
 [C([18,18],4.5,'close','Static Shot',['C02'],
   '特写，关羽急声催道大哥，再不走，江岸都要被曹军封死了，长髯颤动，神色少见地急切。',
   '固定特写，红脸长髯武将急声催促，语气里透了慌张与担忧。',
   'a close static shot on the tall red-faced warrior, and with an urgent voice (S1) he warns the riverbank will soon be sealed by the enemy'),
   C([19,19],4.5,'close','Static Shot',['C03'],
    '特写，张飞在另一侧扬声急呼哥哥！渡口那边已经杀过来了，快随我走，一面扬鞭催促。',
    '固定特写，虬髯大汉扬声急呼，扬鞭催马，语气急切。',
    'a close static shot on the burly bearded general calling urgently from the side, and with a loud, hurried voice (S1) he urges retreat')],
 # [20,21] 刘备催马转头 / 叮嘱子龙
 [C([20,20],4,'close','Push In',['C01'],
   '特写，刘备回望烟尘深处，攥紧缰绳，眼眶通红，终于狠心催马转头，眼泪在旋身的瞬间泛起。',
   '镜头小幅缓推，软袍贵族攥紧缰绳、眼眶微红，终于狠下心催马转身，神色挣扎而坚毅。',
   'a push in on the nobleman tightening the reins with reddened eyes before finally turning his horse around, torn yet resolute'),
   C([21,21],5,'close','Static Shot',['C01'],
    '特写，刘备边催马边扬声叮嘱子龙，无论阿斗生死，你务必把少主带回来见我，声音在风里有些发哑。',
    '固定特写，软袍贵族催马回望扬声叮嘱，声音克制却字字沉甸。',
    'a close static shot on the nobleman, and with a hoarse, steady voice (S1) he commands the young general to bring his son back no matter what')],
 # [22,23,24] 赵云挑曹将回望 / 张飞担保 / 刘备催马渡水
 [C([22,22],4,'wide','Static Shot',['C11'],
   '全景，远处那团白影似有所应，赵云一枪挑开一名曹将，回身朝江岸边望来，枪尖尚悬着一线血光。',
   '固定远镜，远处白袍青年将军一枪挑开周遭一名敌将，回身向江岸方向望来，身影在烟尘中站定。',
   'a wide static shot as the distant white-robed spearman fells an enemy officer with one spear-thrust and glances back toward the riverbank'),
   C([23,23],5,'close','Static Shot',['C03'],
    '特写，张飞在侧扬声笑道大哥放心，子龙一身是胆，既应了，便定不辱命，神情里是铁打的笃定。',
    '固定特写，虬髯大汉扬声宽心，语气豪迈而笃定，眉眼间透着信任。',
    'a close static shot on the burly bearded general, and with a loud, confident voice (S1) he vouches for the spearman\'s courage'),
   C([24,24],6,'wide','Static Shot',['C01'],
    '大远景，刘备居中催马渡水，身后十万军民紧随，江水粼粼、浊浪翻卷，队伍铺满整个画面往对岸延去。',
    '固定远镜，软袍贵族居中策马踏入江水，身后迤逦的军民紧紧相随，浊浪翻卷铺满画面。',
    'a wide static shot of the nobleman urging his horse into the river with the vast host pressing behind, glittering water and rolling waves filling the frame')],
]
segs40s2 = seglist(40, 2, G40s2, osa40s2, mus40s2)
for idx, seg in enumerate(segs40s2):
    seg['blocking'] = BL40s2[idx + 1]
    seg['soundscape'] = SD40s2[idx]
    seg['music'] = MU40s2[idx]
# 新作段统一补 crowd note
for seg in segs40s1 + segs40s2 + segs39s2:
    for c in seg['cuts']:
        if len(c.get('characters', [])) > 3 and not c.get('note'):
            c['note'] = '同框人数超过三人，分镜图以提示词+参考图拆解各人位置与朝向。'
print('ep40 scene2 segs', len(segs40s2), 'total', ep_total(segs40s2))
print('ep40 total', round(ep_total(segs40s1) + ep_total(segs40s2), 1))

# ------------------------------------------------------------
# 8) 组装 episodes + 清洗 + 写回 storyboard-batch-8.json（UTF-8 无 BOM）
# ------------------------------------------------------------
def ep_obj(e, segments):
    return {'ep': e, 'segments': segments}

episodes = [
    ep_obj(36, ep36['segments']),
    ep_obj(37, ep37['segments']),
    ep_obj(38, ep38['segments']),
    ep_obj(39, ep39_segs_all),
    ep_obj(40, segs40s1 + segs40s2),
]
for e in episodes:
    tot = ep_total(e['segments'])
    assert 153 <= tot <= 207, f"ep{e['ep']} {tot}s 不在 [153,207]"
    print(f"ep{e['ep']} segs={len(e['segments'])} total={tot}s")

out = {
    'source': board.get('source', '三国演义'),
    'promptLang': board.get('promptLang', 'en'),
    'params': board.get('params', {'maxSegmentSeconds': 15, 'minCutSeconds': 2,
                                   'maxCutSeconds': 8, 'maxOnScreen': 3, 'tolerance': 0.15}),
    'episodes': episodes,
}
out.pop('seedScenes', None)

import io
raw = json.dumps(out, ensure_ascii=False, indent=2)
open(P, 'w', encoding='utf-8', newline='').write(raw)
b = raw.encode('utf-8')
print('BOM check: first bytes =', b[:3].hex(), '(efbbbf = BOM present)')
print('written', len(b), 'bytes ->', P)