# encoding=utf-8
#-------------------------------------------------------------------------------
# Name:        db_mapper_test
# Purpose:     To understand the function of sqlalchemy.
#              About sqlalchemy, see http://www.sqlalchemy.org/
# Author:      ccat
#
# Created:     12/Aug/2012
#-------------------------------------------------------------------------------


from sqlalchemy import  create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class sqlConnector:
    """ Connecting SQL server and creating a session instance.
    """
    def __init__ (self):
        self.schemeName="mysql"
        self.engine=None
        self.session=None
        self.sessionMaker=None

    def __del__(self):
        self.close()

    def close(self):
        if(self.session):
            self.session.close()
            self.session=None

    def connect(self,user,password,host,port,dbname):

        #self.engine = create_engine(self.schemeName+'://'+user+':'
        #    +password+'@'+host+':'+str(port)+'/'+dbname
        #    +'?charset=utf8&use_unicode=0')
        self.engine = create_engine('sqlite:///:memory:', echo=False)

        Base.metadata.create_all(self.engine)
        self.sessionMaker=sessionmaker(bind=self.engine)
        self.session=self.sessionMaker()

    def insert(self,obj):
        self.session.add(obj)
        #self.flushAndCommit()

    def flushAndCommit(self):
        self.session.flush()
        self.session.commit()

def connect():
    #import config
    db=sqlConnector()
    #db.connect(config.databaseUser,config.databasePass,config.databaseIP,config.databasePort,config.databaseName)
    db.connect(None,None,None,None,None)
    return db

