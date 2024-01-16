function checkind(cominfo) {
var list = ["培训机构", "院校", "房产", "经纪", "工程施工", "批发", "零售", "再生资源"]; 
return list.every(item => !cominfo.includes(item))
}


function checkdesc(desctext) {
var list = ["uds","cdd","diva","整机测试","设备及仪器","蓝牙耳机","游戏测试","汽车","驾驶","车厂","机器人","硬件控制","单片","机顶盒","电机","串口","布线","上位","销售","营销","车间","车型","家具","电路","电气","弱电","变频","plc","pms","配电","电力","电子工艺","新材料","物料","家电","电能","采购","美妆","污染","大气","危废","气动","液压","电控","电池","给排水","限温","水利","水务","水文","水资源","化工","石油","土建","安防产品","手机厂商","请勿联系","兼职","质检员","退货","水泵","原标题","软著","课程","老师","家长","样衣","面辅料","3d设计","3d渲染","犀牛软件","三维建模","频谱","示波器","万用表","分析仪","焊接","电子元器件","车载","酷家乐","面料","女装","汽车行业","墨滴","喷射","喷头","材料化学","机械制图","喷墨","供墨系统","首饰","打板","售后问题","客情关系","客户上门","所属片区","打字速度","全屋定制","华广软件","定制家具","驻店","造诣软件","交换机","不是软件","土木","机械相关","生产设备","质检","平面设计","纺织","无人机","家纺","会员群","货品调配","*****","v50","82800","tr6850","protel","pcb","大学2字","暂挂","简历收集","非立即入职","没有空缺","天猫商家","钉群管理","电商开店","泛微招聘","甲方～","外貌要求","恕不退还","已找到","携带相关证件","6级或以上","21年及之前","焊点","211以上","211本科以上","211本科及以上","大二","大三","研二","研一","2年以上","2年及以上","2年或以上","3年以上","3年及以上","3年或以上","1-3年","1-2年","2-3年","3～5年","二年","2年","两年","4年","5年","年(含)以上"]; 
return list.every(item => !desctext.includes(item))
}

function checkactive(activetext) {
var list = ["半年", "月内", "本月", "周内", "本周", "7日"]; 
return list.every(item => !activetext.includes(item))
}

function checkchat(chattext) {
return chattext.includes("立即")
}


function checkboss(bosstext) {
var list = ["总裁", "总经理", "ceo", "创始人", "法人"]; 
return list.every(item => !bosstext.includes(item))
}

function checkname(nametext) {
var list = ["买手","微信","数通","维修","打单","单证","节目","智库","法务","部门","资料","分诊","录入","签证","物流","标注","建筑","惠普","速卖通","电商助理","营销","经销","城市规划","质检","回收","无人机","小白","收银","bim","caxa","跟线","管理","审计","样品","组长","主管","高级","渗透","爬虫","网络","游戏","架构","英文","英语","单片机","嵌入式软件开发","qt","unity","ue4","ue5","3d",".net","php","wpf","开发媒介","c语言开发","c++软件开发","前端开发","python开发","go","算法","c#"]; 
return list.every(item => !nametext.includes(item))
}

