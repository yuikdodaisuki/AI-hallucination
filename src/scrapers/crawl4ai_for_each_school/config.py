import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# LLM配置
LLM_MODEL = "openai/deepseek-v3-0324"
LLM_BASE_URL = "https://api.lkeap.cloud.tencent.com/v1"
API_KEY_ENV = "DEEPSEEK_API_KEY"

# 输出配置
OUTPUT_DIR = "school_data"
OUTPUT_FILE = "school_intros.json"

# 学校网站配置
SCHOOL_WEBSITES = {
    # 重点大学
    "中山大学": "https://www.sysu.edu.cn/xxg/zdjj1.htm",
    "华南理工大学": "https://www.scut.edu.cn/new/9015/list.htm",
    "暨南大学": "https://www.jnu.edu.cn/bxsj/list.htm",
    "华南师范大学": "https://www.scnu.edu.cn/a/20161025/1.html",
    "华南农业大学": "https://www.scau.edu.cn/17830/list.htm",
    "广州医科大学": "https://www.gzhmu.edu.cn/xxgk/xxjj.htm",
    "广州中医药大学": "https://www.gzucm.edu.cn/xxgk/xxjj.htm",
    "广东药科大学": "https://www.gdpu.edu.cn/xygk/xxjj.htm",
    "南方医科大学": "https://www.smu.edu.cn/xygk/xxjj.htm",
    "广州大学": "https://www.gzhu.edu.cn/xxgk/xxjj.htm",
    "广东工业大学": "https://www.gdut.edu.cn/xxgk/xxjj.htm",
    "广东外语外贸大学": "https://www.gdufs.edu.cn/About%20GDUFS/General_Information.htm",
    "广东财经大学": "https://www.gdufe.edu.cn/gcjj/list.htm",
    
    # 体育、艺术院校
    "广州体育学院": "https://www.gzsport.edu.cn/node/42",
    "广州美术学院": "https://www.gzarts.edu.cn/index/xxgk.htm",
    "星海音乐学院": "https://www.xhcom.edu.cn/xxgk1/xxjj.htm",
    
    # 师范、技术院校
    "广东技术师范大学": "https://www.gpnu.edu.cn/xxgk/xxjj.htm",
    "广东第二师范学院": "https://www.gdei.edu.cn/1334/list.htm",
    "仲恺农业工程学院": "https://www.zhku.edu.cn/xxgk/xxjs.htm",
    "广东警官学院": "https://www.gdppla.edu.cn/xxgk/xxjj.htm",
    "广东金融学院": "https://www.gduf.edu.cn/xygk/gjjj.htm",
    "广州航海学院": "https://www.gzmtu.edu.cn/xxgk/xxgk.htm",
    
    # 独立学院和民办大学
    "广州城市理工学院": "https://www.gcu.edu.cn/2023/0308/c725a146388/page.htm",
    "广州软件学院": "https://www.seig.edu.cn/xxgk/xxjj.htm",
    "广州南方学院": "https://www.nfu.edu.cn/gywm/xxgk.htm",
    "广东外语外贸大学南国商学院": "https://www.gwng.edu.cn/37/list.htm",
    "广州华商学院": "https://www.gdhsc.edu.cn/xygk/xyjj.htm",
    "华南农业大学珠江学院": "https://www.scauzj.edu.cn/xxgk/xxjj/D700102index_1.htm",
    "广州理工学院": "https://www.gzist.edu.cn/xxgk/xxjj.htm",
    "广州华立学院": "https://www.hualixy.edu.cn/xxgk/xxjj",
    "广州应用科技学院": "https://www.gzasc.edu.cn/IntroductionToTheSchool/index.html",
    "广州商学院": "https://www.gcc.edu.cn/xxgk/xxjj/index.htm",
    "广州工商学院": "https://www.gzgs.edu.cn/xxgk/xxjj.htm",
    "广州新华学院": "https://www.xhsysu.edu.cn/xxgk/xxjj.htm",
    "广东白云学院": "https://www.baiyunu.edu.cn/html/cn/gyby/",
    "广东培正学院": "https://www.peizheng.edu.cn/xxgk1/xxjs/index.htm",
    
    # 职业技术大学
    "广东轻工职业技术大学": "https://www.gdqy.edu.cn/info/1059/2741.htm",
    "广州科技职业技术大学": "https://www.gkd.edu.cn/contents/1457/113.html",
    "广州番禺职业技术学院": "https://www.gzpyp.edu.cn/xxgk/xxjj",
    
    # 特殊情况
    "香港科技大学（广州）": "https://www.hkust-gz.edu.cn/about/",
    
}

# 其他配置保持不变...
CRAWL_INTERVAL = 3
MAX_CONCURRENT = 3
ENABLE_HEADLESS = False
PAGE_TIMEOUT = 60000
DELAY_BEFORE_RETURN = 10.0
OUTPUT_DIR = "output"

ENABLE_URL_VALIDATION = True
MAX_RETRY_ATTEMPTS = 2