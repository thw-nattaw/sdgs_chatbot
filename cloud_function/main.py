import functions_framework
from google.cloud import secretmanager
from google.cloud.sql.connector import Connector
import sqlalchemy
import pymysql
import base64
import vertexai
from vertexai.generative_models import GenerativeModel, Part, SafetySetting, FinishReason
import vertexai.preview.generative_models as generative_models
import json
from flask import make_response

client = secretmanager.SecretManagerServiceClient()

def INSTANCE_CONNECTION_NAME():
    name = #Project Name
    response = client.access_secret_version(request={"name": name})
    secret_key = response.payload.data.decode("UTF-8")
    return secret_key

def DB_USER():
    name = #Username
    response = client.access_secret_version(request={"name": name})
    secret_key = response.payload.data.decode("UTF-8")
    return secret_key

def DB_PASS():
    name = #Password
    response = client.access_secret_version(request={"name": name})
    secret_key = response.payload.data.decode("UTF-8")
    return secret_key

INSTANCE_CONNECTION_NAME = INSTANCE_CONNECTION_NAME()
DB_USER = DB_USER()
DB_PASS = DB_PASS()
DB_NAME = #Database name

vertexai.init(project="sdg-gc-hackathon", location="asia-northeast1")
model = GenerativeModel("gemini-1.5-flash")

def create_prompt(table_info,input_text):
  prompt = f"""
  #ROLE
  You're a Google SQL expert. You'll write MySQL query to retrieve data from a table on CloudSQL based on rows and columns data provided in #TABLE_INFORMATION only.
  
  #INSTRUCTIONS
  1.Read #INPUT and think about what data need to be used to answer it.
  2.Then refer to #TABLE_INFORMATION and generate MySQL query that is needed to get such data.
  3.The generated query must strictly follow the #CONDITIONS,
  4.Return only generated SQL query in response.
  
  #CONDITIONS
  1.Never query from all columns. Only query the necessary columns.
  2.Only query data from columns provided in #TABLE_INFORMATION. Do not query non-existing columns.
  3.Only select rows that are related to #INPUT; it can be multiple rows.
  4.Don't forget to select key values that help interpret the results.
  5.The fields are written in both Japanese and English.
  
  #TABLE_INFORMATION
  {table_info}
  
  #INPUT
  {input_text}
  """
  return prompt

table_info_dict = {}

table_info_dict["gyogyo"] = f"""
Table name: gyogyo
Columns: 漁業種類, 年次, value
Rows in 漁業種類 column: '漁獲量計', '網漁業_底びき網_遠洋底びき網_遠洋底びき網', '網漁業_底びき網_以西底びき網_以西底びき網',
       '網漁業_底びき網_沖合底びき網_1そうびき', '網漁業_底びき網_沖合底びき網_2そうびき',
       '網漁業_底びき網_小型底びき網_縦びき1種', '網漁業_船びき網_船びき網計',
       '網漁業_まき網_大中型まき網_1そうまき_遠洋かつお･まぐろまき網',
       '網漁業_まき網_大中型まき網_1そうまき_近海かつお･まぐろまき網',
       '網漁業_まき網_大中型まき網_1そうまき_その他の1そうまき網', '網漁業_まき網_大中型まき網_2そうまき網_2そうまき網計',
       '網漁業_まき網_中小型まき網_1そうまき巾着網', '網漁業_刺網_さけ･ます流し網', '網漁業_刺網_かじき等流し網',
       '網漁業_刺網_その他の刺網', '網漁業_敷網_さんま棒受網', '網漁業_定置網_大型定置網', '網漁業_定置網_さけ定置網',
       '網漁業_定置網_小型定置網', '網漁業_その他の網漁業', '釣漁業_はえ縄_まぐろはえ縄_遠洋まぐろはえ縄_計',
       '釣漁業_はえ縄_まぐろはえ縄_近海まぐろはえ縄', '釣漁業_はえ縄_まぐろはえ縄_沿岸まぐろはえ縄',
       '釣漁業_はえ縄_その他のはえ縄', '釣漁業_はえ縄以外の釣_かつお一本釣_遠洋かつお一本釣',
       '釣漁業_はえ縄以外の釣_かつお一本釣_近海かつお一本釣', '釣漁業_はえ縄以外の釣_かつお一本釣_沿岸かつお一本釣',
       '釣漁業_はえ縄以外の釣_いか釣_遠洋いか釣', '釣漁業_はえ縄以外の釣_いか釣_近海いか釣',
       '釣漁業_はえ縄以外の釣_いか釣_沿岸いか釣', '釣漁業_はえ縄以外の釣_ひき縄釣', '釣漁業_はえ縄以外の釣_その他の釣',
       'その他の漁業_採貝', 'その他の漁業_その他の漁業'
Rows in 年次 column: 2000-2022

#Additional condition
1. if the user query is not specific to types of fishing (漁法), only select the value where 漁業種類 = 漁獲量計
2. Exclude Where 漁業種類 = 漁獲量計 when users ask about a method of fishing(漁法).
"""

