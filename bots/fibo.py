import time


def fibo_1(n: int):
    if n == 0 or n == 1:
        return 1
    return fibo_1(n - 1) + fibo_1(n - 2)


def fibo_2(n: int):
    time.sleep(1)
    data = [0, 1]
    i = 2
    while i <= n:
        data.append(data[i - 1] + data[i - 2])
        i += 1
    return data[n]


if __name__ == '__main__':
    st = time.time_ns()
    # time.sleep(1)
    f = fibo_2(8)
    print(f)
    et = time.time_ns()
    runtime = et - st
    print(runtime)
    # num = 15
    # st1 = time.time_ns()
    # fibo_1(num)
    # et1 = time.time_ns()
    # runtime = et1 - st1
    # print(st1)
    # print(et1)
    # print(f'Second: {runtime}')
    # print('*' * 20)
    # st2 = time.time_ns()
    # print(f'Second: {fibo_2(num)}')
    # et2 = time.time_ns()
    # runtime = et2 - st2
    # print(f'Second: {runtime}')