function checkcom(comtext) {
var list = ["乌鲁木齐","京北方","辛可必","信息咨询","美婷","富联富桂","培训","职业","中介","学校","人力","童星","儿童","童画","童美","工艺","青萍","喜悦","派森特","沐雨禾禾","中电金信","广日电梯","压寨","合伙","中科软","汉科软","快酷","奥特","原子云","泛微","创业","图墨","易科士","老乡鸡","美淘淘","麦田房产","招商银行","格林豪泰","佰钧成","我爱我家","地产","宸鸿","华众万象","丹迪兰","劲爆","天玑科技","华众科技","百思科技","绣歌","通力互联","北京银行","房产","房屋","销售","投资咨询","咨询管理","品牌","再生资源","玻璃","教育咨询","教育信息咨询","文化传承","文化传媒","经纪","旅馆","餐厅","宾馆","摄影","啦啦","旅游开发","法律咨询","文艺创作","水处理","合作社","婚纱","信用卡","维修","轿车","尔希","名人","演员","钟表","网吧","注册","托管","美嘉林","海绵","家居","担保","养殖","汽修","塑料","面包房","艺术","蛋糕","调味品","小吃","早教","宠物","保险","装饰","农场","假日","园艺","代理","练字","书法","书画","器材","烘培","焊业","歌城","美容","少儿","美术","门窗","人力市场","信用管理","建材","机械制造","模具","建筑工程","配件","服装","健身","化妆","美颜","加盟","皇家","花苑","舞蹈","农产品","小镇","直营","托育","工会","练习","宏源电子","鞋业","鞋厂","叮咚","卓杭","商场","商行","经营部","策马科技","任拓"]; 
return list.every(item => !comtext.includes(item))
}


launchApp("BOSS直聘");
sleep(5000);
click(930,96,1052,217);
sleep(5000);
id("et_search").findOne().setText("Java");
id("tv_search").findOne().click();
sleep(5000);
//click(28,365,177,446);
//id("tv_btn_action").findOne().click()
click(177,365,398,446);
sleep(3000);
click(55,1901,231,1966);
sleep(5000);
click(398,365,547,446);
sleep(3000);
id("keywords_view_text").className("android.widget.TextView").text("高中").findOne().click()
id("keywords_view_text").className("android.widget.TextView").text("大专").findOne().click()
id("keywords_view_text").className("android.widget.TextView").text("本科").findOne().click()
id("keywords_view_text").className("android.widget.TextView").text("应届生").findOne().click()
id("keywords_view_text").className("android.widget.TextView").text("经验不限").findOne().click()
id("keywords_view_text").className("android.widget.TextView").text("3-5K").findOne().click()
id("keywords_view_text").className("android.widget.TextView").text("1年以内").findOne().click()
id("keywords_view_text").className("android.widget.TextView").text("1-3年").findOne().click()
id("keywords_view_text").className("android.widget.TextView").text("20-99人").findOne().click()
id("keywords_view_text").className("android.widget.TextView").text("100-499人").findOne().click()
id("keywords_view_text").className("android.widget.TextView").text("500-999人").findOne().click()
id("keywords_view_text").className("android.widget.TextView").text("1000-9999人").findOne().click()
id("keywords_view_text").className("android.widget.TextView").text("10000人以上").findOne().click()
id("btn_confirm").findOne().click()
sleep(5000);
var x = 0; 
for (var i = 0; i < 5; i++) {
  x = x + 1;  
id("boss_job_card_view").find().forEach(function(child){
var bosstext = child.findOne(id("tv_employer")).text();
toastLog(bosstext); 
var nametext=child.findOne(id("tv_position_name")).text();
toastLog(nametext); 
var comtext = child.findOne(id("tv_company_name")).text();
toastLog(comtext); 

if (checkname(nametext) && checkcom(comtext) && checkboss(bosstext)){
child.parent().parent().click();
toastLog("检查详情"); 
sleep(3000);
var activetext = id("boss_label_tv").findOne().text();
toastLog(activetext); 
var desctext =id("tv_description").findOne().text();
toastLog(desctext); 
var chattext=id("btn_chat").findOne().text();
toastLog(chattext); 
swipe(535, 1800, 535, 409, 500)
sleep(2000);
var cominfo = id("tv_com_info").findOne().text();
toastLog(cominfo); 
var comtext = id("tv_com_name").findOne().text();
toastLog(comtext); 

if(checkdesc(desctext) && checkactive(activetext) && checkchat(chattext) && checkind(cominfo) && checkcom(comtext)){
id("btn_chat").findOne().click();
sleep(3000);
back();
sleep(2000);
}
back();
sleep(2000);
}})
swipe(535, 1800, 535, 609, 500)
swipe(535, 1800, 535, 609, 500)
sleep(3000);
}


