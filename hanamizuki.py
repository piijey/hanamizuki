import pandas as pd

def make_noun_list(file_all, file_noun):
    df = pd.read_excel(file_all, sheet_name='重要度順語彙リスト60894語')
    # カラム名の特殊文字（\n（改行）、\s（スペース）、\(（左カッコ）、\)（右カッコ）、（（全角左カッコ）、）（全角右カッコ））をアンダースコアに置き換える
    df.columns = df.columns.str.replace('[\n\s\(\)（）]', '_', regex=True) 
    #print(df.columns)

    # 名詞だけ・必要なカラムだけを取り出す
    df_nouns = df[df['品詞_Part_of_Speech'].str.startswith('名詞')]
    df_nouns = df_nouns[['見出し語彙素_Lexeme', '標準的_新聞_表記_Standard__Newspaper__Orthography', '標準的読み方_カタカナ__Standard_Reading__Katakana_']]

    # 読みが空または0のとき、下流タスクでは使えないので、df_nounsから取り除く
    df_nouns.dropna(subset=['標準的読み方_カタカナ__Standard_Reading__Katakana_'], inplace=True) # 欠損値を削除する
    df_nouns = df_nouns.query('標準的読み方_カタカナ__Standard_Reading__Katakana_ != 0') # 特定のカラムが0の行を削除する

    # 新しいCSVファイルに書き出す
    df_nouns.to_csv(file_noun, index=False)


def find_hanamizuki(file_noun):
    start_word_length = 5
    df = pd.read_csv(file_noun)
    cn_yomi = '標準的読み方_カタカナ__Standard_Reading__Katakana_'
    cn_midashi = '見出し語彙素_Lexeme'

    # 名詞を読みでまとめ、被検索用 dictionary を作る
    all_words_dict = df.groupby(cn_yomi)[cn_midashi].apply(list).to_dict()

    # 5文字の単語を抽出
    grouped = df[df[cn_yomi].str.len() == start_word_length].groupby(cn_yomi)[cn_midashi].apply(list).reset_index()
    five_letter_words = [{'Yomi': row[cn_yomi], 'Midashi': row[cn_midashi]} for _, row in grouped.iterrows()]

    result = []  # 結果を格納するリスト

    for five_letter_word in five_letter_words:
        word = five_letter_word['Yomi']
        temp_word = word
        is_valid = True
        word_members = [five_letter_word]  # 5文字単語自体を最初に追加

        for _ in range(start_word_length-1):
            temp_word = temp_word[:-1]# 5文字から1文字ずつ減らす
            lexemes = all_words_dict.get(temp_word, None) #単語を検索

            if lexemes:
                member = {'Yomi': temp_word, 'Midashi': lexemes} # 例えば、'Yomi':'アク', 'Midashi':['悪','灰汁']
                word_members.append(member)
            else:
                is_valid = False
                break

        if is_valid:
            result.append({'Word': word, 'Members': word_members[::-1]})  # members は、順番を反転して保存

    result = sorted(result, key=lambda x: x['Word'])  # 結果を五十音順に並べる
    print(f"find_hanamizuki: {len(result)}語を見つけました")
    return result


def show_hanamizuki(result):
    # 結果を見やすい形で表示
    for word in result:
        print(f"\n{word['Word']}")
        for member in word['Members']:
            print(f" {member['Yomi']} ({'、'.join(member['Midashi'])})")


if __name__ == "__main__":
    word_list_file = "database/VDRJ_Ver1_1_Research_Top60894.xlsx"
    noun_list_file = "database/VDRJ_Ver1_1_Research_Top60894.nouns.csv"
    make_noun_list(word_list_file, noun_list_file)
    result = find_hanamizuki(noun_list_file)
    show_hanamizuki(result)

