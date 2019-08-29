import sys
import pandas as pd
import pymysql
from sqlalchemy.exc import IntegrityError
from sqlalchemy import create_engine
from util import const, logger

logger = logger.init_logger(__file__)

class MysqlController:

    def __init__(self):
        # MySQL Connection 연결
        self.conn = pymysql.connect(host=const.MYSQL_SVR,
                                    user=const.MYSQL_USER,
                                    password=const.MYSQL_PASSWD,
                                    db=const.MYSQL_DB,
                                    charset='utf8')
        self.curs = self.conn.cursor(pymysql.cursors.DictCursor)
        self.engine = create_engine(
                        '''mysql+pymysql://{user}:{passwd}@{svr}/{db_name}?charset=utf8'''.format(
                            user=const.MYSQL_USER,
                            passwd=const.MYSQL_PASSWD,
                            svr=const.MYSQL_SVR,
                            db_name=const.MYSQL_DB),
                        encoding='utf8')
    def __del__(self):
        if self.conn is not None:
            self.conn.close()
        if self.curs is not None:
            self.curs.close()

    def select(self, query):
        # ==== select example ====
        self.curs.execute(query)

        # 데이타 Fetch
        rows = self.curs.fetchall()
        return rows

    def insert(self, query):
        # ==== insert example ====
        # sql = """insert into customer(name,category,region)
        #         values (%s, %s, %s)"""
        # self.curs.execute(sql, ('이연수', 2, '서울'))
        self.curs.execute(query)
        self.conn.commit()

    def update(self, query):
        self.curs.execute(query)
        self.conn.commit()

    def delete(self, query):
        self.update(query)

    def select_dataframe(self, query):
        df = pd.read_sql(query, self.engine)
        logger.info(f'Select Datarame : {query}')
        return df

    def insert_dataframe(self, df, table, index=False):
        err_cnt = False
        try:
            df.to_sql(name=table, con=self.engine, index=index, if_exists='append')
            logger.info(f'Insert Datarame into {table} : {len(df)}')
        except IntegrityError as e:
            for i in range(len(df)):
                row = df.iloc[[i]]
                try:
                    row.to_sql(name=table, con=self.engine, index=index, if_exists='append')
                except IntegrityError as e:
                    logger.debug(f'Duplicated Row ({table}) : {e.args[0]}')
        except Exception as e:
            logger.error(f'Insert Datarame Error ({table}) : {e}')

