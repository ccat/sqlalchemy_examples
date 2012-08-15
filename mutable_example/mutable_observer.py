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


class ObservedTarget(MutableObject_interface):
    """ Observer target
    """
    def __init__(self):
        MutableObject_interface.__init__(self)
        self.ovserver=None
        self.data=None

    def addOvserver(self,ovserver):
        self.ovserver=ovserver

    def changed(self):
        if(hasattr(self,"ovserver") and self.ovserver!=None):
            self.ovserver.changed()
        MutableObject_interface.changed(self)

class MutableObserver(MutableObject_interface):
    """ Mutable class stared in DB
    """
    def __init__(self):
        MutableObject_interface.__init__(self)
        #self.data=None
        self.data=None
        self.targetList=[]
        self.dicData={}

    def addOvservedTarget(self,target):
        self.targetList.append(target)
        target.addOvserver(self)
        self.changed()

class ObjectListItem(Base):
    __tablename__ = 'ObjectList'
    name = Column(types.Unicode(255), nullable=False, primary_key=True)
    testObj=Column(MutableObject_interface.as_mutable(types.PickleType), nullable=True)

    def __init__(self,name):
        self.name=name
        self.testObj=None

if __name__ == '__main__':
    db=connect()

    print("insert testObj")
    testObj=ObjectListItem(u"testObj")
    db.insert(testObj)
    print db.session.dirty
    db.flushAndCommit()

    print("create MutableObserver")
    testM=MutableObserver()
    target=ObservedTarget()
    target.data="test message"
    testM.addOvservedTarget(target)
    testObj.testObj=testM
    print db.session.dirty
    db.flushAndCommit()

    print("Change target.data")
    target.data="hello world"
    print db.session.dirty
    db.flushAndCommit()

