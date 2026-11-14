---
title: トップ
slug: /
sections:
  - type: GenericSection
    title:
      text: 一社のモヤモヤを、業界みんなの答えに変える。
      color: text-dark
      type: TitleBlock
    subtitle: 中小企業の「毎回めんどう」「ミスが怖い」を、使える形にして届けます。
    text: |-
      見積もり、請求の照合、問い合わせへの返信。どの会社でも同じところでつまずいています。

      一社の悩みを聞いて形にし、同じ業種の会社が使える答えにして届けるのが、合同会社XROSIAの仕事です。
    actions:
      - label: まずは相談する（無料）
        altText: お問い合わせへ
        url: '#contact'
        showIcon: true
        icon: arrowRight
        iconPosition: right
        style: primary
        elementId: ''
        type: Button
      - label: できること
        altText: できることへ
        url: '#services'
        showIcon: false
        icon: arrowRight
        iconPosition: right
        style: secondary
        elementId: ''
        type: Button
    elementId: ''
    colors: bg-light-fg-dark
    styles:
      self:
        alignItems: center
        flexDirection: col
        padding:
          - pt-24
          - pl-8
          - pb-24
          - pr-8
        textAlign: center
        justifyContent: center
  - type: FeaturedItemsSection
    title:
      text: こんなモヤモヤ、ありませんか
      color: text-dark
      styles:
        self:
          textAlign: center
      type: TitleBlock
    subtitle: どれも「うちだけ」ではありません。同じ業種の多くの会社が抱えています。
    items:
      - type: FeaturedItem
        title: 見積もりに時間を取られる
        text: >-
          下請けからの見積書をまとめ直し、諸経費と利益を乗せて、施主向けに仕上げる。毎回ほぼ同じ作業なのに、夜までかかる。
        actions: []
        colors: bg-neutralAlt-fg-dark
        styles:
          self:
            padding:
              - pt-8
              - pl-8
              - pb-8
              - pr-8
            borderRadius: x-large
            textAlign: left
      - type: FeaturedItem
        title: 計算ミスが怖い
        text: >-
          Excelの数字を手で写すたびに不安になる。単価が上がったのに古い数字のまま出していないか、ずっと気になっている。
        actions: []
        colors: bg-neutralAlt-fg-dark
        styles:
          self:
            padding:
              - pt-8
              - pl-8
              - pb-8
              - pr-8
            borderRadius: x-large
            textAlign: left
      - type: FeaturedItem
        title: 事務が社長に集まる
        text: >-
          請求の照合、問い合わせの返信、書類の下書き。人を雇うほどではないが、社長が自分でやるには重い。
        actions: []
        colors: bg-neutralAlt-fg-dark
        styles:
          self:
            padding:
              - pt-8
              - pl-8
              - pb-8
              - pr-8
            borderRadius: x-large
            textAlign: left
    actions: []
    variant: three-col-grid
    colors: bg-neutral-fg-dark
    styles:
      self:
        padding:
          - pt-16
          - pl-8
          - pb-16
          - pr-8
        justifyContent: center
      subtitle:
        textAlign: center
  - type: FeaturedItemsSection
    elementId: services
    title:
      text: できること
      color: text-dark
      styles:
        self:
          textAlign: center
      type: TitleBlock
    subtitle: まずは無料の相談から。合うと思っていただけた分だけ、段階的にお手伝いします。
    items:
      - type: FeaturedItem
        tagline: STEP 1
        title: 無料相談
        text: >-
          いま何に時間を取られているか、どこでミスが起きやすいかを伺います。売り込みはしません。お話を聞いて、形にできそうかをお伝えします。
        actions: []
        colors: bg-light-fg-dark
        styles:
          self:
            padding:
              - pt-8
              - pl-8
              - pb-8
              - pr-8
            borderRadius: x-large
            textAlign: left
      - type: FeaturedItem
        tagline: STEP 2
        title: すぐ使える型（テンプレート）
        text: >-
          見積もり自動化のExcelなど、同じ業種の会社がそのまま使える既製品。単価表を入れ替えるだけで、入力→計算→見積書→PDFまで進みます。
        actions: []
        colors: bg-light-fg-dark
        styles:
          self:
            padding:
              - pt-8
              - pl-8
              - pb-8
              - pr-8
            borderRadius: x-large
            textAlign: left
      - type: FeaturedItem
        tagline: STEP 3
        title: 御社専用につくる
        text: >-
          御社の書式・工種・単価・ロゴに合わせて、専用版をおつくりします。過去の案件で答え合わせをしてからお渡しします。
        actions: []
        colors: bg-light-fg-dark
        styles:
          self:
            padding:
              - pt-8
              - pl-8
              - pb-8
              - pr-8
            borderRadius: x-large
            textAlign: left
      - type: FeaturedItem
        tagline: STEP 4
        title: 続けて面倒を見る（月額）
        text: >-
          単価の更新、見積もり・請求照合・問い合わせ返信の下書きを代わりに作ります。仕上げと送信は御社で。事務員を一人雇うより軽い形で続けられます。
        actions: []
        colors: bg-light-fg-dark
        styles:
          self:
            padding:
              - pt-8
              - pl-8
              - pb-8
              - pr-8
            borderRadius: x-large
            textAlign: left
    actions:
      - label: 相談してみる
        altText: お問い合わせへ
        url: '#contact'
        showIcon: true
        icon: arrowRight
        iconPosition: right
        style: primary
        elementId: ''
        type: Button
    variant: two-col-grid
    colors: bg-neutral-fg-dark
    styles:
      self:
        padding:
          - pt-16
          - pl-8
          - pb-16
          - pr-8
        justifyContent: center
      subtitle:
        textAlign: center
  - type: GenericSection
    elementId: approach
    title:
      text: 進め方
      color: text-dark
      type: TitleBlock
    text: |-
      **1. 悩みを聞く**　どこで時間がかかり、どこでミスが起きているかを、現場の言葉のまま伺います。

      **2. 形にする**　毎回くり返している作業を、使える形（Excel・書式・手順）にします。

      **3. 答え合わせをする**　終わった案件の数字で確かめ、合わない所は直してからお渡しします。数字には「どこから拾ったか」を付け、確かめが必要な所は分けてお知らせします。

      **4. 続けて面倒を見る**　単価の更新や、書類の下書きを続けて引き受けます。
    colors: bg-light-fg-dark
    styles:
      self:
        alignItems: center
        flexDirection: col
        padding:
          - pt-16
          - pl-8
          - pb-16
          - pr-8
        justifyContent: center
  - type: GenericSection
    elementId: about
    title:
      text: 代表より
      color: text-dark
      type: TitleBlock
    text: |-
      私自身、中小企業の社長として長く現場に立ってきました。社長の「痛い」「かゆい」「歯がゆい」は、身をもって知っています。

      不器用でも、できなかったら人の倍やる。それでもできなかったら、さらにその倍やる。
      お客さまの悩みを一つずつ形にし、同じ業種のみなさんの答えにしていきます。
    colors: bg-neutral-fg-dark
    styles:
      self:
        alignItems: center
        flexDirection: col
        padding:
          - pt-16
          - pl-8
          - pb-16
          - pr-8
        justifyContent: center
  - type: GenericSection
    elementId: contact
    title:
      text: ご相談・お問い合わせ
      color: text-dark
      type: TitleBlock
    text: |-
      「こんなことで相談していいのかな」という段階でかまいません。
      内容を拝見し、2営業日以内にメールでご連絡します。
    media:
      fields:
        - name: name
          label: お名前
          placeholder: 山田 太郎
          isRequired: true
          width: 1/2
          type: TextFormControl
        - name: company
          label: 会社名
          placeholder: 株式会社〇〇
          isRequired: false
          width: 1/2
          type: TextFormControl
        - name: email
          label: メールアドレス
          placeholder: you@example.com
          isRequired: true
          width: full
          type: EmailFormControl
        - name: topic
          label: ご相談の種類
          defaultValue: 選んでください
          options:
            - 見積もり・積算
            - 請求・入金の照合
            - 問い合わせ返信・事務の下書き
            - その他
          isRequired: true
          width: full
          type: SelectFormControl
        - name: message
          label: ご相談内容
          placeholder: いま困っていること、時間がかかっている作業などをご自由にお書きください。
          isRequired: true
          width: full
          type: TextareaFormControl
        - name: privacy
          label: プライバシーポリシーに同意します
          isRequired: true
          width: full
          type: CheckboxFormControl
      elementId: contact-form
      styles:
        self:
          padding:
            - pt-6
            - pb-6
            - pl-6
            - pr-6
          borderColor: border-dark
          borderStyle: solid
          borderWidth: 1
          borderRadius: large
      type: FormBlock
      submitButton:
        type: SubmitButtonFormControl
        label: 送信する
        showIcon: false
        icon: arrowRight
        iconPosition: right
        style: primary
        elementId: null
    colors: bg-light-fg-dark
    styles:
      self:
        alignItems: center
        flexDirection: row
        padding:
          - pt-16
          - pl-8
          - pb-16
          - pr-8
seo:
  metaTitle: 合同会社XROSIA｜一社のモヤモヤを、業界みんなの答えに変える。
  metaDescription: 見積もり・請求照合・問い合わせ返信など、中小企業の「毎回めんどう」「ミスが怖い」を使える形にして届けます。まずは無料でご相談ください。
  type: Seo
type: PageLayout
---