table_info_dict["caughtfish"] = f"""
Table name: caughtfish
Columns: 海面漁業魚種, 年次, unit, value
Rows in 栄養素等 column: '海面漁業計', '魚類_まぐろ類', '魚類_まぐろ類_くろまぐろ', '魚類_まぐろ類_みなみまぐろ',
       '魚類_まぐろ類_びんなが', '魚類_まぐろ類_めばち', '魚類_まぐろ類_きはだ', '魚類_かじき類',
       '魚類_かつお類_小計', '魚類_かつお類_かつお', '魚類_かつお類_そうだがつお類', '魚類_さめ類',
       '魚類_さけ・ます類_小計', '魚類_さけ・ます類_さけ類', '魚類_さけ・ます類_ます類', '魚類_にしん',
       '魚類_いわし類', '魚類_いわし類_まいわし', '魚類_いわし類_うるめいわし', '魚類_いわし類_かたくちいわし',
       '魚類_あじ類', '魚類_あじ類_まあじ', '魚類_さば類', '魚類_さんま', '魚類_ぶり類',
       '魚類_ひらめ・かれい類', '魚類_たら類_まだら', '魚類_たら類_すけとうだら', '魚類_ほっけ', '魚類_たちうお',
       '魚類_たい類', '魚類_たい類_まだい', '魚類_いかなご', 'えび類', 'かに類', '貝類_あわび類',
       '貝類_さざえ', '貝類_はまぐり類', '貝類_あさり類', '貝類_ほたてがい', '貝類_さるぼう(もがい)', 'いか類',
       'いか類_するめいか', 'たこ類', '海産哺乳類', '海藻類_こんぶ類', '海藻類_わかめ類', '海藻類_ひじき',
       '捕鯨業(くじら類)'
Rows in 年次 column: 2000-2016
"""

table_info_dict["aquaculture"] = f"""
Table name: aquaculture
Columns: 海面漁業魚種, 年次, unit, value
Rows in 栄養素等 column: '海面養殖業計', '魚類_ぶり類', '魚類_まだい', '魚類_くろまぐろ', '貝類_ほたてがい', '貝類_かき類',
       '海藻類_こんぶ類', '海藻類_わかめ類', '海藻類_のり類', '真珠'
Rows in 年次 column: 2000-2016
"""

table_info_dict["waste"] = f"""
Table name: waste
Columns: 旧産業分類	, 年度, unit, value
Rows in 旧産業分類 column: '耕種農業', '畜産農業', '林業大分類', '漁業', '水産養殖業', '鉱業', '建設業', '食料品製造業',
       '飲料・たばこ・飼料製造業', '繊維工業', '衣類・その他の繊維製品製造業', '木材・木製品製造業', '家具・装備品製造業',
       'パルプ・紙・紙加工品製造業', '印刷・同関連業', '化学工業', '石油製品・石炭製品製造業', 'プラスチック製品製造業',
       'ゴム製品製造業', 'なめし革・同製品・毛皮製造業', '窯業・土石製品製造業', '鉄鋼業', '非鉄金属製造業',
       '金属製品製造業', '汎用、生産、業務', '一般機械器具製造業', '電気機械器具製造業', '電子、電気、情報',
       '情報通信機械器具製造業', '電子部品・デバイス製造業', '輸送用機械器具製造業', '精密機械器具製造業',
       'その他の製造業', '電気業', 'ガス業', '熱供給業', '上水道業', '下水道業', '通信業', '放送業',
       '情報サービス業', 'インターネット付随サービス業', '映像・音声・文字情報制作業', '鉄道業', '道路旅客運送業',
       '道路貨物運送業', '上記以外の運輸通信業', '各種商品卸売業', '各種商品小売業', '自動車小売業',
       '家具・じゅう器・機械器具小売業（人）', '燃料小売業（人）', '上記以外の卸売・小売業・飲食店小売業（人）',
       '一般飲食店（人）', '上記以外の飲食店，宿泊業（人）', '医療業（床）', '上記以外の医療、福祉（人）',
       '教育、学習支援業大分類（人）', '複合サービス事業大分類（人）', '写真業（人）', '学術開発研究機関（人）',
       '洗濯業（人）', '自動車整備業（人）', 'と畜場（人）', 'と畜場（頭）', '上記以外のサービス業（人）',
       '公務大分類（人）'
Rows in 年度 column: 2003-2013
"""

