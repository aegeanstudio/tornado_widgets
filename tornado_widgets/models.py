# -*- coding: UTF-8 -*-


class BaseModel(object):

    def __init__(self, id_, is_deleted, create_time, update_time):
        self.id_ = id_
        self._is_deleted = is_deleted
        self.create_time = create_time
        self.update_time = update_time

    @property
    def is_deleted(self):
        return bool(self._is_deleted)

    def __repr__(self):
        return '<{class_name}({props})>'.format(
            class_name=self.__class__.__name__,
            props=','.join(
                ['{}={}'.format(k, v) for k, v in self.__dict__.items()]))
