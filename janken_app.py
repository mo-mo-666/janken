# -*- coding: utf-8 -*-

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from tkinter import filedialog

import random
from datetime import datetime
from PIL import Image, ImageTk
from copy import deepcopy
import csv


ROCK = "グー"
SCISSORS = "チョキ"
PAPER = "パー"
NUMBER = "試合数"
WIN = "勝ち"
EVEN = "あいこ"
LOSE = "負け"
WINRATE = "勝率(あいこを除く)"

BUTTONSTYLE = {'background': '#f7f6eb', 'relief':tk.GROOVE,
               'overrelief':tk.RIDGE, 'activebackground': '#e3cea4'}
BUTTONSIZE = {'height':1, 'width':10}
# ttk.Buttonのスタイルが上手く働かないので，ボタンだけはtk.Buttonを使うことにする。


class ParamCal():

    def __init__(self):
        self.reset_params()
        self.reset_results()

    def reset_params(self):
        self.win_param = 100
        self.even_param = 100
        self.lose_param = 100
        self.params_are_initial = True

    def reset_results(self):
        self.result_counter = {NUMBER: 0, WIN: 0, EVEN: 0, LOSE: 0, WINRATE: 0}
        self.result_recorder = [['n', 'Time', 'YOU', 'COM', 'R',
                            'WIN', 'EVEN', 'LOSE', 'W_r','W_p','E_p', 'L_p' ]]

    def update_params(self, win_param, even_param, lose_param):
        self.win_param = win_param
        self.even_param = even_param
        self.lose_param = lose_param

    def update_results(self, hand, com_hand, result):
        self.result_counter[NUMBER] += 1
        self.result_counter[result] += 1
        if self.result_counter[WIN] + self.result_counter[LOSE] > 0:
            self.result_counter[WINRATE] = self.result_counter[WIN] / (self.result_counter[WIN]+self.result_counter[LOSE])
        record = [self.result_counter[NUMBER],
                  datetime.now(),
                  hand,
                  com_hand,
                  result,
                  self.result_counter[WIN],
                  self.result_counter[EVEN],
                  self.result_counter[LOSE],
                  self.result_counter[WINRATE],
                  self.win_param,
                  self.even_param,  # 正規化はしていない
                  self.lose_param]
        self.result_recorder.append(record)

    def hand_calculate(self, hand):
        if hand == ROCK:
            win_hand, lose_hand = SCISSORS, PAPER
        elif hand == SCISSORS:
            win_hand, lose_hand = PAPER, ROCK
        elif hand == PAPER:
            win_hand, lose_hand = ROCK, SCISSORS
        else:
            raise ValueError

        resultdic = {win_hand: WIN, hand: EVEN, lose_hand: LOSE}
        com_hand = random.choices([win_hand, hand, lose_hand],
                                  weights=[self.win_param, self.even_param, self.lose_param])[0]
        self.update_results(hand, com_hand, resultdic[com_hand])  # 結果の更新
        return com_hand


param_instance = ParamCal()


