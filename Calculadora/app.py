from tkinter import *
from tkinter import ttk


cor1 = "#000000"
cor2 = "#12c8ff"
cor3 = "#bbbcbd"

janela = Tk()
janela.title("Calculadora")
janela.geometry("235x318")
janela.resizable(False, False)
janela.config(bg=cor1)

frame_tela = Frame(janela, width=235, height=50, bg=cor2)
frame_tela.grid(row=0, column=0)

frame_corpo = Frame(janela, width=235, height=268)
frame_corpo.grid(row=1, column=0)

# Craindo Botoes

b_1 = Button(frame_corpo, text="Clean", width=18, height=2, overrelief=RIDGE)
b_1.place(x=0, y=0)

b_2 = Button(frame_corpo, text="%", width=5, height=2, overrelief=RIDGE)
b_2.place(x=140, y=0)

b_3 = Button(frame_corpo, text="/", width=5, height=2, overrelief=RIDGE)
b_3.place(x=190, y=0)

janela.mainloop()
