# encoding=utf-8
#-------------------------------------------------------------------------------
# Name:        db_mapper_test
# Purpose:     To understand the function of sqlalchemy.
#              About sqlalchemy, see http://www.sqlalchemy.org/
# Author:      ccat
#
# Created:     12/Aug/2012
#-------------------------------------------------------------------------------

from sqlalchemy import Table, Column, types, Sequence, String, MetaData, ForeignKey
from sqlalchemy.orm import mapper, clear_mappers, relationship, backref

from sqlalchemy.ext.mutable import Mutable

from library import Base, connect

class MutableObject_interface(Mutable,object):
    """ Mutable base class """
    @classmethod
    def coerce(cls, key,value):
        return value

    def __getstate__(self): # To store data by using Pickle, this "d.pop" is needed.  In the case of JSON, you don't need this.
        #See http://docs.sqlalchemy.org/en/rel_0_7/orm/extensions/mutable.html#supporting-pickling
        d = self.__dict__.copy()
        d.pop('_parents', None)
        return d

    def __setstate__(self, state):
        self.__dict__=state

    def __setattr__(self,name,value):
        object.__setattr__(self, name, value)
        self.changed() # To notice value change to SQLAlchemy


class TestMutable(MutableObject_interface):
    """ Mutable class stared in DB
    """
    def __init__(self):
        MutableObject_interface.__init__(self)
        #self.data=None
        self.data=None
        self.listData=[]
        self.dicData={}

class ObjectListItem(Base):
    __tablename__ = 'ObjectList'
    name = Column(types.Unicode(255), nullable=False, primary_key=True)
    testObj=Column(MutableObject_interface.as_mutable(types.PickleType), nullable=True)

    def __init__(self,name):
        self.name=name
        self.testObj=None

if __name__ == '__main__':
    db=connect()

    #Inserting ObjectListItem to DB with no testObj
    print("insert testObj")
    testObj=ObjectListItem(u"testObj")
    db.insert(testObj)
    print db.session.dirty
    db.flushAndCommit()

    #Adding TestMutable instance to ObjectListItem instance.
    print("create testM")
    testM=TestMutable()
    testM.data=["hello world"]
    testObj.testObj=testM
    testM.changed()
    print db.session.dirty
    db.flushAndCommit()

    #Changing data of TestMutable instance, but SQLAlchemy cannot understand it.
    print("Change testM.data")
    testM.data.append("test message")
    print("Before calling changed()")
    print db.session.dirty
    testM.changed()
    print("After calling changed()")
    print db.session.dirty
    db.flushAndCommit()

