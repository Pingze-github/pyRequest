import sqlite3

class ReqLogDB:
    def __init__(self):
        (self.conn, self.cursor) = self.createConn()

    def createConn(self):
        conn = sqlite3.connect('reqlog.db')
        print('sqlite 数据库连接成功')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS LOG
               (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
               METHOD TEXT NOT NULL,
               URL TEXT NOT NULL,
               QUERY TEXT NOT NULL,
               BODY TEXT NOT NULL);''')
        conn.commit()
        return (conn, cursor)

    def execute(self, sql):
        self.cursor.execute(sql)
        self.conn.commit()

    def insert(self, log):
        self.cursor.execute('INSERT INTO LOG (METHOD,URL,QUERY,BODY) VALUES (?,?,?,?)', (log['method'], log['url'], log['query'], log['body']))
        self.conn.commit()
        rows = self.cursor.execute('SELECT ID FROM LOG ORDER BY ID DESC LIMIT 1')
        return list(rows)[0][0]

    def selectAll(self):
        logs = []
        rows = self.cursor.execute('SELECT * FROM LOG ORDER BY ID DESC')
        for row in rows:
            logs.append({
                'id': row[0],
                'method': row[1],
                'url': row[2],
                'query': row[3],
                'body': row[4],
            })
        return logs


    def selectOne(self, id):
        rows = self.cursor.execute('SELECT * FROM LOG WHERE ID=' + str(id))
        row = list(rows)[0]
        log = {
            'id': row[0],
            'method': row[1],
            'url': row[2],
            'query': row[3],
            'body': row[4],
        }
        return log

