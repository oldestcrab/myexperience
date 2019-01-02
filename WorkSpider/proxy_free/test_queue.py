from queue import Queue

class test():
    def __init__(self, q):
        self.queue_test = q
    def test(self):

        try:
            while 1:
                b = self.queue_test.get(False)
                print(b)
        except:
            pass
        
        self.queue_test.put(3)
            

if __name__ == "__main__":
    a = Queue()
    for i in range(10):
        a.put(i)
    # b = test(a)
    # b.test()
    # print(a.get())
    while not a.empty():
        pass
    print(a.get())