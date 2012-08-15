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

    def __init__(self):
        pass

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


class MutableTree(MutableObject_interface):
    """ Mutable class stared in DB
    """
    def __init__(self):
        MutableObject_interface.__init__(self)
        #self.data=None
        self.children=[]
        self.parent=None

    def addChild(self,child):
        self.children.append(child)
        child.addParent(self)
        self.changed()

    def addParent(self,parent):
        self.parent=parent

    def changed(self):
        if(hasattr(self,"parent") and self.parent!=None):
            self.parent.changed()
        MutableObject_interface.changed(self)


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
    testM=MutableTree()
    child=MutableTree()
    child.data="test message"
    testM.addChild(child)
    testObj.testObj=testM
    print db.session.dirty
    db.flushAndCommit()

    print("Change target.data")
    child.data="hello world"
    print db.session.dirty
    db.flushAndCommit()

    print("add child of child")
    childOFchild=MutableTree()
    child.addChild(childOFchild)
    print db.session.dirty
    db.flushAndCommit()
