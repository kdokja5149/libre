import tkinter
import json
import os
import subprocess
import sys
from tkinter import *
from tkinter import ttk, messagebox, filedialog, Scrollbar, Text
from PIL import Image, ImageTk

DATA_FILE = "library.json"

class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Электронная библиотека")
        self.root.geometry("1200x700")
        self.root.configure(bg="#8B5A2B")  # коричневый фон главного окна

        self.books = []
        self.load_data()

        self.create_widgets()
        self.refresh_table()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                self.books = json.load(f)
        else:
            self.books = []

    def save_data(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.books, f, indent=4, ensure_ascii=False)

    def create_widgets(self):
        # Стиль для Treeview (чтобы изменить цвет фона таблицы)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#D2B48C", fieldbackground="#D2B48C", foreground="black")
        style.configure("Treeview.Heading", background="#A0522D", foreground="white", font=("Arial", 10, "bold"))

        main_panel = PanedWindow(self.root, orient=HORIZONTAL, sashrelief=RAISED, sashwidth=5, bg="#8B5A2B")
        main_panel.pack(fill=BOTH, expand=True, padx=10, pady=5)

        # Левая панель
        left_frame = Frame(main_panel, bg="#A0522D")  # тёмно-коричневый
        main_panel.add(left_frame, width=750)

        # Поиск
        search_frame = Frame(left_frame, bg="#A0522D")
        search_frame.pack(fill=X, pady=5)
        Label(search_frame, text="Поиск:", bg="#A0522D", fg="white", font=("Arial", 10)).pack(side=LEFT)
        self.search_entry = Entry(search_frame, bg="#D2B48C", fg="black", font=("Arial", 10))
        self.search_entry.pack(side=LEFT, fill=X, expand=True, padx=5)
        Button(search_frame, text="Найти", command=self.search_books, bg="#D2691E", fg="white", font=("Arial", 10)).pack(side=LEFT)

        # Таблица Treeview
        self.tree = ttk.Treeview(left_frame, columns=("ID", "Название", "Автор", "Год", "Жанр"), show="headings")
        self.tree.heading("ID", text="ID", command=lambda: self.sort_by_column("ID", False))
        self.tree.heading("Название", text="Название", command=lambda: self.sort_by_column("Название", False))
        self.tree.heading("Автор", text="Автор", command=lambda: self.sort_by_column("Автор", False))
        self.tree.heading("Год", text="Год", command=lambda: self.sort_by_column("Год", False))
        self.tree.heading("Жанр", text="Жанр", command=lambda: self.sort_by_column("Жанр", False))
        self.tree.column("ID", width=50)
        self.tree.column("Название", width=200)
        self.tree.column("Автор", width=150)
        self.tree.column("Год", width=80)
        self.tree.column("Жанр", width=150)
        self.tree.pack(fill=BOTH, expand=True)

        # Кнопки действий
        btn_frame = Frame(left_frame, bg="#A0522D")
        btn_frame.pack(fill=X, pady=5)
        Button(btn_frame, text="Добавить книгу", command=self.add_book_window, bg="#D2691E", fg="white", font=("Arial", 10)).pack(side=LEFT, padx=5)
        Button(btn_frame, text="Удалить выбранную", command=self.delete_book, bg="#D2691E", fg="white", font=("Arial", 10)).pack(side=LEFT, padx=5)
        Button(btn_frame, text="Обновить список", command=self.refresh_table, bg="#D2691E", fg="white", font=("Arial", 10)).pack(side=LEFT, padx=5)

        # Привязка событий
        self.tree.bind("<Double-1>", self.open_book_file)
        self.tree.bind("<<TreeviewSelect>>", self.on_select_book)

        # Правая панель
        right_frame = Frame(main_panel, width=380, relief=SUNKEN, bd=2, bg="#A0522D")
        main_panel.add(right_frame)

        self.cover_label = Label(right_frame, bg="#D2B48C", relief=RIDGE, bd=3)
        self.cover_label.pack(pady=15, padx=15, fill=BOTH, expand=True)

        self.info_text = Text(right_frame, width=40, height=12, wrap=WORD, state=DISABLED, font=("Arial", 10), bg="#D2B48C", fg="black")
        self.info_text.pack(fill=BOTH, expand=True, padx=15, pady=10)

    def refresh_table(self, books_to_show=None):
        for row in self.tree.get_children():
            self.tree.delete(row)

        data = books_to_show if books_to_show is not None else self.books
        for book in data:
            self.tree.insert("", END, values=(
                book.get("id", ""),
                book.get("title", ""),
                book.get("author", ""),
                book.get("year", ""),
                book.get("genre", "")
            ))

    def search_books(self):
        keyword = self.search_entry.get().strip().lower()
        if not keyword:
            self.refresh_table()
            return
        filtered = [book for book in self.books
                    if keyword in book.get("title", "").lower() or keyword in book.get("author", "").lower()]
        self.refresh_table(filtered)

    def sort_by_column(self, col, reverse):
        if col == "Год":
            self.books.sort(key=lambda x: x.get("year", 0), reverse=reverse)
        elif col == "ID":
            self.books.sort(key=lambda x: x.get("id", 0), reverse=reverse)
        else:
            self.books.sort(key=lambda x: x.get(col.lower(), ""), reverse=reverse)
        self.refresh_table()
        self.tree.heading(col, command=lambda: self.sort_by_column(col, not reverse))

    def on_select_book(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        item = self.tree.item(selected[0])
        book_id = item['values'][0]
        for book in self.books:
            if book.get("id") == book_id:
                self.display_book_info(book)
                break

    def display_book_info(self, book):
        self.info_text.configure(state=NORMAL)
        self.info_text.delete(1.0, END)
        info = f"Название: {book.get('title', '')}\n"
        info += f"Автор: {book.get('author', '')}\n"
        info += f"Год: {book.get('year', '')}\n"
        info += f"Жанр: {book.get('genre', '')}\n"
        info += f"Файл: {os.path.basename(book.get('file_path', ''))}\n"
        self.info_text.insert(END, info)
        self.info_text.configure(state=DISABLED)

        cover_path = book.get('cover_path')
        if cover_path and os.path.exists(cover_path):
            try:
                img = Image.open(cover_path)
                img.thumbnail((350, 350), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.cover_label.config(image=photo, text="")
                self.cover_label.image = photo
            except Exception as e:
                self.cover_label.config(image='', text=f"Ошибка загрузки\n{str(e)}")
        else:
            self.cover_label.config(image='', text="Нет обложки")

    def open_book_as_text(self, file_path, title):
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("Ошибка", "Файл не найден!")
            return
        if not file_path.lower().endswith('.txt'):
            if os.name == 'nt':
                os.startfile(file_path)
            else:
                if sys.platform == "darwin":
                    subprocess.run(["open", file_path])
                else:
                    subprocess.run(["xdg-open", file_path])
            return

        text_win = Toplevel(self.root)
        text_win.title(f"Чтение: {title}")
        text_win.geometry("800x600")
        text_win.configure(bg="#A0522D")
        text_widget = Text(text_win, wrap=WORD, bg="#D2B48C", fg="black")
        scrollbar = Scrollbar(text_win, command=text_widget.yview, bg="#D2691E")
        text_widget.configure(yscrollcommand=scrollbar.set)
        text_widget.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            text_widget.insert(END, content)
            text_widget.configure(state=DISABLED)
        except Exception as e:
            text_widget.insert(END, f"Не удалось прочитать файл: {e}")

    def open_book_file(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        item = self.tree.item(selected[0])
        book_id = item['values'][0]
        for book in self.books:
            if book.get("id") == book_id:
                self.open_book_as_text(book.get("file_path"), book.get("title", "Книга"))
                break

    def add_book_window(self):
        win = Toplevel(self.root)
        win.title("Добавить книгу")
        win.geometry("400x420")
        win.configure(bg="#A0522D")

        Label(win, text="Название:", bg="#A0522D", fg="white", font=("Arial", 10)).pack(pady=2)
        title_entry = Entry(win, width=50, bg="#D2B48C")
        title_entry.pack()

        Label(win, text="Автор:", bg="#A0522D", fg="white", font=("Arial", 10)).pack(pady=2)
        author_entry = Entry(win, width=50, bg="#D2B48C")
        author_entry.pack()

        Label(win, text="Год:", bg="#A0522D", fg="white", font=("Arial", 10)).pack(pady=2)
        year_entry = Entry(win, width=10, bg="#D2B48C")
        year_entry.pack()

        Label(win, text="Жанр:", bg="#A0522D", fg="white", font=("Arial", 10)).pack(pady=2)
        genre_entry = Entry(win, width=30, bg="#D2B48C")
        genre_entry.pack()

        file_path_var = StringVar()
        Button(win, text="Выбрать файл книги", command=lambda: file_path_var.set(filedialog.askopenfilename(
            filetypes=[("PDF", "*.pdf"), ("DOC", "*.docx"), ("TXT", "*.txt"), ("Все файлы", "*.*")]
        )), bg="#D2691E", fg="white").pack(pady=5)
        Label(win, textvariable=file_path_var, wraplength=350, fg="yellow", bg="#A0522D").pack()

        cover_path_var = StringVar()
        Button(win, text="Выбрать обложку (опционально)", command=lambda: cover_path_var.set(filedialog.askopenfilename(
            filetypes=[("Изображения", "*.png *.jpg *.jpeg *.gif")]
        )), bg="#D2691E", fg="white").pack(pady=5)
        Label(win, textvariable=cover_path_var, wraplength=350, fg="yellow", bg="#A0522D").pack()

        def save_new_book():
            title = title_entry.get().strip()
            author = author_entry.get().strip()
            year = year_entry.get().strip()
            genre = genre_entry.get().strip()
            file_path = file_path_var.get()
            cover_path = cover_path_var.get()

            if not title or not author or not file_path:
                messagebox.showerror("Ошибка", "Название, автор и файл книги обязательны!")
                return

            new_id = max([b.get("id", 0) for b in self.books], default=0) + 1
            new_book = {
                "id": new_id,
                "title": title,
                "author": author,
                "year": int(year) if year.isdigit() else None,
                "genre": genre,
                "file_path": file_path,
                "cover_path": cover_path if cover_path else None
            }
            self.books.append(new_book)
            self.save_data()
            self.refresh_table()
            win.destroy()
            messagebox.showinfo("Успех", f"Книга '{title}' добавлена!")

        Button(win, text="Сохранить", command=save_new_book, bg="#D2691E", fg="white", font=("Arial", 10, "bold")).pack(pady=10)

    def delete_book(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите книгу для удаления")
            return
        item = self.tree.item(selected[0])
        book_id = item['values'][0]
        for book in self.books:
            if book.get("id") == book_id:
                confirm = messagebox.askyesno("Удаление", f"Удалить книгу '{book['title']}'?")
                if confirm:
                    self.books.remove(book)
                    self.save_data()
                    self.refresh_table()
                    self.info_text.configure(state=NORMAL)
                    self.info_text.delete(1.0, END)
                    self.info_text.configure(state=DISABLED)
                    self.cover_label.config(image='', text="Нет обложки")
                break

if __name__ == "__main__":
    root = Tk()
    app = LibraryApp(root)
    root.mainloop()