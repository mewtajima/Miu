import streamlit as st
import pandas as pd
 
st.title("割り勘アプリ")
 
#イベントタイトル
event_title = st.text_input("イベントタイトル（例: 軽井沢旅 2025/10/08）", max_chars=50)
st.write(f"イベント: {event_title}")
 
#メンバー登録
st.subheader("メンバー登録")
if "members" not in st.session_state:
    st.session_state.members = []
new_member = st.text_input("追加したいメンバー名", key="new_member")
if st.button("メンバー追加"):
    if new_member and new_member not in st.session_state.members:
        st.session_state.members.append(new_member)
for m in st.session_state.members:
    st.write(f"- {m}")
 
#支払い登録
st.subheader("支払い登録")
if "payments" not in st.session_state:
    st.session_state.payments = []
if st.session_state.members:
    pay_item = st.text_input("内容（例:夕食）")
    pay_amount = st.number_input("金額", min_value=0, step=1)
    pay_payer = st.selectbox("支払者（誰が払ったか）", options=st.session_state.members)
    pay_participants = st.multiselect("支払いの対象者（割り勘するメンバー）", options=st.session_state.members, default=st.session_state.members)
    pay_memo = st.text_input("メモ（任意）")
    if st.button("支払い追加"):
        st.session_state.payments.append({
            "内容": pay_item,
            "金額": pay_amount,
            "支払者": pay_payer,
            "参加者": ','.join(pay_participants),
            "メモ": pay_memo,
        })
 
if st.session_state.payments:
    df = pd.DataFrame(st.session_state.payments)
    st.write(df)
 
#精算計算
st.subheader("精算結果")
if st.button("精算計算") and st.session_state.payments:
    members = st.session_state.members
    balances = {m: 0 for m in members}
    for pay in st.session_state.payments:
        amt = pay["金額"]
        payer = pay["支払者"]
        participants = pay["参加者"].split(",")
        per_person = amt / len(participants) if participants else 0
        for m in participants:
            balances[m] -= per_person
        balances[payer] += amt
 
    st.write("各メンバーの精算額（プラス=受け取る、マイナス=支払う）:")
    bal_df = pd.DataFrame(list(balances.items()), columns=["メンバー", "精算額"])
    st.write(bal_df)
 
    # シンプルな精算案
    receive = [(k, v) for k, v in balances.items() if v > 0]
    pay = [(k, v) for k, v in balances.items() if v < 0]
    result_msgs = []
    i, j = 0, 0
    receive.sort(key=lambda x: -x[1])
    pay.sort(key=lambda x: x[1])
 
    while i < len(pay) and j < len(receive):
        payer, pay_amt = pay[i]
        receiver, recv_amt = receive[j]
        settle_amt = min(-pay_amt, recv_amt)
        if settle_amt < 1:
            i += 1; continue
        result_msgs.append(f"{payer}は{receiver}に {int(settle_amt)}円 支払う")
        pay[i] = (payer, pay_amt + settle_amt)
        receive[j] = (receiver, recv_amt - settle_amt)
        if pay[i][1] >= 0: i += 1
        if receive[j][1] <= 0: j += 1
 
    if result_msgs:
        for msg in result_msgs: st.write(msg)
    else:
        st.write("精算不要です。")
 
#CSVダウンロード
st.subheader("支払い履歴CSV保存")
if st.session_state.payments:
    csv_data = pd.DataFrame(st.session_state.payments).to_csv(index=False, encoding="utf-8-sig")
    st.download_button("CSVダウンロード", csv_data, "payments.csv", "text/csv")
