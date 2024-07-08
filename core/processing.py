from multiprocessing import Process


# ----------------------Base-Functional-Class----------------------
class ProcessThread:
    def __init__(self, func=None, *args, **kwargs):
        # print('creating thread')
        # print(f'func: {func}, args: {args}, kwargs: {kwargs}')
        self.active = False
        if func is not None:
            self.proc = func
            self.func = func
            self.args = args
            self.kwargs = kwargs
            self.create_process()
        else:
            self.proc = None
            self.func = None
            self.args = args
            self.kwargs = kwargs
        # print(f'func: {self.func}, args: {self.args}, kwargs: {self.kwargs}')

    def create_process(self, func=None, *args, **kwargs):
        if func is not None:
            if args or kwargs:
                self.proc = Process(target=func, args=args, kwargs=kwargs)
            else:
                self.proc = Process(target=func, args=self.args, kwargs=self.kwargs)
        else:
            if self.func is not None:
                if args or kwargs:
                    self.proc = Process(target=self.func, args=args, kwargs=kwargs)
                else:
                    self.proc = Process(target=self.func, args=self.args, kwargs=self.kwargs)
            else:
                print('error: Function not defined')

    def start(self):
        # print(f'{self.proc} with function {self.func} is starting...')
        self.active = True
        self.proc.start()
        # print(f'{self.proc} with function {self.func} is started')

    def terminate(self):
        # print(f'{self.proc} with function {self.func} is terminating...')
        self.active = False
        self.proc.terminate()
        # print(f'{self.proc} with function {self.func} is terminated')
        # print(f'{self.proc} with function {self.func} is joining...')
        self.proc.join()
        # print(f'{self.proc} with function {self.func} is joined')

    def update_func(self, func, *args, **kwargs):
        if args or kwargs:
            self.func = func
            self.args = args
            self.kwargs = kwargs
        else:
            self.func = func

    def update_args(self, func=None, *args, **kwargs):
        if func is not None:
            self.func = func
            self.args = args
            self.kwargs = kwargs
        else:
            self.args = args
            self.kwargs = kwargs

    class SubProcess:
        def __init__(self, func, *args, **kwargs):
            self.active = False
            self.proc = Process(target=func, args=args, kwargs=kwargs)

        def start(self):
            self.active = True
            self.proc.start()

        def terminate(self):
            self.active = False
            self.proc.terminate()
            self.proc.join()