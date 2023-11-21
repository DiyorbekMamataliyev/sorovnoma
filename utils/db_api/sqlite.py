import datetime
import sqlite3


class Database:
    def __init__(self, path_to_db="main.db"):
        self.path_to_db = path_to_db

    @property
    def connection(self):
        return sqlite3.connect(self.path_to_db)

    def execute(self, sql: str, parameters: tuple = None, fetchone=False, fetchall=False, commit=False):
        if not parameters:
            parameters = ()
        connection = self.connection
        connection.set_trace_callback(logger)
        cursor = connection.cursor()
        data = None
        cursor.execute(sql, parameters)

        if commit:
            connection.commit()
        if fetchall:
            data = cursor.fetchall()
        if fetchone:
            data = cursor.fetchone()
        connection.close()
        return data

    def create_table_users(self):
        sql = """
            CREATE TABLE Users (
                id int NOT NULL,
                phone varchar(30) NULL,
                captchatext varchar(4) NULL,
                bloklaganmi varchar(1) NULL,
                deeplink varchar(160) NULL,
                PRIMARY KEY (id)
                );
    """
        self.execute(sql, commit=True)

    def create_table_reklama(self):
        sql = """
            CREATE TABLE Reklama (
                id int NOT NULL,
                text varchar(4000) NULL,
                korish int NULL,
                vaqt varchar(12) NULL,
                PRIMARY KEY (id)
                );
    """
        self.execute(sql, commit=True)

    def select_all_reklama(self):
        sql = """
        SELECT * FROM Reklama
        """
        return self.execute(sql, fetchall=True)

    def update_reklama_korish(self):
        # SQL_EXAMPLE = "UPDATE Users SET email=mail@gmail.com WHERE id=12345"

        sql = f"""
        UPDATE Reklama SET korish=korish+1;
        """
        self.execute(sql, commit=True)

    def add_reklama(self, id: int, text="0", korish=0, vaqt='0'):
        # SQL_EXAMPLE = "INSERT INTO Users(id, Name, email) VALUES(1, 'John', 'John@gmail.com')"

        sql = """
        INSERT INTO Reklama(id, text, korish, vaqt) VALUES(?, ?, ?, ?)
        """
        self.execute(sql, parameters=(id, text, korish, vaqt), commit=True)

    def delete_reklama(self):
        self.execute("DELETE FROM Reklama WHERE TRUE", commit=True)

    def create_table_sorovnoma(self):
        sql = """
            CREATE TABLE Sorovnoma (
                s_id int NOT NULL,
                s_name varchar(100) NULL,
                variant varchar(40) NULL,
                ovozlar int NULL,
                guruh varchar(20) NULL,
                message_id varchar(20) NULL,
                channel_id varchar(20) NULL
                );
    """
        self.execute(sql, commit=True)

    def select_all_sorovnoma(self):
        sql = """
        SELECT * FROM Sorovnoma ORDER BY ovozlar DESC
        """
        return self.execute(sql, fetchall=True)

    def add_sorovnoma(self, s_id: int, s_name="0", variant="0", ovozlar="0", guruh="0", message_id="0", channel_id="0"):
        # SQL_EXAMPLE = "INSERT INTO Users(id, Name, email) VALUES(1, 'John', 'John@gmail.com')"

        sql = """
        INSERT INTO Sorovnoma(s_id, s_name, variant, ovozlar, guruh, message_id, channel_id) VALUES(?, ?, ?, ?, ?, ?, ?)
        """
        self.execute(sql, parameters=(s_id, s_name, variant, ovozlar, guruh, message_id, channel_id), commit=True)

    def update_sorovnoma_ids(self, s_id, message_id, channel_id):
        # SQL_EXAMPLE = "UPDATE Users SET email=mail@gmail.com WHERE id=12345"

        sql = f"""
        UPDATE Sorovnoma SET message_id=?, channel_id=? WHERE s_id=?
        """
        return self.execute(sql, parameters=(message_id, channel_id, s_id), commit=True)

    def update_sorovnoma_ovozlar(self, s_name, guruh, variant):
        # SQL_EXAMPLE = "UPDATE Users SET email=mail@gmail.com WHERE id=12345"

        sql = f"""
        UPDATE Sorovnoma SET ovozlar=ovozlar+1 WHERE s_name=? AND guruh=? AND variant=?
        """
        return self.execute(sql, parameters=(s_name, guruh, variant), commit=True)

    def delete_sorovnoma(self, s_id):
        self.execute("DELETE FROM Sorovnoma WHERE s_id=?", parameters=(s_id,), commit=True)

    def create_table_ovoz(self):
        sql = """
            CREATE TABLE Ovoz (
                id int NOT NULL, 
                s_name varchar(100) NULL,
                guruh varchar(20) NULL,
                variant varchar(40) NULL
                );
    """
        self.execute(sql, commit=True)

    def select_all_ovoz(self):
        sql = """
        SELECT * FROM Ovoz
        """
        return self.execute(sql, fetchall=True)

    def add_ovoz(self, id: int, s_name="0", guruh="0", variant="0"):
        # SQL_EXAMPLE = "INSERT INTO Users(id, Name, email) VALUES(1, 'John', 'John@gmail.com')"

        sql = """
        INSERT INTO Ovoz(id, s_name, guruh, variant) VALUES(?, ?, ?, ?)
        """
        self.execute(sql, parameters=(id, s_name, guruh, variant), commit=True)

    def delete_ovoz_sorovnoma(self, s_id):
        self.execute("DELETE FROM Ovoz WHERE s_name=?", parameters=(s_id,), commit=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ?" for item in parameters
        ])
        return sql, tuple(parameters.values())

    def add_user(self, id: int, phone="0", captchatext="0", bloklanganmi="0", deeplink="0"):
        # SQL_EXAMPLE = "INSERT INTO Users(id, Name, email) VALUES(1, 'John', 'John@gmail.com')"

        sql = """
        INSERT INTO Users(id, phone, captchatext, bloklaganmi, deeplink) VALUES(?, ?, ?, ?, ?)
        """
        self.execute(sql, parameters=(id, phone, captchatext, bloklanganmi, deeplink), commit=True)

    def select_all_users(self):
        sql = """
        SELECT * FROM Users ORDER BY bloklaganmi
        """
        return self.execute(sql, fetchall=True)

    # def select_user(self, **kwargs):
    #     # SQL_EXAMPLE = "SELECT * FROM Users where id=1 AND Name='John'"
    #     sql = "SELECT * FROM Users WHERE "
    #     sql, parameters = self.format_args(sql, kwargs)
    #
    #     return self.execute(sql, parameters=parameters, fetchone=True)

    def select_user_by_id(self, star, user_id):
        sql = """
        SELECT ? FROM Users WHERE id=?
        """
        return self.execute(sql, parameters=(star, user_id), fetchall=True)

    def count_users(self):
        all = self.execute("SELECT COUNT(*) FROM Users;", fetchone=True)
        active = self.execute("SELECT COUNT(*) FROM Users WHERE captchatext!='dele' AND bloklaganmi=0;", fetchone=True)
        passive = self.execute("SELECT COUNT(*) FROM Users WHERE captchatext!='dele' AND bloklaganmi=1;", fetchone=True)
        dele = self.execute("SELECT COUNT(*) FROM Users WHERE captchatext='dele';")
        return all, active, passive, dele

    def update_user_phone(self, userid, new_phone):
        # SQL_EXAMPLE = "UPDATE Users SET email=mail@gmail.com WHERE id=12345"

        sql = f"""
        UPDATE Users SET phone=? WHERE id=?
        """
        return self.execute(sql, parameters=(new_phone, userid), commit=True)

    def update_user_deeplink(self, userid, deeplink):
        # SQL_EXAMPLE = "UPDATE Users SET email=mail@gmail.com WHERE id=12345"

        sql = f"""
        UPDATE Users SET deeplink=? WHERE id=?
        """
        return self.execute(sql, parameters=(deeplink, userid), commit=True)

    def update_user_captcha_text(self, userid, captcha_text):
        # SQL_EXAMPLE = "UPDATE Users SET email=mail@gmail.com WHERE id=12345"

        sql = f"""
        UPDATE Users SET captchatext=? WHERE id=?
        """
        return self.execute(sql, parameters=(captcha_text, userid), commit=True)

    def update_user_bloklaganmi(self, userid, blok):
        # SQL_EXAMPLE = "UPDATE Users SET email=mail@gmail.com WHERE id=12345"

        sql = f"""
        UPDATE Users SET bloklaganmi=? WHERE id=?
        """
        return self.execute(sql, parameters=(blok, userid), commit=True)

    def delete_users(self):
        self.execute("DELETE FROM Users WHERE TRUE", commit=True)

    def create_table_channels(self):
        sql = """
            CREATE TABLE Channels (
                id varchar(40) NULL
                );
    """
        self.execute(sql, commit=True)

    def select_all_channels(self):
        sql = """
        SELECT * FROM Channels ORDER BY id DESC
        """
        return self.execute(sql, fetchall=True)

    def add_channel(self, id: str):
        # SQL_EXAMPLE = "INSERT INTO Users(id, Name, email) VALUES(1, 'John', 'John@gmail.com')"

        sql = """
        INSERT INTO Channels(id) VALUES(?)
        """
        self.execute(sql, parameters=(id,), commit=True)

    def delete_channel(self, s_id):
        self.execute("DELETE FROM Channels WHERE id=?", parameters=(s_id,), commit=True)

    def create_table_captchas(self):
        sql = """
            CREATE TABLE Captchas (
                file_id varchar(128) NOT NULL,
                text varchar(4) NULL
                );
        """
        self.execute(sql, commit=True)

    def select_all_captchas(self):
        sql = """
        SELECT * FROM Captchas
        """
        return self.execute(sql, fetchall=True)

    def add_captchas(self, file_id: str, text="0"):
        # SQL_EXAMPLE = "INSERT INTO Users(id, Name, email) VALUES(1, 'John', 'John@gmail.com')"

        sql = """
        INSERT INTO Captchas(file_id, text) VALUES(?, ?)
        """
        self.execute(sql, parameters=(file_id, text), commit=True)


def logger(statement):
    print(f"""
_____________________________________________________        
Executing: 
{statement}
_____________________________________________________
""")
