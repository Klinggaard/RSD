import json
import time
import logging

logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.INFO)

class OEE:
    COMPLETED = 1
    REJECTED = 2

    __instance = None  # INITIAL INSTANCE OF CLASS

    @staticmethod
    def getInstance(ict=1, pot=24*60, pst=60, start=False, task=None):
        if OEE.__instance == None:
            OEE(ict=ict, pot=pot, pst=pst, start=start, task=task)
        """ Static access method. """
        return OEE.__instance

    def __init__(self, ict=1, pot=24*60, pst=60, start=False, task=None):
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
        self._ot = 0.0       # Operating Time
        self._sl = 0.0       # Speed Loss
        self._dtl = 0.0      # Down Time Loss
        self._neot = 0.0     # Net Operating Time
        self._ql = 0.0       # Quality Loss
        self._fpt = 0.0      # Fully Productive Time
        self._timestamps = []

        self.t_order = 0    # Total Pieces
        self.g_order = 0    # Good Orders
        self._started = False

        self.availability = 0
        self.performance = 0
        self.quality = 0
        self.oee = 0

        if start:
            self.start(self._task)

        """ Virtually private constructor. """
        if OEE.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            OEE.__instance = self

    def _availability(self):
        assert self._started is True, "OEE module not started"
        self.availability = self._ot / self._ppt
        return self.availability

    def _performance(self):
        assert self._started is True, "OEE module not started"
        self.performance = (self._ict * self.t_order) / self._ot
        # log.info("%f %f %f",self.ict,self.t_order,self.ot)
        return self.performance

    def _quality(self):
        assert self._started is True, "OEE module not started"
        self.quality = self.g_order/self.t_order
        return self.quality

    def _oee(self):
        assert self._started is True, "OEE module not started"
        self.oee = (self.g_order * self._ict) / self._ppt
        return self.oee

    def _update(self, sys_up, t):
        assert self._started is True, "OEE module not started"
        self._timestamps.append(t)
        if not sys_up:
            self._dtl += self._timestamps[-1] - self._timestamps[-2]
            log.debug("timeStamp %f", self._timestamps[-1] - self._timestamps[-2])
        # else:
        #     self.dtl = 0.0
        self._ot = self._ppt - self._dtl
        #print(self.ot, self.ppt, self.dtl)
        self._neot = self._ot - self._sl
        self._fpt = self._neot - self._ql
        pass

    def update(self, sys_up, task=None, update_order=False, order_status=None):
        self._update(sys_up=sys_up, t=time.time()/60)

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


        ret = json.dumps({
            'Availability': round(self._availability(), 3),
            'Performance':  round(self._performance(), 3),
            'Quality':      round(self._quality(), 3),
            'OEE':          round(self._oee(), 3),
            'Task':         self._task
        })

        # resetting shift
        if (self._timestamps[-1] - self._timestamps[0])/60 >= self._pot:
            self.reset_shift()
            log.info("[OEE] Resetting shift")

        return ret

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

    def get_oee(self):
        return json.dumps({
            'Availability': round(self._availability(), 3),
            'Performance':  round(self._performance(), 3),
            'Quality':      round(self._quality(), 3),
            'OEE':          round(self._oee(), 3),
            'Task':         self._task
        })

    def get_metrics(self):
        return json.dumps({
            'Total Orders': self._availability(),
            'Good Orders':  self._performance(),
            'Bad Orders': self._quality(),
        })

    def reset_shift(self):

        self._ppt = self._pot - self._pst  # Planned Production Time
        self._ot = 0.0       # Operating Time
        self._sl = 0.0       # Speed Loss
        self._dtl = 0.0      # Down Time Loss
        self._neot = 0.0     # Net Operating Time
        self._ql = 0.0       # Quality Loss
        self._fpt = 0.0      # Fully Productive Time
        self._timestamps = []

        self.t_order = 0    # Total Pieces
        self.g_order = 0    # Good Orders
        self._started = False

        self.availability = 0
        self.performance = 0
        self.quality = 0
        self.oee = 0

        self.start(self._task)


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
        print(oee.update(sys_up=True,update_order=True, order_status=OEE.REJECTED))
    elif c % 7 == 0:
        print("\naccept")
        print(oee.update(sys_up=True, update_order=True, order_status=OEE.COMPLETED))

'''