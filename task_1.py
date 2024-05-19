from collections import UserDict
from datetime import datetime, timedelta
import pickle

def input_error(func):  # Декоратор для обробки помилок
    def inner(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except KeyError as error:
            return f"Contact with the name was not found: {error}"
        except ValueError as error:
            return f"You did not specify a name, phone number, or date of birth correctly: {error}"
        except IndexError as error:
            return f"Please enter the name and phone number: {error}"
        except Exception as error:  
            return f"An unexpected error occurred: {error}"
    return inner


# Оголошуємо клас Field, який представляє поле запису в адресній книзі
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

# Оголошуємо клас Name, який успадковує клас Field
class Name(Field):
    def __init__(self, value):
        # Ім'я є обов'язковим полем, тому перевіряємо, чи воно не порожнє
        if not value:
            raise ValueError("The name cannot be empty")
        super().__init__(value)


# Оголошуємо клас Phone, який успадковує клас Field
class Phone(Field):
    # Конструктор класу Phone
    def __init__(self, value):
        # Перевіряємо правильність формату номера телефону (10 цифр)
        if len(value) != 10 or not value.isdigit():
            # Викидаємо ValueError, якщо формат номера телефону невірний
            raise ValueError("The phone number format is incorrect")
        # Викликаємо конструктор класу Field з правильним значенням номера телефону
        super().__init__(value)

#клас для переведення дати в об'єкт datetime 
class Birthday(Field):
    def __init__(self, value):
        try:
            today = datetime.now().date() #теперішня дата 
            value = datetime.strptime(value, '%d.%m.%Y').date() #перевоодимо дату в об'єкт datetime
            value = datetime(today.year, value.month, value.day).date() #готуємо дату для подальшого порівння, додавши теперішній рік
            super().__init__(value)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        
# Оголошуємо клас Record, який представляє запис в адресній книзі
class Record:
    # Конструктор класу Record
    def __init__(self, name):
        # Встановлюємо значення поля name
        self.name = Name(name)
        # Встановлюємо порожній список для зберігання номерів телефону
        self.phones = []
        self.birthday = None
        
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    # Метод для додавання номера телефону в запис
    def add_phone(self, phone):
        # Спробуємо додати номер телефону в список
        try:
            # Викликаємо конструктор класу Phone з правильним значенням номера телефону
            self.phones.append(Phone(phone))
        # Якщо формат номера телефону невірний, то спрацює виняток ValueError
        except ValueError as e:
            # Виводимо повідомлення про помилку
            print(e)

    # Метод для видалення номера телефону з запису
    def remove_phone(self, phone):
        if phone not in self.phones:
            raise ValueError("This phone number does not exist")
        # Фільтруємо список номерів телефону, залишаючи тільки ті, які не дорівнюють шуканому номеру
        self.phones = [p for p in self.phones if str(p) != phone]

    # Метод для редагування номера телефону в записі
    def edit_phone(self, old_phone, new_phone):
        try:
            phone_str_list = [str(phone)for phone in self.phones]
            if old_phone in phone_str_list:
                # Знаходимо індекс старого номера телефону в списку номерів телефону
                index = phone_str_list.index(old_phone)
                # Замінюємо старий номер телефону на новий
                self.phones[index] = Phone(new_phone)
            else:
                print("No such phone number found")
        except ValueError as e:
            print(f"Error: {e}")

    # Метод для пошуку номера телефону в записі
    def find_phone(self, phone):
        # Знаходимо індекс номера телефону в списку номерів телефону
        try:
            index = self.phones.index(Phone(phone))
            # Повертаємо рядок, який містить знайдений номер телефону
            return str(self.phones[index])
        # Якщо такого номера телефону немає в списку, то спрацює виняток ValueError
        except ValueError:
            # Повертаємо рядок, який містить повідомлення про те, що такого номера телефону не знайдено
            return "No such phone number found"

    # Метод для отримання рядкового представлення запису
    def __str__(self):
        # Повертаємо рядок, який містить ім's користувача та його номери телефону
        return f"Контакт: {self.name}, Телефони: {', '.join(str(p) for p in self.phones)}, День народження: {self.birthday}"

# Оголошуємо клас AddressBook, який успадковує клас UserDict
class AddressBook(UserDict):
    # Метод для додавання запису в адресну книгу
    def add_record(self, record):
        # Додаємо запис в словник адресної книги
        self.data[record.name.value] = record

    # Метод для пошуку запису в адресній книзі
    def find(self, name):
        # Спробуємо знайти запис в словнику адресної книги
        try:
            # Повертаємо знайдений запис
            return self.data[name]
        # Якщо запис не знайдено, то спрацює виняток KeyError
        except KeyError:
            # Виводимо повідомлення про помилку
            print("Contact not found")

    # Метод для видалення запису з адресної книги
    def delete(self, name):
        # Спробуємо видалити запис з словника адресної книги
        try:
            # Видаляємо запис з словника адресної книги
            del self.data[name]
        # Якщо запис не знайдено, то спрацює виняток KeyError
        except KeyError:
            # Виводимо повідомлення про помилку
            print("Contact not found")

    # метод для виведення днів народження які випадають на 7 днів вперед  
    def get_users_to_greet(self):
        today = datetime.today().date() 
        users_to_greet = []
        for _, record in self.data.items():
            try:
                if record.birthday.value - today >= timedelta(days=0) and record.birthday.value - today <= timedelta(days=7):
                    users_to_greet.append(record)
            except AttributeError: # обробка вийнятків, для тих контактів, в яких не вказане день народження 
                pass
        if not users_to_greet:  # Якщо список порожній, виводимо відповідне повідомлення
            print("No upcoming birthdays found.")
        return users_to_greet
        
    def __str__(self):
        re = [record for _, record in self.data.items()]
        return "\n".join(str(r) for r in re)
    
@input_error
def parse_input(user_input): # Функція для підготовки введеного користувачем тексту. Розділяє команду та аргументи 
   cmd, *args = user_input.split()
   cmd = cmd.strip().lower()
   return cmd, *args

# Функція для додавання контактів в словник 

def add_contact(args, book):
    try:
        name, phone = args
        if len(phone) != 10 or not phone.isdigit():
            raise ValueError("the phone number must consist of 10 digits")
        
        if name in book:  # Перевірка, чи контакт вже існує в адресній книзі
            # Якщо так, додати новий номер телефону до існуючого запису
            book[name].add_phone(phone)
            return "Phone added to existing contact"
        else:
            # Якщо контакт не існує, створити новий запис
            record = Record(name)
            record.add_phone(phone)
            book.add_record(record)
            return "New contact added"
    except Exception as e:
        return e
        
@input_error
def change_contact(args, book): # Функція для зміни номеру в існуючому контакті 
        name, old_phone, new_phone = args
        try:
            if name not in book or len(new_phone) !=10:
                raise ValueError(f"Incorrect phone number: {new_phone}")
            else:
                record = book[name]
                record.edit_phone(old_phone, new_phone)
                return "Contact updated." 
        except Exception as e:
            return e

@input_error
def show_phone(args, book): # Функція для виведення номеру по імені контакта 
    *_, name = args
    value = book[name]
    return value

@input_error
def add_birthday(args, book): # Функція для додавання дня народження до контакту 
    name, birthday = args
    if name in book:
        record = book[name]
        record.add_birthday(birthday)
        return "Birthday added"
    else:
        return "Contact not found"
    
@input_error
def show_birthday(args, book):# Функція для вивдення дня народження контакту 
    *_, name = args
    if name in book:
        record = book[name]
        if record.birthday:
            return record.birthday.value
        else:
            return "Birthday not found for this contact"
    else:
        return "Contact not found"
    
@input_error
def remove(args, book): # Функція для видалення контакту з адресної книги 
    *_ ,name = args
    if name in book:
        book.delete(name)
        return "The contact has been deleted"
    else:
        return "Contact not found"
    
def load_data(filename="addressbook.pkl"): # Функція для десеріалізації книги контактів при запуску
    try:
        with open(filename, "rb") as file:
            return pickle.load(file)
    except FileNotFoundError:
        return AddressBook()
    except EOFError: # Додаємо обробку EOFError, якщо файл існує, але порожній
        return AddressBook()
    
def save_data(book, filename="addressbook.pkl"): # Функція для серіалізації книги контактів при закриті програми
    with open(filename, "wb") as file:
        pickle.dump(book, file)

@input_error
def main(): # Основна функція для обробки запитів користувача. В ній використовуються інші функції
    
    book = load_data()
    print("Welcome to asistant bot")

    while True: #вічний цикл 
        user_input = input("Enter a command: ")
        
        command, *args = parse_input(user_input)
        
        if command in ["close", "exit"]: #команда для завершення роботи бота 
            print("Good bye")
            save_data(book)
            break

        elif command == "hello": 
            print("How can I help you?")

        elif command == "add": #команда для додавання контакту 
            print(add_contact(args, book))      

        elif command == "phone": # команда для виведення номеру телефону по імені
            print(show_phone(args, book))

        elif command == "change": #команда для змінни номера телефону по імені 
            print(change_contact(args, book))

        elif command == "all": #команда для виведення всіх контактів
            if book:
                print(book)
            else:
                print("Address book is empty")
    
        elif command == "add-birthday":
                print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            for el in book.get_users_to_greet():
                print(f"{el.name} {el.birthday}")
        
        elif command == "del":
            print(remove(args, book))

        else:
            print("invalid command")
       
        
if __name__ == "__main__":
    main()
         
    