table_info_dict["nutrition"] = f"""
This is a table about average consumed nutrition per day in Japan and each region of Japan.
Table name: nutrition
Columns: 栄養素等, 地域ブロック, 年次, unit, value
Rows in 栄養素等 column: 'エネルギー', 'たんぱく質', 'たんぱく質_動物性', '脂質', '脂質_動物性', '脂肪酸_飽和脂肪酸',
       '脂肪酸_一価不飽和脂肪酸', '脂肪酸_n-6系脂肪酸', '脂肪酸_n-3系脂肪酸', 'コレステロール', '炭水化物',
       '食物繊維_総量', '食物繊維_水溶性', '食物繊維_不溶性', 'ビタミンＡ', 'ビタミンＤ', 'ビタミンＥ',
       'ビタミンＫ', 'ビタミンＢ1', 'ビタミンＢ2', 'ナイアシン', 'ビタミンＢ6', 'ビタミンＢ12', '葉酸',
       'パントテン酸', 'ビタミンＣ', 'ナトリウム', '食塩相当量_g', '食塩相当量_g/1,000kcal', 'カリウム',
       'カルシウム', 'マグネシウム', 'リン', '鉄', '亜鉛', '銅', '脂肪エネルギー比率',
       '炭水化物エネルギー比率', '動物性たんぱく質比率', '穀類ｴﾈﾙｷﾞｰ比率'
Rows in 地域ブロック column: '全国', '北海道', '東北', '関東', '北陸', '東海', '近畿', '中国', '四国', '九州'
Rows in 年次 column: 2012-2019
"""

def final_prompt(input_text,sql_query,sql_response):
    final_prompt = response_prompt = f"""
    #ROLE
    You're a data expert. You'll answer a question based on the data retrieved from MySQL database only.

    #INSTRUCTIONS
    1.Read #QUESTION and think about what data need to be used to answer it.
    2.Then refer to data #SQL_RESPONSE and MySQL query #SQL_QUERY which used to retrieve such data. Think carefully how it can be used to answer #QUESTION
    3.Generate response to #QUESTION without using other information apart from what provided and then return as an output in Japanese.

    #CONDITIONS
    1.The input question will be in Japanese. Output also need to be in Japanese.
    2.Only use data provided in #QUESTION, #SQL_QUERY, and #SQL_RESPONSE.
    3.The fields are written in both Japanese and English.

    #QUESTION
    {input_text}

    #SQL_QUERY
    {sql_query}

    #SQL_RESPONSE
    {sql_response}
    """
    return final_prompt


@functions_framework.http
def main(request):

    if request.path == "/":
        table_name = "nutrition"
    elif request.path == "/gyogyo":
        table_name = "gyogyo"
    elif request.path == "/caughtfish":
        table_name = "caughtfish"
    elif request.path == "/aquaculture":
        table_name = "aquaculture"
    elif request.path == "/waste":
        table_name = "waste"
    elif request.path == "/nutrition":
        table_name = "nutrition"
    else:
        return 'Please provide accurate path or table name.'

    request_json = request.get_json(silent=True)
    request_args = request.args

    connector = Connector()
    def getconn():
        conn = connector.connect(
            INSTANCE_CONNECTION_NAME,
            "pymysql",
            user=DB_USER,
            password=DB_PASS,
            db=DB_NAME
        )
        return conn

    pool = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=getconn,
    )

    for attempt_num in range(5):
        try:
            if request_json and 'input' in request_json:
                input_text = request_json['input']
            elif request_args and 'input' in request_args:
                input_text = request_args.get('input')
            else:
                return('No input information provided')
                break

            query = create_prompt(table_info_dict[table_name],input_text)
            response = model.generate_content(query)

            sql_query = response.text.strip("```sql\n").strip("\n```")

            with pool.connect() as db_conn:
                sql_response = db_conn.execute(sqlalchemy.text(sql_query)).fetchall()
                connector.close()

            final_query = final_prompt(input_text,sql_query,sql_response)
            response_final = model.generate_content(final_query)
            break
        except:
            attempt_num += 1

    return make_response(json.dumps(response_final.text), 200, {'Content-Type': 'application/json'})
