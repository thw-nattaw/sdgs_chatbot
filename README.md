EN follows JP

# ともちゃんボット
## ともに未来へ歩こう〜サスティナブルに〜

ともちゃんチャットボットは、日本の政策や統計データに関連する持続可能な開発目標（SDGs）に焦点を当てた知識ベースのチャットボットです。Google Vertex AI Agent Builder を使用して構築されました。

このリポジトリには 3 つのフォルダーが含まれています。

1. agent_and_tool
このフォルダーには、エージェントのアーキテクチャ、各エージェントのプロンプト、および YAML 形式の OpenAPI ツールの OpenAPI スキーマが含まれています。
デフォルトのエージェントは、各目標のエージェントに接続されています。デモ版では、SDG ゴール 2、12、14 のエージェントのほか、全体的な知識やその他の SDG 目標用の 一般的な SDG エージェントも利用できます。
各目標固有のエージェントは、データストアに保存されている日本政府の政策の PDF ファイルである政策ツールと、OpenAPI ツールである統計データ エージェントを呼び出すことができます。OpenAPI ツールは、Cloud SQL の表形式データにアクセスできる Cloud Run 関数に接続されています。

2. cloud_function
このフォルダには、エージェント (統計データ ツール) から呼び出すことができる Google Cloud Run Function にデプロイされた Python コードが含まれています。テーブル名へのパスと入力パラメータを受け取ります。次に、Gemini 1.5 Flash を使用して SQL コードが生成されます。Cloud SQL データベースから取得されたデータは、ユーザーへの応答を生成するために使用されます。

3. goapp
このフォルダには、Go で記述されたフロントエンド コードが含まれています。Google App Engine でホストされています。

デモ　https://sdg-gc-hackathon.an.r.appspot.com/
__________________

# Tomo-Chan Chatbot
## Let's walk towards the sustainable future together~

The Tomo-chan Chatbot is a knowledge-based chatbot focused on Sustainable Development Goals (SDGs) related to Japanese policy and statistical data. It was built using Google Vertex AI Agent Builder.

This repository contains three folders:

1. agent_and_tool
This folder contains the architecture of the agent, the prompt for each agent, and the OpenAPI schema of the OpenAPI tools in YAML format.
The default agent is connected to the agents for each goal. In the demo version, agents for SDG Goals 2, 12, and 14 are available, as well as a general SDGs agent for overall knowledge and other SDG goals.
Each goal-specific agent can call policy tools, which are PDF files of Japanese government policies stored in the datastore, and statistical data agents, which are OpenAPI tools. The OpenAPI tools are connected to Cloud Run functions that can access tabular data in Cloud SQL.

2. cloud_function
This folder contains Python code deployed in a Google Cloud Run function, which can be called by the agent (Statistical Data Tool). It receives the path to the table name and the input parameters. Next, SQL code is generated using Gemini 1.5 Flash. The data retrieved from the Cloud SQL database is used to generate a response for the user.

3. goapp
This folder contains front-end code written in Go. It is hosted on Google App Engine.

Demo https://sdg-gc-hackathon.an.r.appspot.com/
