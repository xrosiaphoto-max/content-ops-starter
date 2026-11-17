# SNS 自動化（① リール自動生成 + ② 毎日自動投稿）

スタジオで撮った物撮り写真を入れるだけで、Instagram リールと X 用の縦型動画を作り、毎日決まった時刻に自動投稿する仕組みです。

```
[撮影] → inbox/ に写真セットを置く
          │  python -m sns_auto build   （自分のPCで実行）
          ▼
   9:16 リール動画を生成 → R2/S3 にアップロード → queue.yaml に1日1本ずつ予約
          │  git push
          ▼
   GitHub Actions が毎日 19:07 JST に queue.yaml の先頭を Instagram と X に投稿
```

## 1. 準備（最初の1回だけ）

### 1-1. PC 側
- Python 3.10 以上と ffmpeg をインストールする（Mac の場合は `brew install ffmpeg`）
- `cd sns-automation && pip install -r requirements.txt`
- 日本語テロップ用のフォントを `assets/fonts/NotoSansJP-Bold.ttf` に置く（Google Fonts の Noto Sans JP）。置かなかった場合は、OS に入っているヒラギノ（Mac）やメイリオ（Windows）を自動で使います。
- BGM を使う場合は、**著作権フリーの音源**を `assets/bgm/` に入れる（ランダムで使われます）。
  ※ Instagram アプリ内の人気曲は、API 投稿では付けられません。

### 1-2. 動画置き場（Instagram に必須）
Instagram の API は動画ファイルを直接受け取らず、**公開 URL** から取得します。Cloudflare R2 がおすすめです（下り転送が無料）。
1. R2 でバケットを作り、Public access（r2.dev か独自ドメイン）を有効にする
2. R2 の API トークン（読み書き）を作る
3. PC の環境変数（`.env` などで設定）

| 変数 | 例 |
|---|---|
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | R2 の API トークン |
| `S3_BUCKET` | `reels` |
| `S3_ENDPOINT_URL` | `https://<accountid>.r2.cloudflarestorage.com` |
| `S3_PUBLIC_BASE_URL` | `https://media.example.com` |

### 1-3. Instagram
1. Instagram アカウントを**プロアカウント**（ビジネスまたはクリエイター）にする
2. [Meta for Developers](https://developers.facebook.com/) でアプリを作り、「Instagram API（Instagram ログイン）」を追加する
3. 権限 `instagram_business_basic` と `instagram_business_content_publish` で自分のアカウントを接続し、**長期アクセストークン**と**ユーザー ID** を取得する
4. 自分のアカウントだけに投稿する場合は、開発モードのままで動きます（アプリ審査は、他人のアカウントを扱う場合に必要です）

> トークンの有効期限は 60 日です。月に 1 回 `python -m sns_auto refresh-ig-token` を実行し、表示された新しいトークンで GitHub Secret を更新してください。

### 1-4. X
1. [X Developer Portal](https://developer.x.com/) でプロジェクトとアプリを作る
2. User authentication settings で App permissions を **Read and Write** にする
3. 「Keys and tokens」で API Key / Secret と Access Token / Secret を発行する（権限を変更した後で発行し直すこと）
4. 料金プランによって投稿数の上限が変わります。1 日 1 本なら最小のプランで足りる想定ですが、契約前に最新の料金表を確認してください。

### 1-5. GitHub Secrets
リポジトリの Settings → Secrets and variables → Actions に登録します。

`IG_USER_ID`, `IG_ACCESS_TOKEN`, `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_SECRET`

## 2. 毎日の運用

```bash
# 1) 写真セットを作る（1フォルダ = リール1本）
cp -r examples/2026-11-lip-cosme inbox/lip-red
#    → inbox/lip-red/ に写真を入れて meta.yaml を書き換える

# 2) 動画を確認だけしたいとき（アップロードしない）
python -m sns_auto build --no-upload --keep
#    → output/ の mp4 を確認

# 3) 本番：生成 → アップロード → 予約
python -m sns_auto build
python -m sns_auto status        # 予約一覧
git add queue.yaml && git commit -m "add posts" && git push
```

まとめて 30 セット入れておけば、30 日分が 1 日 1 本ずつ自動で投稿されます。ストックが 3 本を切ると、Actions のログに警告が出ます。

### 投稿のテスト
GitHub の Actions タブで「SNS daily post」→ Run workflow を開き、`dry_run` にチェックを入れて実行すると、実際には投稿せずキャプションを確認できます。

## 3. 設定の変更（`config.yaml`）
- 投稿時刻：`.github/workflows/sns-daily-post.yml` の `cron`（UTC で書く。JST − 9 時間）
- 1 枚あたりの秒数、ズーム量、背景色、テロップの表示秒数：`reel:`
- 共通ハッシュタグ、キャプションのテンプレート：`caption:`
- 片方だけ投稿する場合：`posting.instagram.enabled` / `posting.x.enabled`

## 仕組みの補足
- 片方の SNS だけ失敗した場合、次回はその SNS だけ再投稿します（二重投稿しません）。エラー内容は `queue.yaml` の `errors` に残ります。
- 生成される動画：1080×1920、30fps、H.264 + AAC、faststart。Instagram リールと X の推奨形式です。
- 投稿はすべて公式 API で行います。いいね、フォロー、閲覧の自動化（水増し）は規約違反なので入れていません。
