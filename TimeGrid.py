import logging
from math import ceil

from ef.config.components import time_grid
from ef.util.serializable_h5 import SerializableH5


class TimeGrid(SerializableH5):
    def __init__(self, total_time, time_step_size, time_save_step, current_time=0.0, current_node=0):
        if total_time <= 0:
            raise ValueError()
        if time_save_step < time_step_size:
            raise ValueError()
        if time_step_size <= 0:
            raise ValueError()
        if time_step_size > total_time:
            raise ValueError()
        self.total_time = float(total_time)
        self._total_nodes = ceil(self.total_time / time_step_size) + 1
        self.time_step_size = self.total_time / (self._total_nodes - 1)
        if self.time_step_size != time_step_size:
            logging.warning("Reducing time step to {:.3E} from {:.3E} "
                            "to fit a whole number of cells."
                            .format(self.time_step_size, time_step_size))
        self.time_save_step = int(time_save_step / self.time_step_size) * self.time_step_size
        if self.time_save_step != time_save_step:
            logging.warning("Reducing save time step to {:.3E} from {:.3E} "
                            "to fit a whole number of cells."
                            .format(self.time_save_step, time_save_step))
        self._node_to_save = int(self.time_save_step / self.time_step_size)
        self.current_time = current_time
        self.current_node = current_node

    def to_component(self):
        return time_grid.TimeGrid(self.total_time, self.time_save_step, self.time_step_size)

    @classmethod
    def init_from_config(cls, conf):
        time_config = time_grid.TimeGridConf.from_section(conf["TimeGrid"]).make()
        return cls(time_config.total, time_config.step, time_config.save_step)

    @classmethod
    def init_from_h5(cls, h5group):
        return cls.load_h5(h5group)

    def update_to_next_step(self):
        self.current_node += 1
        self.current_time += self.time_step_size

    def write_to_file(self, h5file):
        groupname = "/TimeGrid"
        h5group = h5file.create_group(groupname)
        self.save_h5(h5group)
