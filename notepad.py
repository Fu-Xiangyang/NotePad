from tkinter import *
from tkinter import filedialog, messagebox
from tkinter.ttk import Scrollbar, Checkbutton, Label, Button
import os
import sys


class NotePad(Tk):
    icons = ['new_file', 'open_file', 'save', 'cut',
             'copy', 'paste', 'undo', 'redo', 'find_text']
    icon_res = []
    theme_color = {'Default': '#000000.#FFFFFF',
                   'Olive Green': '#D1E7E0.#5B8340',
                   'Night Mode': '#FFFFFF.#000000'}

    # 初始化
    def __init__(self):
        super().__init__()
        self.theme_choice = None
        self.line_num_bar = None
        self.is_show_line_num = None
        self.is_highlight_line = None
        self.context_text = None
        self.file_name = None
        self.set_window()
        self.create_menu_bar()
        self.create_tool_bar()
        self.create_body()
        self.create_pop_menu()

    # 设置窗口界面
    def set_window(self):
        self.title("NotePad")
        max_width, max_height = self.maxsize()
        align_center = "800x600+%d+%d" % ((max_width - 800) / 2, (max_height - 600) / 2)
        self.geometry(align_center)
        self.iconbitmap("img/editor.ico")

    # 创建菜单项目
    def create_menu_bar(self):
        menu_bar = Menu(self)

        # 添加菜单项目
        file_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label='文件', menu=file_menu)
        file_menu.add_command(label='新建', accelerator='Ctrl+N', command=self.new_file)
        file_menu.add_command(label='打开', accelerator='Ctrl+O', command=self.open_file)
        file_menu.add_command(label='保存', accelerator='Ctrl+S', command=self.save_file)
        file_menu.add_command(label='另存为', accelerator='Ctrl+Shift+S', command=self.save_as)
        file_menu.add_separator()
        file_menu.add_command(label='退出', accelerator='Alt+F4', command=self.exit_notepad)

        edit_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label='编辑', menu=edit_menu)
        edit_menu.add_command(label='撤销', accelerator='Ctrl+Z',
                              command=lambda: self.handle_menu_action('撤销'))
        edit_menu.add_command(label='恢复', accelerator='Ctrl+Y',
                              command=lambda: self.handle_menu_action('恢复'))
        edit_menu.add_separator()
        edit_menu.add_command(label='剪切', accelerator='Ctrl+X',
                              command=lambda: self.handle_menu_action('剪切'))
        edit_menu.add_command(label='复制', accelerator='Ctrl+C',
                              command=lambda: self.handle_menu_action('复制'))
        edit_menu.add_command(label='粘贴', accelerator='Ctrl+V',
                              command=lambda: self.handle_menu_action('粘贴'))
        edit_menu.add_command(label='全选', accelerator='Ctrl+A',
                              command=self.seclect_all)
        edit_menu.add_separator()
        edit_menu.add_command(label='查找', accelerator='Ctrl+F',
                              command=self.find_text_dialog)

        view_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label='视图', menu=view_menu)
        # 显示行号
        self.is_show_line_num = IntVar()
        self.is_show_line_num.set(1)
        view_menu.add_checkbutton(label='显示行号',
                                  onvalue=1, offvalue=0,
                                  variable=self.is_show_line_num,
                                  command=self.update_line_num)
        # 高亮当前行
        self.is_highlight_line = IntVar()
        view_menu.add_checkbutton(label='高亮当前行',
                                  onvalue=1, offvalue=0,
                                  variable=self.is_highlight_line,
                                  command=self.toggle_highlight)
        view_menu.add_separator()
        # 主题
        themes_menu = Menu(menu_bar, tearoff=0)
        view_menu.add_cascade(label='主题', menu=themes_menu)
        self.theme_choice = StringVar()
        self.theme_choice.set('Default')
        for k in sorted(self.theme_color):
            themes_menu.add_radiobutton(label=k, variable=self.theme_choice,
                                        command=self.change_theme)
        # 关于
        about_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label='关于', menu=about_menu)
        about_menu.add_command(label='关于', command='')
        about_menu.add_command(label='帮助', command='')

        self['menu'] = menu_bar

    # 创建工具栏
    def create_tool_bar(self):
        tool_bar = Frame(self, height=25, background='#FFFFFF')
        # 填充x轴
        tool_bar.pack(fill='x')
        for icon in self.icons:
            tool_icon = PhotoImage(file=f"img/{icon}.gif")
            tool_btn = Button(tool_bar, image=tool_icon,
                              command=self.tool_bar_action(icon))
            tool_btn.pack(side='left')
            # 要将tool_icon添加到icon_res
            self.icon_res.append(tool_icon)

    # 界面操作的主体
    def create_body(self):
        # 左边行号 中间文本编辑区 右边滚动条
        # 行号
        self.line_num_bar = Text(self, width=4, padx=3, takefocus=0,
                                 border=0, background='#F0E68C', state='disabled')

        self.line_num_bar.pack(side='left', fill='y')

        # 文本编辑区
        # wrap: 换行方式, word表示按照单词自动换行
        # undo: 表示是否开启撤销功能
        self.context_text = Text(self, wrap='word', undo=True)
        self.context_text.pack(fill='both', expand=1)

        # 热键的绑定
        self.context_text.bind('<Control-o>', self.open_file)
        self.context_text.bind('<Control-O>', self.open_file)
        self.context_text.bind('<Control-s>', self.save_file)
        self.context_text.bind('<Control-S>', self.save_file)
        self.context_text.bind('<Control-n>', self.new_file)
        self.context_text.bind('<Control-N>', self.new_file)
        self.context_text.bind('<Control-f>', self.find_text_dialog)
        self.context_text.bind('<Control-F>', self.find_text_dialog)
        self.context_text.bind('<Control-Shift-s>', self.save_as)
        self.context_text.bind('<Control-Shift-S>', self.save_as)
        self.context_text.bind('<Any-KeyPress>', lambda e: self.update_line_num())

        # 设置文本输入区
        self.context_text.tag_config('active_line', background="#EEEEE0")

        # 滚动条
        scroll_bar = Scrollbar(self.context_text)
        scroll_bar['command'] = self.context_text.yview
        self.context_text['yscrollcommand'] = scroll_bar.set
        scroll_bar.pack(side='right', fill='y')

    # 打开文件
    def open_file(self, event=None):
        # 打开文件并进行类型设置
        input_file = filedialog.askopenfilename(filetypes=[('所有文件', '*.*'),
                                                           ('文本文档', '*.txt')])

        if input_file:
            self.title("{}***NotePad".format(os.path.basename(input_file)))
            self.file_name = input_file
            self.context_text.delete(1.0, END)
            with open(input_file, 'r') as _file:
                self.context_text.insert(1.0, _file.read())

    # 保存文件
    def write_to_file(self, file_name):
        try:
            content = self.context_text.get(1.0, END)
            with open(file_name, 'w') as _file:
                _file.write(content)
            self.title("{}---NotePad".format(os.path.basename(file_name)))
        except IOError:
            messagebox.showerror('错误', '文件保存失败！')

    def save_file(self, event=None):
        if not self.file_name:
            self.save_as()
        else:
            self.write_to_file(self.file_name)

    # 新建文件
    def new_file(self, event=None):
        self.title('新建---NotePad')
        self.context_text.delete(1.0, END)
        self.file_name = None

    # 另存为
    def save_as(self, event=None):
        input_file = filedialog.asksaveasfilename(filetypes=[('所有文件', '*.*'),
                                                             ('文本文档', '*.txt')])
        if input_file:
            self.file_name = input_file
            self.write_to_file(self.file_name)

    # 退出
    def exit_notepad(self):
        if messagebox.askokcancel("退出", "确定退出吗？"):
            self.destroy()

    # 右键菜单
    def create_pop_menu(self):
        pop_menu = Menu(self.context_text, tearoff=0)
        for item1, item2 in zip(['剪切', '复制', '粘贴', '撤销', '恢复'],
                                ['cut', 'copy', 'paste', 'undo', 'redo']):
            pop_menu.add_command(label=item1, compound='left',
                                 command=self.tool_bar_action(item2))

        pop_menu.add_separator()
        pop_menu.add_command(label='全选', command=self.seclect_all)
        # 绑定
        self.context_text.bind('<Button-3>',
                               lambda event: pop_menu.tk_popup(event.x_root,
                                                               event.y_root))

    # 右键菜单的处理
    def handle_menu_action(self, action_type):
        if action_type == '撤销':
            self.context_text.event_generate('<<Undo>>')
        elif action_type == '恢复':
            self.context_text.event_generate('<<Redo>>')
        elif action_type == '剪切':
            self.context_text.event_generate('<<Cut>>')
        elif action_type == '复制':
            self.context_text.event_generate('<<Copy>>')
        elif action_type == '粘贴':
            self.context_text.event_generate('<<Paste>>')

        # 防止事件传递
        return 'break'

    # 工具栏命令处理
    def tool_bar_action(self, action_type):
        def handle():
            if action_type == 'open_file':
                self.open_file()
            elif action_type == 'save':
                self.save_file()
            elif action_type == 'new_file':
                self.new_file()
            elif action_type == 'cut':
                self.handle_menu_action('剪切')
            elif action_type == 'copy':
                self.handle_menu_action('复制')
            elif action_type == 'paste':
                self.handle_menu_action('粘贴')
            elif action_type == 'undo':
                self.handle_menu_action('撤销')
            elif action_type == 'redo':
                self.handle_menu_action('恢复')
            elif action_type == 'find_text':
                self.find_text_dialog()

        # 返回handle
        return handle

    # 全选
    def seclect_all(self):
        self.context_text.tag_add('sel', 1.0, END)
        return 'break'

    # 行号处理
    def update_line_num(self):
        if self.is_show_line_num.get():
            # 获取所有行
            row, col = self.context_text.index(END).split('.')
            # 列举每行的行号
            line_num_content = "\n".join([str(i) for i in range(1, int(row))])
            self.line_num_bar.config(state='normal')
            self.line_num_bar.delete(1.0, END)
            self.line_num_bar.insert(1.0, line_num_content)
            self.line_num_bar.config(state='disabled')
        else:
            self.line_num_bar.config(state='normal')
            self.line_num_bar.delete(1.0, END)
            self.line_num_bar.config(state='disabled')

    # 高亮当前行
    def toggle_highlight(self):
        if self.is_highlight_line.get():
            self.context_text.tag_remove('active_line', 1.0, END)
            # 设置高亮
            self.context_text.tag_add('active_line',
                                      'insert linestart',
                                      'insert lineend+1c')
            # 通过轮询递归的方式进行处理
            self.context_text.after(200, self.toggle_highlight)
        else:
            self.context_text.tag_remove('active_line', 1.0, END)

    # 设置查找对话框
    def find_text_dialog(self):
        search_dialog = Toplevel(self)
        search_dialog.title('查找文本')
        max_width, max_height = self.maxsize()
        align_center = "300x80+%d+%d" % ((max_width - 300) / 2, (max_height - 80) / 2)
        search_dialog.geometry(align_center)
        search_dialog.resizable(False, False)
        Label(search_dialog, text='查找全部').grid(row=0, column=0, sticky='e')
        search_text = Entry(search_dialog, width=25)
        search_text.grid(row=0, column=1, padx=2, pady=2, sticky='we')
        search_text.focus_set()
        # 忽略大小写
        ignore_case_value = IntVar()
        Checkbutton(search_dialog, text='忽略大小写',
                    variable=ignore_case_value).grid(row=1, column=1,
                                                     sticky='e',
                                                     padx=2, pady=2)
        Button(search_dialog, text='查找',
               command=lambda: self.search_result(search_text.get(),
                                                  ignore_case_value.get(),
                                                  search_dialog,
                                                  search_text)).grid(row=0, column=2, sticky='we', padx=2, pady=2)

        def close_search_dialog():
            self.context_text.tag_remove('match', 1.0, END)
            search_dialog.destroy()

        search_dialog.protocol('WM_DELETE_WINDOW', close_search_dialog)
        return 'break'

    # 查找方法
    def search_result(self, key, ignore_case, search_dialog, search_box):
        self.context_text.tag_remove('match', 1.0, END)
        matches_found = 0
        if key:
            start_pos = 1.0
            while True:
                start_pos = self.context_text.search(key, start_pos,
                                                     nocase=ignore_case,
                                                     stopindex=END)
                if not start_pos:
                    break
                end_pos = '{}+{}c'.format(start_pos, len(key))
                self.context_text.tag_add('match', start_pos, end_pos)
                matches_found += 1
                start_pos = end_pos
            self.context_text.tag_config('match', foreground='red', background='yellow')
        search_box.focus_set()
        search_dialog.title(f'发现了{matches_found}个匹配的')

    # 主题的切换
    def change_theme(self):
        selected_theme = self.theme_choice.get()
        fg_bg = self.theme_color.get(selected_theme)
        fg_color, bg_color = fg_bg.split('.')
        self.context_text.config(bg=bg_color, fg=fg_color)


if __name__ == '__main__':
    app = NotePad()
    app.mainloop()
