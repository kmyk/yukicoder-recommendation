# Yukicoder Recommendation

-   <https://psyched-oxide-184819.appspot.com/>
-   <https://psyched-oxide-184819.appspot.com/?name=yuki2006>

## これはなに

Yukicoder(<https://yukicoder.me/>)上のFav情報からおすすめの問題を提案してくれるwepアプリです

![screenshot](https://user-images.githubusercontent.com/2203128/32404658-6dccbb40-c197-11e7-9dad-af1553d81969.png)

## memo

-   frontend
    -   実装はFlask+MySQL
    -   hostはGAE
    -   herokuも試したがDB部分が無料枠に収まらなさげだったので棄却
    -   ISUCON7 予選の[コード](https://github.com/isucon/isucon7-qualify/blob/master/webapp/python/app.py)を参考に作った
    -   DBを持ち出すほどのデータ量ではない気もするが、他に良い手法を知らず
-   backend
    -   fav情報やAC情報をwebからscrapingしてDBに投げる
    -   localにて手動で叩く
    -   ここの自動化をする元気はもうない
-   管理
    -   GAEへの反映: `cd frontend ; gcloud app deploy`
    -   手元でpreview: `DB_HOST=$DB_HOST DB_USER=$DB_USER DB_PASSWORD=$DB_PASSWORD py3 frontend/server.py`
    -   手元でscrapingして鯖にinsert: `DB_HOST=$DB_HOST DB_USER=$DB_USER DB_PASSWORD=$DB_PASSWORD py3 backend/main.py`
-   他
    -   機械学習+webで後に残るものを作りたかった
    -   開発は1日だったのにdeployに3日かかった
    -   プログラミングで最も難しいのは環境構築だと再確認させられてしまった
    -   後者で力尽きたのとデータ量が少なかったので機械学習することはなかった
    -   本体に負荷かかる(+ scrapingが面倒)なのでそのうち落とす
