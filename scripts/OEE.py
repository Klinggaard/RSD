import time
import logging
import csv

logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.INFO)


class OEE:
    COMPLETED = 1
    REJECTED = 2

    __instance = None  # INITIAL INSTANCE OF CLASS

    @staticmethod
    def getInstance(ict=2.0, pot=24 * 60, pst=60, start=False, task=None):
        if OEE.__instance == None:
            OEE(ict=ict, pot=pot, pst=pst, start=start, task=task)
        """ Static access method. """
        return OEE.__instance

    def __init__(self, ict=2.0, pot=24 * 60, pst=60, start=False, task=None):
        '''
        :param ict: Ideal Cycle Time (m)
        :param pot: Plant Operating Time (m)
        :param pst: Planned Shut Down (m)
        :param task: A string for the task being performed at this moment
        '''
        assert type(start) is bool, "start parameter is not boolean"
        self._ict = float(ict)
        self._pot = float(pot)
        self._pst = float(pst)
        self._task = task

        self._ppt = self._pot - self._pst  # Planned Production Time
        self._ot = 0.0  # Operating Time
        self._sl = 0.0  # Speed Loss
        self._dtl = 0.0  # Down Time Loss
        self._neot = 0.0  # Net Operating Time
        self._ql = 0.0  # Quality Loss
        self._fpt = 0.0  # Fully Productive Time
        self._timestamps = []

        self.t_order = 0  # Total Pieces
        self.g_order = 0  # Good Orders
        self._started = False

        self.availability = 0
        self.performance = 0
        self.quality = 0
        self.oee = 0

        self.last_save = time.time()
        self.save_interval = 300  # 5 minutes
        self.t_suspended = 0

        self.file = "OEE_LOG/OEE_LOG-" + time.strftime("%Y%m%d-%H%M%S") + ".csv"
        with open(self.file, mode='w') as my_file:
            file_writer = csv.writer(my_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            file_writer.writerow(
                ['total_orders', 'good_orders', 'bad_orders', 'total_time', 'uptime', 'downtime', 'suspended'])

        if start:
            self.start(self._task)

        """ Virtually private constructor. """
        if OEE.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            OEE.__instance = self

    def _availability(self):
        assert self._started is True, "OEE module not started"
        self.availability = self._ot / (self._ot + self._dtl)
        return self.availability

    def _performance(self):
        assert self._started is True, "OEE module not started"
        if self._ot != 0:
            self.performance = (self._ict * self.t_order) / self._ot
        else:
            return 0
        # log.info("%f %f %f",self.ict,self.t_order,self.ot)
        return self.performance

    def _quality(self):
        assert self._started is True, "OEE module not started"
        if self.t_order != 0:
            self.quality = self.g_order / self.t_order
        else:
            return 0
        return self.quality

    def _oee(self):
        assert self._started is True, "OEE module not started"
        self.oee = self.get_availability() * self.get_performance() * self.get_quality()
        return self.oee

    def _update(self, sys_up, t, task):
        assert self._started is True, "OEE module not started"
        self._timestamps.append(t)

        if not sys_up:
            self._dtl += self._timestamps[-1] - self._timestamps[-2]
            if task == 'Suspended' or task == 'Suspending' or task == 'Unsuspending':
                self.t_suspended += self._timestamps[-1] - self._timestamps[-2]
        else:
            self._ot += self._timestamps[-1] - self._timestamps[-2]

        # else:
        #     self.dtl = 0.0
        # self._ot = self._ppt - self._dtl
        # print(self.ot, self.ppt, self.dtl)
        self._neot = self._ot - self._sl
        self._fpt = self._neot - self._ql

    def update(self, sys_up, task=None, update_order=False, order_status=None):
        self._update(sys_up=sys_up, t=time.time() / 60, task=task)

        if time.time() - self.last_save > self.save_interval:
            self.save_oee()

        if task is None:
            assert type(self._task) is str, "No task assigned - Task must be assigned by first update"
        if task:
            self._task = task

        if update_order:
            assert order_status, "No order_status given"
            assert order_status == self.REJECTED or order_status == self.COMPLETED, \
                "Unknown order_status - Use REJECTED or COMPLETED"
            if order_status == self.COMPLETED:
                self.t_order += 1
                self.g_order += 1
            elif order_status == self.REJECTED:
                self.t_order += 1

        ret = {
            'Availability': round(self._availability(), 3),
            'Performance': round(self._performance(), 3),
            'Quality': round(self._quality(), 3),
            'OEE': round(self._oee(), 3),
            'Total Orders': self._availability(),
            'Good Orders': self._performance(),
            'Bad Orders': self._quality()
        }

        # resetting shift
        if (self._timestamps[-1] - self._timestamps[0]) / 60 >= self._pot:
            self.reset_shift()
            log.info("[OEE] Resetting shift")
            return ret
        return None

    def start(self, task):
        assert task, "No task assigned - Task must be assigned when stating"
        assert type(task) is str, "Task must be a string"
        if not self._started:
            self._task = task
            self._started = True
            self._timestamps = [time.time() / 60]
        else:
            log.info("[OEE] Module already started - Task is not updated")

        return self._started

    def get_availability(self):
        return round(self._availability(), 3)

    def get_performance(self):
        return round(self._performance(), 3)

    def get_quality(self):
        return round(self._quality(), 3)

    def get_oee(self):
        return round(self._oee(), 3)

    def get_metrics(self):
        return {
            'Total Orders': self.t_order,
            'Good Orders': self.g_order,
            'Bad Orders': self.t_order - self.g_order
        }

    def get_time(self):
        return {
            "Up-time": self._ot,
            "Down-time": self._dtl,
            "Total time": self._ot + self._dtl
        }

    def reset_shift(self):

        self._ppt = self._pot - self._pst  # Planned Production Time
        self._ot = 0.0  # Operating Time
        self._sl = 0.0  # Speed Loss
        self._dtl = 0.0  # Down Time Loss
        self._neot = 0.0  # Net Operating Time
        self._ql = 0.0  # Quality Loss
        self._fpt = 0.0  # Fully Productive Time
        self._timestamps = []

        self.t_order = 0  # Total Pieces
        self.g_order = 0  # Good Orders
        self._started = False

        self.availability = 0
        self.performance = 0
        self.quality = 0
        self.oee = 0

        self.start(self._task)

    def save_oee(self):
        log.info("OEE: Saving log")
        with open(self.file, mode='a') as my_file:
            file_writer = csv.writer(my_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            metrics = self.get_metrics()
            my_time = self.get_time()
            file_writer.writerow(
                [metrics['Total Orders'], metrics['Good Orders'], metrics['Bad Orders'], my_time['Total time'],
                 my_time['Up-time'], my_time['Down-time'], self.t_suspended])
        self.last_save = time.time()


'''
oee = OEE(start=True, task="testing")
c = 0
n = ""
while True:
    c += 1
    #print(c%21)
    time.sleep(1)
    if c % 28 == 0:
        print("\nsys down")
        print(oee.update(sys_up=False))
        n = OEE.getInstance()
        print(n.get_oee())

    elif c % 21 == 0.0:
        print("\nreject")
        print(oee.update(sys_up=True, update_order=True, order_status=OEE.REJECTED))
    elif c % 7 == 0:
        print("\naccept")
        print(oee.update(sys_up=True, update_order=True, order_status=OEE.COMPLETED))
'''