class Janken(ttk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.pack(padx=10, pady=10)
        self.createwidgets()

    ### ウィジェットを作る関数
    def createwidgets(self):
        self.frame1 = ttk.Frame(self)
        self.createcanvas(self.frame1)
        self.frame1.grid(row=0, column=0, padx=10, pady=10)
        self.frame2 = ttk.Frame(self)
        self.createbuttons(self.frame2)
        self.frame2.grid(row=1, column=0, padx=10, pady=10)
        self.frame3 = ttk.Frame(self)
        self.createrecordform(self.frame3)
        self.frame3.grid(row=0, column=1, padx=10, pady=10)
        self.frame4 = ttk.Frame(self)
        self.createoption(self.frame4)
        self.frame4.grid(row=1, column=1, padx=10, pady=10)

    def createbuttons(self, frame):
        """手のボタン部分を作る"""
        rock_button_png = Image.open(r'./icons/rock_button.png')
        scissors_button_png = Image.open(r'./icons/scissors_button.png')
        paper_button_png = Image.open(r'./icons/paper_button.png')

        self.rock_button_image = ImageTk.PhotoImage(rock_button_png)
        self.scissors_button_image = ImageTk.PhotoImage(scissors_button_png)
        self.paper_button_image = ImageTk.PhotoImage(paper_button_png)

        self.rockbutton = tk.Button(frame, image=self.rock_button_image, command=self.rock_calculate, **BUTTONSTYLE)
        self.scissorsbutton = tk.Button(frame, image=self.scissors_button_image, command=self.scissors_calculate, **BUTTONSTYLE)
        self.paperbutton = tk.Button(frame, image=self.paper_button_image, command=self.paper_calculate, **BUTTONSTYLE)

        self.rockbutton.grid(row=0, column=0, padx=15)
        self.scissorsbutton.grid(row=0, column=1, padx=15)
        self.paperbutton.grid(row=0, column=2, padx=15)


    def createoption(self, frame):
        """オプション部分を作る"""
        self.settingbutton = tk.Button(frame, text='設定', command=self.option, **BUTTONSTYLE, **BUTTONSIZE)
        self.resetbutton = tk.Button(frame, text='リセット', command=self.reset, **BUTTONSTYLE, **BUTTONSIZE)
        self.savebutton = tk.Button(frame, text='結果を保存', command=self.save, **BUTTONSTYLE, **BUTTONSIZE)

        self.settingbutton.grid(row=0, column=0, columnspan=2, padx=10)
        self.resetbutton.grid(row=1, column=0, padx=10, pady=10)
        self.savebutton.grid(row=1, column=1, padx=10, pady=10)

    def createcanvas(self, frame):
        """COMの手を出す部分"""
        title_png = Image.open(r'./icons/title.png')
        rock_png = Image.open(r'./icons/rock.png')
        scissors_png = Image.open(r'./icons/scissors.png')
        paper_png = Image.open(r'./icons/paper.png')
        self.title_image = ImageTk.PhotoImage(title_png)
        self.rock_image = ImageTk.PhotoImage(rock_png)
        self.scissors_image = ImageTk.PhotoImage(scissors_png)
        self.paper_image = ImageTk.PhotoImage(paper_png)
        self.hand_images = {ROCK: self.rock_image, SCISSORS: self.scissors_image, PAPER: self.paper_image}

        self.canvas = tk.Canvas(frame, background='white', width=600, height=400)
        self.canvas.create_image(300, 200, image=self.title_image)
        self.canvas.pack()

    def createrecordform(self, frame):
        """結果を記録する表の部分を作る"""
        self.textexp = ttk.Label(frame, text='結果')
        self.field = ttk.Treeview(frame, columns=(0,1,2,3,4,5,6,7,8,9,10,11), height=13, show='headings', selectmode='none')
        # 表のheadingと幅を設定
        for i, j in enumerate([15,50,35,35,15,35,35,35,35,35,35,35]):
            self.field.column(i, width=j)
            self.field.heading(i, text=param_instance.result_recorder[0][i])
        self.fieldscroll = ttk.Scrollbar(frame, command=self.field.yview)
        self.field.configure(yscrollcommand=self.fieldscroll.set)
        self.result_rate = ttk.Label(frame, text='*'*30+ '  集計  ' +'*'*30)
        self.result_win = ttk.Label(frame, text=WIN)
        self.result_winn = ttk.Label(frame, text=param_instance.result_counter[WIN])
        self.result_even = ttk.Label(frame, text=EVEN)
        self.result_evenn = ttk.Label(frame, text=param_instance.result_counter[EVEN])
        self.result_lose = ttk.Label(frame, text=LOSE)
        self.result_losen = ttk.Label(frame, text=param_instance.result_counter[LOSE])
        self.result_winrate = ttk.Label(frame, text=WINRATE)
        self.result_winraten = ttk.Label(frame, text='{:.2f}%'.format(param_instance.result_counter[WINRATE]*100))

        self.textexp.grid(row=0, column=0, columnspan=3)
        self.field.grid(row=1, column=0, columnspan=3)
        self.fieldscroll.grid(row=1, column=3, sticky=tk.N+tk.S)
        self.result_rate.grid(row=2, column=0, columnspan=3)
        self.result_win.grid(row=3, column=0)
        self.result_winn.grid(row=4, column=0)
        self.result_even.grid(row=3, column=1)
        self.result_evenn.grid(row=4, column=1)
        self.result_lose.grid(row=3, column=2)
        self.result_losen.grid(row=4, column=2)
        self.result_winrate.grid(row=5, column=0, columnspan=3)
        self.result_winraten.grid(row=6, column=0, columnspan=3)

    def option(self):
        """オプションポップアップメニューを表示"""
        self.app2 =  OptionWindow()

    def reset(self):
        """全ての結果，パラメータをリセット"""
        global param_insance
        param_instance.reset_params()
        param_instance.reset_results()
        self.createwidgets()

    def react_animation(self, com_hand):
        """ボタンを押すことによるUIの更新"""
        # キャンバス(frame1)の更新
        self.canvas.delete('all')
        self.canvas.create_image(300, 200, image=self.hand_images[com_hand])

        # 結果表示(frame3)の更新
        self.result_winn.configure(text=param_instance.result_counter[WIN])
        self.result_evenn.configure(text=param_instance.result_counter[EVEN])
        self.result_losen.configure(text=param_instance.result_counter[LOSE])
        self.result_winraten.configure(text='{:.2f}%'.format(param_instance.result_counter[WINRATE]*100))
        self.columnwrite()

    def columnwrite(self):
        """表の更新"""
        r = deepcopy(param_instance.result_recorder[-1])
        r[1] = r[1].strftime('%H:%M:%S')
        r[4] = {WIN: '○', EVEN: '△', LOSE: '×'}[r[4]]
        r[8] = '{:.1f}'.format(r[8]*100)
        self.field.insert("", "end", values=r, iid=r[0])
        self.field.see(r[0])

    def save(self):
        """結果をファイルに書き出し"""
        filename = filedialog.asksaveasfilename(defaultextension='.csv',
                 filetypes=[("CSVファイル",".csv" ), ("すべてのファイル", ".*")],
                 initialfile='JankenRecord.csv')
        with open(filename, 'w', newline='') as csvfile:
            record_writer = csv.writer(csvfile)
            record_writer.writerow(['じゃんけんゲーム♪'])
            record_writer.writerow(['保存日時', datetime.now()] )
            record_writer.writerows(param_instance.result_recorder)

    ### 以下計算系の関数
    def rock_calculate(self):
        com_hand = param_instance.hand_calculate(ROCK)
        self.react_animation(com_hand)

    def scissors_calculate(self):
        com_hand = param_instance.hand_calculate(SCISSORS)
        self.react_animation(com_hand)

    def paper_calculate(self):
        com_hand = param_instance.hand_calculate(PAPER)
        self.react_animation(com_hand)


class OptionWindow():

    def __init__(self):
        self.root = tk.Toplevel(padx=5, pady=5, background='#fffbf7') # ←Tkでなく，Toplevelを使うことでメインウィンドウと連動できる(メインを閉じれば同時に閉じる)
        self.root.title('設定')
        self.calc = self.root.register(self.custom_caliculate)
        self.createwidgets()
        self.root.bind('<Return>', func=self.set_params) # Enterキーを推したらOK扱い
        self.root.bind('<Escape>', func=self.cancel)
        self.root.focus_set()  # フォーカスウィンドウ（今操作中のウィンドウ）にする
        self.root.resizable(False, False) # サイズ変更の禁止
        self.root.grab_set()   # モーダルダイアログ

    def createwidgets(self):
        win_param = param_instance.win_param
        even_param = param_instance.even_param
        lose_param = param_instance.lose_param

        self.val = tk.BooleanVar()
        self.val.set(param_instance.params_are_initial)
        self.button1 = ttk.Radiobutton(self.root, text='標準(ランダム)', value=True, variable=self.val, command=self.custom_disabled)
        self.button2 = ttk.Radiobutton(self.root, text='カスタマイズ', value=False, variable=self.val, command=self.custom_activate)
        self.experience = ttk.Label(self.root, text='自分の勝率を比率でカスタマイズします。整数値で入力してください。')
        self.win_l = ttk.Label(self.root, text=WIN)
        self.even_l = ttk.Label(self.root, text=EVEN)
        self.lose_l = ttk.Label(self.root, text=LOSE)
        self.win_e = ttk.Entry(self.root, width=18, validate='focusout', cursor='xterm', validatecommand=self.calc)
        self.win_e.insert(tk.END, win_param)
        self.even_e = ttk.Entry(self.root, width=18, validate='focusout', cursor='xterm', validatecommand=self.calc)
        self.even_e.insert(tk.END, even_param)
        self.lose_e = ttk.Entry(self.root, width=18, validate='focusout', cursor='xterm', validatecommand=self.calc)
        self.lose_e.insert(tk.END, lose_param)
        self.win_p = ttk.Label(self.root,
                text='{:.1f}%'.format(win_param/(win_param+even_param+lose_param)*100))
        self.even_p = ttk.Label(self.root,
                text='{:.1f}%'.format(even_param/(win_param+even_param+lose_param)*100))
        self.lose_p = ttk.Label(self.root,
                text='{:.1f}%'.format(lose_param/(win_param+even_param+lose_param)*100))

        if win_param == 0:
            win_r = 0
        else:
            win_r = win_param / (win_param+lose_param)
        self.win_r = ttk.Label(self.root,text='あいこを除いた勝率: {:.2f}%'.format(win_r*100))

        self.okbutton = tk.Button(self.root, text='OK', command=self.set_params, **BUTTONSTYLE, **BUTTONSIZE)
        self.cancelbutton = tk.Button(self.root, text='キャンセル', command=self.cancel, **BUTTONSTYLE, **BUTTONSIZE)

        self.button1.grid(row=0, column=0, columnspan=3, sticky=tk.W)
        self.button2.grid(row=1, column=0, columnspan=3, sticky=tk.W)
        self.experience.grid(row=2, column=0, columnspan=3)
        self.win_l.grid(row=3, column=0)
        self.even_l.grid(row=3, column=1)
        self.lose_l.grid(row=3, column=2)
        self.win_e.grid(row=4, column=0)
        self.even_e.grid(row=4, column=1)
        self.lose_e.grid(row=4, column=2)
        self.win_p.grid(row=5, column=0)
        self.even_p.grid(row=5, column=1)
        self.lose_p.grid(row=5, column=2)
        self.win_r.grid(row=6, column=0, columnspan=3)
        self.okbutton.grid(row=7, column=1)
        self.cancelbutton.grid(row=7, column=2)

        if self.val.get():
            self.custom_disabled()

    def custom_activate(self):
        """ラジオボタンでカスタムを選んだ時の挙動"""
        self.experience.configure(state=tk.NORMAL)
        self.win_l.configure(state=tk.NORMAL)
        self.even_l.configure(state=tk.NORMAL)
        self.lose_l.configure(state=tk.NORMAL)
        self.win_e.configure(state=tk.NORMAL, cursor='xterm')
        self.even_e.configure(state=tk.NORMAL, cursor='xterm')
        self.lose_e.configure(state=tk.NORMAL, cursor='xterm')
        self.win_p.configure(state=tk.NORMAL)
        self.even_p.configure(state=tk.NORMAL)
        self.lose_p.configure(state=tk.NORMAL)
        self.win_r.configure(state=tk.NORMAL)

    def custom_disabled(self):
        """ラジオボタンで標準を選んだ時の挙動"""
        self.experience.configure(state=tk.DISABLED)
        self.win_l.configure(state=tk.DISABLED)
        self.even_l.configure(state=tk.DISABLED)
        self.lose_l.configure(state=tk.DISABLED)
        self.win_e.configure(state=tk.DISABLED, cursor='')
        self.even_e.configure(state=tk.DISABLED, cursor='')
        self.lose_e.configure(state=tk.DISABLED, cursor='')
        self.win_p.configure(state=tk.DISABLED)
        self.even_p.configure(state=tk.DISABLED)
        self.lose_p.configure(state=tk.DISABLED)
        self.win_r.configure(state=tk.DISABLED)

    def custom_caliculate(self):
        """フォームに数字を入力したときに対話的に勝率を表示"""
        try:
            assert int(self.win_e.get()) >= 0 and int(self.even_e.get()) >= 0 and int(self.lose_e.get()) >= 0
            if int(self.win_e.get())+int(self.even_e.get())+int(self.lose_e.get()) > 0:

                win_param = int(self.win_e.get())
                even_param = int(self.even_e.get())
                lose_param = int(self.lose_e.get())
                self.win_p.configure(text='{:.1f}%'.format(win_param/(win_param+even_param+lose_param)*100))
                self.even_p.configure(text='{:.1f}%'.format(even_param/(win_param+even_param+lose_param)*100))
                self.lose_p.configure(text='{:.1f}%'.format(lose_param/(win_param+even_param+lose_param)*100))
                if win_param == 0:
                    self.win_r.configure(text='あいこを除いた勝率: {:.2f}%'.format(0))
                else:
                    self.win_r.configure(text='あいこを除いた勝率: {:.2f}%'.format(win_param/(win_param+lose_param)*100))
            else:
                self.win_p.configure(text='{:.1f}%'.format(0))
                self.even_p.configure(text='{:.1f}%'.format(0))
                self.lose_p.configure(text='{:.1f}%'.format(0))
                self.win_r.configure(text='あいこを除いた勝率: {:.2f}%'.format(0))
            return True

        except:
            return False

    def set_params(self, event=None):  # event引数は，'<Return>'により閉じたときに渡される。
        """OKボタンを押したときの挙動"""
        global param_instance

        if  self.val.get():
            param_instance.reset_params()
            self.root.destroy()
        else:
            try:
                assert int(self.win_e.get()) >= 0 and int(self.even_e.get()) >= 0 and int(self.lose_e.get()) >= 0
                assert int(self.win_e.get())+int(self.even_e.get())+int(self.lose_e.get()) > 0
                param_instance.params_are_initial = False
                win_param = int(self.win_e.get())
                even_param = int(self.even_e.get())
                lose_param = int(self.lose_e.get())
                param_instance.update_params(win_param, even_param, lose_param)
                self.root.destroy()
            except:
                messagebox.showerror('Error', '入力フォームには合計が正になる非負整数を入力してください。')

    def cancel(self, event=None):   # event引数は，'<Escape>'により閉じたときに渡される。
        """キャンセルボタンを押したときの挙動""" # <KeyPress event keysym=Escape keycode=27 char='\x1b' x=281 y=38> ←event引数にはこんなのが渡される
        self.root.destroy()         # destroyだと消す。withdrawだと隠すだけ


def main():
    root = tk.Tk()
    root.title('じゃんけんゲーム！')
    root.configure(background='#fffbf7')
    ttk.Style().configure('.', background='#fffbf7')    # スタイルの変更
        # 本来はbuttonもttk.Buttonを使うべきだが，それだとなぜかbackgroundが変化しないので，
        # tk.Buttonを使っている。同じような疑問がネット上にも多くあった。

    root.resizable(False, False) # サイズ変更の禁止
    app = Janken(root)
    app.mainloop()


if __name__ == '__main__':
    main()
